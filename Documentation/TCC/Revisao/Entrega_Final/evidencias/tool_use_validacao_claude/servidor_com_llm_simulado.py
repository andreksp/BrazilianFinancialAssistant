"""
Sobe o backend REAL (FastAPI + MCP real por stdio) com o cliente Anthropic
substituído por um dublê com latência realista. Objetivo: medir o comportamento
de concorrência do serviço completo sem chamadas pagas.

O que é real aqui: FastAPI, roteamento, orquestrador, agentes, tool_chat,
subprocesso MCP, calculadoras, persistência. O que é simulado: apenas as
respostas do modelo (classificação, extração e seleção de ferramentas).
"""
import sys
import time
from pathlib import Path
from types import SimpleNamespace

PROJECT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT / "backend"))

# Latência artificial por chamada ao "modelo", para tornar visível qualquer
# bloqueio do event loop durante a janela da requisição.
LLM_LATENCIA_S = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8


class DubleClaude:
    """Reproduz a interface usada pelo backend, com respostas roteirizadas."""

    def __init__(self):
        self.model_parser = "duble-haiku"
        self.model_explainer = "duble-sonnet"
        self._turnos = {}

    # --- usados pelo orquestrador/agentes ---
    def classify_intent(self, message):
        time.sleep(LLM_LATENCIA_S)
        return {"tipo": "fii", "ativo": "HGLG11", "confianca": 0.98}

    def parse_trade(self, user_message):
        time.sleep(LLM_LATENCIA_S)
        from app.models.trade import TradeInput
        return TradeInput(ativo="HGLG11", tipo_ativo="fii", tipo_operacao="venda",
                          quantidade=10, preco_unitario=110, data_operacao="2026-09-20",
                          preco_medio_informado=100, custos_operacao=0)

    def chat(self, system_prompt, user_message, use_haiku=False):
        time.sleep(LLM_LATENCIA_S)
        return "Resposta simulada."

    # --- usado pelo tool_chat (seleção de ferramentas) ---
    def tool_turn(self, system_prompt, messages, tools):
        time.sleep(LLM_LATENCIA_S)
        chave = id(messages)
        rodada = self._turnos.get(len(messages), 0)
        self._turnos[len(messages)] = rodada + 1
        # 1ª rodada: pede política; 2ª: calcula; 3ª: conclui.
        if len(messages) == 1:
            return SimpleNamespace(
                content=[{"type": "tool_use", "id": "p1", "name": "fee_policy", "input": {}}],
                stop_reason="tool_use")
        if len(messages) == 3:
            return SimpleNamespace(
                content=[{"type": "tool_use", "id": "t1", "name": "calculate_trade", "input": {}}],
                stop_reason="tool_use")
        return SimpleNamespace(
            content=[{"type": "text", "text": "Explicação simulada do cálculo."}],
            stop_reason="end_turn")


import app.llm.claude_client as cc
_duble = DubleClaude()
cc.get_claude_client = lambda: _duble
import app.agents.orchestrator as orch
orch.get_claude_client = lambda: _duble

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8030, log_level="warning")
