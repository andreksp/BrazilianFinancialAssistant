"""
Teste com MODELO REAL (chamadas pagas autorizadas pelo autor).

Instrumenta ClaudeClient.tool_turn para registrar, em cada rodada:
- blocos tool_use devolvidos pelo modelo (nome, id, input)
- stop_reason
- uso de tokens (entrada/saída/cache), para cálculo de custo real
- tool_result devolvido pelo host na rodada seguinte

Objetivo central: comprovar que a SELEÇÃO das ferramentas vem do modelo real,
não de roteiro simulado nem do gateway do formulário. Nenhuma chave é registrada.

Executa diretamente contra os agentes/orquestrador (mesmo caminho da rota de chat),
com banco SQLite e Chroma temporários.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT / "backend"))

TMP = Path(tempfile.mkdtemp(prefix="tooluse_real_"))
os.environ["DATABASE_URL"] = f"sqlite:///{TMP.as_posix()}/real.db"
os.environ["CHROMA_DB_PATH"] = f"{TMP.as_posix()}/chroma"

# Preços públicos (US$ por 1M tokens) — usados só para estimar o custo desta rodada.
PRECOS = {"sonnet": (2.00, 10.00), "haiku": (1.00, 5.00)}

from app.llm.claude_client import ClaudeClient, get_claude_client
from app.storage.database import create_tables, SessionLocal
from app.agents.orchestrator import get_orchestrator

registro = {"rodadas": [], "uso": [], "cenarios": []}


def instrumentar():
    original_tool_turn = ClaudeClient.tool_turn
    original_call = ClaudeClient._call_model

    def tool_turn(self, system_prompt, messages, tools):
        t0 = time.perf_counter()
        resposta = original_tool_turn(self, system_prompt, messages, tools)
        dur = time.perf_counter() - t0
        blocos = []
        for b in resposta.content:
            d = b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else dict(b)
            if d.get("type") == "tool_use":
                blocos.append({"tipo": "tool_use", "id": d.get("id"), "nome": d.get("name"), "input": d.get("input")})
            elif d.get("type") == "text":
                blocos.append({"tipo": "text", "texto": d.get("text", "")[:2000]})
        # tool_result que o host devolveu na rodada anterior (última mensagem user)
        anterior = None
        if messages and isinstance(messages[-1].get("content"), list):
            anterior = [
                {"tool_use_id": b.get("tool_use_id"), "is_error": b.get("is_error"),
                 "content": (b.get("content") or "")[:800]}
                for b in messages[-1]["content"] if b.get("type") == "tool_result"
            ]
        u = resposta.usage
        registro["rodadas"].append({
            "modelo": self.model_explainer,
            "n_mensagens_enviadas": len(messages),
            "ferramentas_oferecidas": [t["name"] for t in tools],
            "tool_result_recebido_do_host": anterior,
            "blocos_do_modelo": blocos,
            "stop_reason": resposta.stop_reason,
            "tokens_entrada": getattr(u, "input_tokens", None),
            "tokens_saida": getattr(u, "output_tokens", None),
            "duracao_s": round(dur, 2),
        })
        registro["uso"].append(("sonnet", getattr(u, "input_tokens", 0), getattr(u, "output_tokens", 0)))
        return resposta

    def _call_model(self, model, system_prompt, user_message):
        t0 = time.perf_counter()
        msg = self.client.messages.create(
            model=model, max_tokens=1024, system=system_prompt,
            messages=[{"role": "user", "content": user_message}])
        u = msg.usage
        familia = "haiku" if "haiku" in model else "sonnet"
        registro["uso"].append((familia, getattr(u, "input_tokens", 0), getattr(u, "output_tokens", 0)))
        for block in msg.content:
            if block.type == "text":
                return block.text
        raise ValueError("No text block in model response")

    ClaudeClient.tool_turn = tool_turn
    ClaudeClient._call_model = _call_model


def cenario(nome, mensagem, esperado):
    db = SessionLocal()
    marca_rodadas = len(registro["rodadas"])
    t0 = time.perf_counter()
    try:
        resp = get_orchestrator().process(mensagem, db, "validacao-real")
        saida = {
            "agente": resp.agent_name,
            "tem_calculo": resp.calculation_result is not None,
            "resposta": resp.response[:1500],
        }
        if resp.calculation_result:
            r = resp.calculation_result
            saida["numeros"] = {
                "ganho_bruto": r.ganho_prejuizo_bruto, "ir_devido": r.ir_devido,
                "custos": r.taxas_totais.total, "ganho_liquido_campo": r.ganho_prejuizo_liquido,
                "aliquota": r.aliquota_aplicada, "isencao": r.isenção_aplicada,
            }
        erro = None
    except Exception as e:
        saida = None
        erro = f"{type(e).__name__}: {e}"
    finally:
        db.close()

    rodadas = registro["rodadas"][marca_rodadas:]
    ferramentas = [b["nome"] for r in rodadas for b in r["blocos_do_modelo"] if b["tipo"] == "tool_use"]
    registro["cenarios"].append({
        "nome": nome, "mensagem": mensagem, "esperado": esperado,
        "duracao_s": round(time.perf_counter() - t0, 2),
        "ferramentas_escolhidas_pelo_modelo": ferramentas,
        "n_rodadas": len(rodadas), "saida": saida, "erro": erro,
    })
    print(f"[{nome}] ferramentas={ferramentas} rodadas={len(rodadas)} "
          f"{'erro=' + erro[:70] if erro else 'ok'}")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY ausente."); sys.exit(1)
    instrumentar()
    create_tables()
    from app.vector_db.chroma_client import get_chroma_client
    c = get_chroma_client()
    if c:
        c.load_initial_regulations()

    cenario("1_pergunta_geral", "Qual a diferenca de tributacao entre venda de acoes e venda de cotas de FII?",
            "Resposta consultiva, sem ferramentas de cálculo")
    cenario("2_compra", "Comprei 50 cotas do HGLG11 a 100 reais hoje",
            "Registro de compra, sem ciclo de ferramentas")
    cenario("3_fii_com_compra_previa", "Vendi as 50 cotas do HGLG11 a 110 reais hoje",
            "Modelo deve consultar preco medio (banco) + fee_policy + calculate_trade; IR=R$100")
    cenario("4_fii_custo_informado", "Vendi 10 cotas do KNRI11 a 110 reais hoje, custo medio de 100 reais",
            "Custo informado: nao precisa consultar banco; IR=R$20")
    cenario("5_fii_sem_custo", "Vendi 10 cotas do XPML11 a 110 reais hoje",
            "Sem custo e sem compra previa: deve recusar, sem gravar venda")
    cenario("6_acoes_sem_total_mensal", "Vendi 100 acoes da PETR4 a 30 reais hoje, custo medio 25 reais",
            "Sem total mensal: calculate_trade deve recusar")
    cenario("7_emprestimo_sem_prazo", "Recebi 120 reais de aluguel das minhas 200 acoes da VALE3",
            "Sem prazo do contrato: deve recusar")

    custo = 0.0
    for familia, entrada, saida in registro["uso"]:
        pe, ps = PRECOS[familia]
        custo += (entrada or 0) / 1e6 * pe + (saida or 0) / 1e6 * ps
    registro["custo_estimado_usd"] = round(custo, 4)
    registro["tokens_totais"] = {
        "entrada": sum(e or 0 for _, e, _ in registro["uso"]),
        "saida": sum(s or 0 for _, _, s in registro["uso"]),
        "chamadas": len(registro["uso"]),
    }

    import sqlite3
    conn = sqlite3.connect(f"{TMP.as_posix()}/real.db")
    registro["vendas_gravadas"] = conn.execute(
        "select ativo,tipo_operacao,ir_devido from trades").fetchall()

    out = Path(__file__).resolve().parent / "resultados_modelo_real.json"
    out.write_text(json.dumps(registro, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nTokens: {registro['tokens_totais']}  Custo estimado: US$ {registro['custo_estimado_usd']}")
    print(f"Operações gravadas no banco temporário: {registro['vendas_gravadas']}")
    print(f"Salvo em {out}")
