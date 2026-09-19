"""
Testes de concorrência e comportamento no event loop (Windows/uvicorn).

1. N chamadas concorrentes via calculate_via_mcp_async (caminho usado pela rota
   estruturada /api/trades/process, que é `async def` e usa `await` de verdade).
2. Reprodução do caminho usado pelo chat (base_agent.py chama o wrapper SÍNCRONO
   calculate_via_mcp() de dentro de uma função async, sem awaitar) — testado aqui
   isoladamente do orquestrador/LLM (sem custo de API), com um "heartbeat"
   concorrente no mesmo event loop para detectar bloqueio.
3. Confirma ausência de processos órfãos após rajada de chamadas.
"""
import asyncio
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

import psutil
from app.models.trade import TradeInput
from app import mcp_gateway as gateway

results = {}


def trade(i):
    preco = 30.0 + i
    return TradeInput(
        ativo="PETR4", tipo_ativo="acao", tipo_operacao="venda",
        quantidade=100, preco_unitario=preco, data_operacao="2026-09-16",
        total_vendas_mes=100 * preco,  # sempre >= valor_financeiro desta venda
    )


async def test_concurrent_async_calls(n=8):
    """Caminho real da rota estruturada: await calculate_via_mcp_async concorrente."""
    parent = psutil.Process()
    before = {c.pid for c in parent.children(recursive=True)}

    t0 = time.perf_counter()
    outcomes = await asyncio.gather(
        *[gateway.calculate_via_mcp_async(trade(i), average_price=25.0) for i in range(n)],
        return_exceptions=True,
    )
    elapsed = time.perf_counter() - t0

    ok = sum(1 for o in outcomes if not isinstance(o, Exception))
    correct_isolation = all(
        not isinstance(o, Exception) and o.preco_unitario == 30.0 + i
        for i, o in enumerate(outcomes)
    )
    errors = [f"{type(o).__name__}: {o}" for o in outcomes if isinstance(o, Exception)]
    results.setdefault("_debug", {})["async_concurrent_errors"] = errors
    for i, o in enumerate(outcomes):
        if isinstance(o, Exception):
            print(f"    [erro i={i}] {type(o).__name__}: {o}")

    await asyncio.sleep(0.5)
    after = {c.pid for c in parent.children(recursive=True)}
    orphans = (before | after) - before if (after - before) else set()
    # more precise orphan check: anything spawned during the burst that is still alive now
    still_running = {pid for pid in (after - before)}

    results["async_concurrent"] = {
        "n_requests": n,
        "n_ok": ok,
        "elapsed_seconds": round(elapsed, 3),
        "avg_seconds_per_call": round(elapsed / n, 3),
        "results_correctly_isolated_per_call": correct_isolation,
        "orphan_pids_after_burst": sorted(still_running),
    }
    print(f"[async_concurrent] n={n} ok={ok}/{n} elapsed={elapsed:.2f}s isolados={correct_isolation} orfaos={sorted(still_running)}")


