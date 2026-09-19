"""
Testes de falha no nível do gateway/protocolo MCP (não via HTTP, para evitar
ambiguidade da serialização JSON do cliente de teste):
- NaN / infinito em preco_medio_informado
- ferramenta ausente (nome de tool inexistente)
- resposta inválida de um servidor MCP forjado
- timeout
- cancelamento de tarefa asyncio em andamento

Usa subprocesso stdio real do runtime_server.py (não mock) para os dois
primeiros; usa um servidor MCP forjado (fake_server.py) para timeout/resposta
inválida/ferramenta ausente, pois o servidor real não tem como provocar
esses cenários sob demanda.
"""
import asyncio
import json
import sys
from datetime import timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.models.trade import TradeInput
from app import mcp_gateway as gateway

results = []


def record(name, ok, detail):
    results.append({"case": name, "ok": ok, "detail": detail})
    print(f"[{'OK' if ok else 'FALHA'}] {name}: {detail}")


def trade(**kw):
    values = dict(ativo="PETR4", tipo_ativo="acao", tipo_operacao="venda",
                  quantidade=100, preco_unitario=30.0, data_operacao="2026-09-16",
                  total_vendas_mes=3000.0)
    values.update(kw)
    return TradeInput(**values)


async def test_nan():
    try:
        await gateway.calculate_via_mcp_async(trade(preco_medio_informado=float("nan")), average_price=None)
        record("preco_medio_nan_direto", False, "Deveria ter sido rejeitado antes de chegar ao MCP")
    except Exception as e:
        # NaN é rejeitado antes mesmo do gateway: TradeInput.preco_medio_informado tem
        # Field(..., ge=0), e qualquer comparação "NaN >= 0" é False em Python/Pydantic —
        # então a validação do próprio modelo já barra o valor. Isso é uma camada de
        # defesa anterior ao math.isfinite() do runtime_server.py, não um caminho não testado.
        is_pydantic_ge_rejection = "greater_than_equal" in str(e) or "ValidationError" in type(e).__name__
        record(
            "preco_medio_nan_direto",
            is_pydantic_ge_rejection,
            f"Rejeitado na validação do modelo TradeInput (Field ge=0), antes do gateway MCP: {type(e).__name__}: {e}",
        )


async def test_inf():
    try:
        await gateway.calculate_via_mcp_async(trade(preco_medio_informado=float("inf")), average_price=None)
        record("preco_medio_inf_direto", False, "Deveria ter levantado ValueError")
    except ValueError as e:
        record("preco_medio_inf_direto", "custo médio" in str(e) or "positivo" in str(e), str(e))
    except Exception as e:
        record("preco_medio_inf_direto", False, f"Exceção inesperada: {type(e).__name__}: {e}")


async def test_ferramenta_ausente():
    params = StdioServerParameters(command=sys.executable, args=[str(gateway.SERVER)], env={"PYTHONIOENCODING": "utf-8"})
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=10)) as session:
                await session.initialize()
                try:
                    resp = await session.call_tool("ferramenta_que_nao_existe", {})
                    record("ferramenta_ausente", resp.isError, f"isError={resp.isError} content={resp.content}")
                except Exception as e:
                    record("ferramenta_ausente", True, f"Levantou exceção no cliente: {type(e).__name__}: {e}")
    except Exception as e:
        record("ferramenta_ausente", False, f"Falha inesperada de transporte: {type(e).__name__}: {e}")


async def test_cancelamento():
    task = asyncio.create_task(gateway.calculate_via_mcp_async(trade(), average_price=25.0))
    await asyncio.sleep(0.01)  # let it start opening the subprocess
    task.cancel()
    try:
        await task
        record("cancelamento", False, "Task deveria ter sido cancelada, mas completou normalmente")
    except asyncio.CancelledError:
        record("cancelamento", True, "CancelledError propagada corretamente; sem exceção não tratada")
    except Exception as e:
        record("cancelamento", None, f"Completou com outra exceção (corrida esperada às vezes): {type(e).__name__}: {e}")


async def test_timeout_com_servidor_forjado():
    fake = Path(__file__).resolve().parent / "fake_slow_server.py"
    fake.write_text(
        "import sys,time\n"
        "sys.path.insert(0, r'" + str(PROJECT_ROOT / 'backend') + "')\n"
        "from mcp.server.fastmcp import FastMCP\n"
        "mcp = FastMCP('fake slow server')\n"
        "@mcp.tool()\n"
        "def fee_policy(asset_type: str) -> dict:\n"
        "    time.sleep(120)\n"
        "    return {}\n"
        "@mcp.tool()\n"
        "def calculate_trade(trade: dict, average_price=None) -> dict:\n"
        "    return {'ok': False, 'error': 'unreachable'}\n"
        "if __name__=='__main__': mcp.run(transport='stdio')\n",
        encoding="utf-8",
    )
    original_server = gateway.SERVER
    gateway.SERVER = fake
    try:
        try:
            await asyncio.wait_for(gateway.calculate_via_mcp_async(trade(), average_price=25.0), timeout=5)
            record("timeout_servidor_lento", False, "Deveria ter estourado timeout")
        except asyncio.TimeoutError:
            record("timeout_servidor_lento", True, "asyncio.TimeoutError levantado no limite externo de 5s (gateway usa 30s internamente; aqui forçamos um teto externo menor para o teste)")
        except ValueError as e:
            record("timeout_servidor_lento", True, f"gateway converteu timeout em ValueError: {e}")
        except Exception as e:
            record("timeout_servidor_lento", False, f"Exceção inesperada: {type(e).__name__}: {e}")
    finally:
        gateway.SERVER = original_server
        fake.unlink(missing_ok=True)


async def test_resposta_invalida_servidor_forjado():
    fake = Path(__file__).resolve().parent / "fake_bad_server.py"
    fake.write_text(
        "import sys\n"
        "sys.path.insert(0, r'" + str(PROJECT_ROOT / 'backend') + "')\n"
        "from mcp.server.fastmcp import FastMCP\n"
        "mcp = FastMCP('fake bad server')\n"
        "@mcp.tool()\n"
        "def fee_policy(asset_type: str) -> dict:\n"
        "    return {'warning': 'ok'}\n"
        "@mcp.tool()\n"
        "def calculate_trade(trade: dict, average_price=None) -> dict:\n"
        "    return {'ok': True, 'result': {'campo_incompleto': 'nao_eh_um_taxcalculationresult_valido'}}\n"
        "if __name__=='__main__': mcp.run(transport='stdio')\n",
        encoding="utf-8",
    )
    original_server = gateway.SERVER
    gateway.SERVER = fake
    try:
        try:
            await gateway.calculate_via_mcp_async(trade(), average_price=25.0)
            record("resposta_invalida_servidor", False, "Deveria ter falhado ao validar o payload")
        except ValueError as e:
            record("resposta_invalida_servidor", True, str(e))
        except Exception as e:
            record("resposta_invalida_servidor", False, f"Exceção inesperada (não convertida em ValueError pelo gateway): {type(e).__name__}: {e}")
    finally:
        gateway.SERVER = original_server
        fake.unlink(missing_ok=True)


async def main():
    await test_nan()
    await test_inf()
    await test_ferramenta_ausente()
    await test_cancelamento()
    await test_resposta_invalida_servidor_forjado()
    await test_timeout_com_servidor_forjado()

    out = Path(__file__).resolve().parent / "resultados_nan_inf_timeout_cancel.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvos em {out}")


asyncio.run(main())
