"""
Complemento aos testes adversariais: casos exigidos pelo prompt de validação que
não estavam cobertos — ferramenta desconhecida, repetição de chamada (id duplicado),
limite de chamadas e limite de rodadas.

Guardas exercitadas em backend/app/agents/tool_chat.py:
  linha  70-71  MAX_CALLS  -> "Limite de chamadas de ferramentas atingido."
  linha  76-78  seen_ids   -> id repetido é recusado
  linha  122    catálogo   -> "Ferramenta não autorizada."
  linha  130    MAX_ROUNDS -> "Limite de rodadas de ferramentas atingido."

Modelo SIMULADO (sem custo). Servidor MCP real por stdio.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT / "backend"))

from app.agents import tool_chat
from app.models.trade import TradeInput

RESULTS = []


def record(name, status, detail):
    RESULTS.append({"caso": name, "status": status, "detalhe": detail})
    print(f"[{status}] {name}: {detail}")


def trade():
    return TradeInput(ativo="HGLG11", tipo_ativo="fii", tipo_operacao="venda", quantidade=10,
                      preco_unitario=110, data_operacao="2026-09-20", custos_operacao=0,
                      preco_medio_informado=100)


def call(name, ident):
    return {"type": "tool_use", "id": ident, "name": name, "input": {}}


class Roteiro:
    """Dublê de LLM que emite uma sequência fixa de blocos por rodada."""

    def __init__(self, rodadas):
        self.rodadas = rodadas
        self.n = 0
        self.vistas = []
        self.historico = []

    def tool_turn(self, system_prompt, messages, tools):
        self.vistas.append([t["name"] for t in tools])
        self.historico.append([dict(m) for m in messages])
        bloco = self.rodadas[min(self.n, len(self.rodadas) - 1)]
        self.n += 1
        return SimpleNamespace(content=bloco, stop_reason="tool_use")


def executar(roteiro):
    try:
        tool_chat.run_tool_chat(roteiro, "Sistema", "Venda", trade(), "", lambda: 100.0)
        return None
    except ValueError as exc:
        return str(exc)


def teste_ferramenta_desconhecida():
    # O modelo pede uma ferramenta que nao foi oferecida. A guarda de catalogo
    # (linha 122) devolve o erro ao modelo como tool_result; o ciclo nao aborta.
    # Verificamos o tool_result efetivamente devolvido, nao apenas a excecao final.
    r = Roteiro([[call("consultar_saldo_bancario", "x1")], [call("fee_policy", "x2")]])
    executar(r)
    devolvido = None
    for msgs in r.historico:
        for m in msgs:
            if m.get("role") == "user" and isinstance(m.get("content"), list):
                for b in m["content"]:
                    if b.get("type") == "tool_result" and b.get("is_error"):
                        devolvido = b.get("content")
    ofertadas = r.vistas[0] if r.vistas else []
    ok = (devolvido is not None and "nao autorizada" in (devolvido or "").lower().replace("ã", "a")
          and "consultar_saldo_bancario" not in ofertadas)
    record("ferramenta_desconhecida", "OK" if ok else "FALHA",
           f"Ferramentas oferecidas={ofertadas}; ferramenta inventada nunca executada. "
           f"tool_result devolvido ao modelo={devolvido}")


def teste_id_duplicado():
    # O modelo repete o mesmo tool_use id em rodadas diferentes.
    r = Roteiro([[call("fee_policy", "mesmo_id")], [call("fee_policy", "mesmo_id")]])
    erro = executar(r)
    ok = erro is not None
    record("repeticao_id_duplicado", "OK" if ok else "FALHA",
           f"Reuso do mesmo tool_use_id recusado. Erro='{erro}'")


def teste_limite_de_chamadas():
    # Nove chamadas numa única rodada; MAX_CALLS = 8.
    blocos = [call("fee_policy", f"c{i}") for i in range(9)]
    erro = executar(Roteiro([blocos]))
    ok = erro is not None and "chamadas" in (erro or "").lower()
    record("limite_de_chamadas", "OK" if ok else "FALHA",
           f"MAX_CALLS=8 aplicado antes de executar a rodada. Erro='{erro}'")


def teste_limite_de_rodadas():
    # O modelo nunca conclui: pede fee_policy indefinidamente. MAX_ROUNDS = 6.
    r = Roteiro([[call("fee_policy", f"r{i}")] for i in range(12)])
    erro = executar(r)
    ok = erro is not None and "rodadas" in (erro or "").lower()
    record("limite_de_rodadas", "OK" if ok else "FALHA",
           f"Ciclo encerrado após {r.n} rodadas (MAX_ROUNDS=6). Erro='{erro}'")


if __name__ == "__main__":
    teste_ferramenta_desconhecida()
    teste_id_duplicado()
    teste_limite_de_chamadas()
    teste_limite_de_rodadas()

    total = len(RESULTS)
    ok = sum(1 for r in RESULTS if r["status"] == "OK")
    falhas = sum(1 for r in RESULTS if r["status"] == "FALHA")
    print(f"\nTotal={total} OK={ok} FALHA={falhas}")
    out = Path(__file__).resolve().parent / "resultados_adversariais_limites.json"
    out.write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Salvo em {out}")