async def test_sync_wrapper_blocks_event_loop():
    """
    Reproduz o padrão de app/agents/base_agent.py: dentro de uma função async
    (como a rota /api/chat/, que é `async def`), chama-se o wrapper SÍNCRONO
    calculate_via_mcp() sem await. Este teste mede se isso trava o event loop
    para outras tarefas concorrentes rodando no mesmo processo.
    """
    heartbeat_ticks = []
    stop = asyncio.Event()

    async def heartbeat():
        start = time.perf_counter()
        while not stop.is_set():
            heartbeat_ticks.append(time.perf_counter() - start)
            await asyncio.sleep(0.05)

    async def call_sync_wrapper_from_async_context():
        # Roda em thread separada porque calculate_via_mcp() é uma função
        # SÍNCRONA e bloqueante; chamá-la diretamente aqui (sem to_thread)
        # bloquearia literalmente esta coroutine de teste inteira, o que
        # impediria até o loop.call_soon de agendar o heartbeat. Para isolar
        # "o wrapper síncrono trava o event loop" do "eu mesmo bloqueei",
        # replicamos exatamente o que base_agent.py faz: chamar a função
        # síncrona a partir de uma thread cujo laço de eventos é o mesmo
        # processo — usamos run_in_executor com um único worker para
        # observar o efeito no loop principal enquanto ele aguarda.
        loop = asyncio.get_running_loop()
        t0 = time.perf_counter()
        # This mirrors calling gateway.calculate_via_mcp() synchronously:
        # base_agent.py's caller thread blocks on it. We call the *sync*
        # function itself (not the async one) to reproduce its internal
        # ThreadPoolExecutor + asyncio.run() nesting exactly.
        result = await loop.run_in_executor(None, gateway.calculate_via_mcp, trade(0), 25.0)
        return time.perf_counter() - t0, result

    hb_task = asyncio.create_task(heartbeat())
    call_task = asyncio.create_task(call_sync_wrapper_from_async_context())
    elapsed, result = await call_task
    stop.set()
    await hb_task

    gaps = [b - a for a, b in zip(heartbeat_ticks, heartbeat_ticks[1:])]
    max_gap = max(gaps) if gaps else 0.0

    results["sync_wrapper_via_executor"] = {
        "call_elapsed_seconds": round(elapsed, 3),
        "heartbeat_ticks": len(heartbeat_ticks),
        "max_heartbeat_gap_seconds": round(max_gap, 3),
        "note": (
            "Este teste roda o wrapper síncrono via run_in_executor (thread separada), "
            "o que É a forma correta de não travar o loop. NÃO reproduz o bug real: "
            "base_agent.py chama calculate_via_mcp() diretamente, sem run_in_executor, "
            "de dentro do corpo síncrono de Orchestrator.process() invocado por uma rota "
            "`async def` (app/api/chat.py) sem await — ver test_sync_wrapper_blocks_real_pattern."
        ),
    }
    print(f"[sync_wrapper_via_executor] elapsed={elapsed:.2f}s heartbeat_ticks={len(heartbeat_ticks)} max_gap={max_gap:.3f}s")


async def test_sync_wrapper_blocks_real_pattern():
    """
    Reproduz o padrão REAL: chama gateway.calculate_via_mcp() (síncrono) direto,
    dentro de uma coroutine, sem run_in_executor — exatamente como
    Orchestrator.process() faz quando chamado (sem await) de dentro de
    `async def send_message(...)` em app/api/chat.py.
    """
    heartbeat_ticks = []
    stop = asyncio.Event()

    async def heartbeat():
        start = time.perf_counter()
        while not stop.is_set():
            heartbeat_ticks.append(time.perf_counter() - start)
            await asyncio.sleep(0.05)

    hb_task = asyncio.create_task(heartbeat())
    await asyncio.sleep(0.15)  # let a few ticks accumulate first

    t0 = time.perf_counter()
    result = gateway.calculate_via_mcp(trade(0), average_price=25.0)  # SEM await, SEM executor — padrão real
    elapsed = time.perf_counter() - t0

    await asyncio.sleep(0.15)  # let a few more ticks accumulate after
    stop.set()
    await hb_task

    gaps = [b - a for a, b in zip(heartbeat_ticks, heartbeat_ticks[1:])]
    max_gap = max(gaps) if gaps else 0.0

    results["sync_wrapper_real_pattern"] = {
        "call_elapsed_seconds": round(elapsed, 3),
        "heartbeat_ticks_total": len(heartbeat_ticks),
        "max_heartbeat_gap_seconds": round(max_gap, 3),
        "event_loop_blocked": max_gap > elapsed * 0.5,
        "note": (
            "Padrão real de base_agent.py: calculate_via_mcp() síncrono chamado direto "
            "dentro de uma coroutine, sem run_in_executor. Se max_heartbeat_gap_seconds "
            "for próximo de call_elapsed_seconds, o event loop ficou bloqueado durante "
            "toda a chamada MCP — outras requisições no mesmo worker uvicorn ficariam "
            "paradas nesse intervalo."
        ),
    }
    print(f"[sync_wrapper_real_pattern] elapsed={elapsed:.2f}s heartbeat_ticks={len(heartbeat_ticks)} max_gap={max_gap:.3f}s bloqueado={max_gap > elapsed * 0.5}")


async def main():
    await test_concurrent_async_calls(n=8)
    await test_sync_wrapper_blocks_event_loop()
    await test_sync_wrapper_blocks_real_pattern()

    import json
    out = Path(__file__).resolve().parent / "resultados_concorrencia_eventloop.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvos em {out}")


asyncio.run(main())
