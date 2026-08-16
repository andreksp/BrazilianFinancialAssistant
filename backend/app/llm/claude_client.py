"""
Anthropic Claude API client — Phase 3 implementation.

Models:
- claude-haiku-4-5-20251001: Fast, cheap parsing of natural language trades
- claude-sonnet-4-6: Intelligent explanations and Q&A
"""

import json
import logging
from datetime import date
from typing import Optional

from anthropic import Anthropic

from app.models.trade import TradeInput, TaxCalculationResult, AssetType, OperationType
from app.core.config import settings
from app.llm.prompts import (
    PARSE_TRADE_SYSTEM,
    EXPLAIN_CALCULATION_SYSTEM,
    ANSWER_QUESTION_SYSTEM,
    ORCHESTRATOR_SYSTEM,
)

logger = logging.getLogger(__name__)


class ClaudeClient:
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model_parser = settings.LLM_MODEL_PARSER
        self.model_explainer = settings.LLM_MODEL_EXPLAINER

    def parse_trade(self, user_message: str) -> Optional[TradeInput]:
        """
        Parse natural language trade description into a TradeInput.
        Uses Haiku for speed. Returns None if no trade is found in the message.
        """
        today = date.today().strftime("%Y-%m-%d")
        prompt = f"Data de hoje: {today}\n\nMensagem do usuário: {user_message}"

        try:
            raw = self._call_model(self.model_parser, PARSE_TRADE_SYSTEM, prompt)
            raw = raw.strip()

            # Strip markdown fences if the model wraps the JSON
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            data = json.loads(raw)

            if "erro" in data:
                logger.info(f"No trade extracted: {data['erro']}")
                return None

            return TradeInput(
                ativo=data["ativo"].upper(),
                tipo_ativo=AssetType(data["tipo_ativo"]),
                tipo_operacao=OperationType(data["tipo_operacao"]),
                quantidade=float(data["quantidade"]),
                preco_unitario=float(data["preco_unitario"]),
                data_operacao=date.fromisoformat(data["data_operacao"]),
                corretora=data.get("corretora"),
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse trade from message: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in parse_trade: {e}", exc_info=True)
            return None

    def explain_calculation(self, result: TaxCalculationResult, context: str = "") -> str:
        """
        Generate a PT-BR explanation of a tax calculation result.
        Uses Sonnet for better reasoning quality.
        """

        def fmt(v: float) -> str:
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        tipo = result.tipo_operacao_classificacao.value.replace("_", " ").title()
        isento = " (ISENTO — vendas abaixo de R$ 20.000 no mês)" if result.isenção_aplicada else ""

        summary = (
            f"Ativo: {result.ativo} ({result.tipo_ativo.value.upper()})\n"
            f"Data: {result.data_operacao.strftime('%d/%m/%Y')}\n"
            f"Quantidade: {int(result.quantidade)} unidades\n"
            f"Preço de venda: {fmt(result.preco_unitario)}\n"
            f"Valor financeiro: {fmt(result.valor_financeiro)}\n"
            f"Ganho/Prejuízo bruto: {fmt(result.ganho_prejuizo_bruto)}\n"
            f"Tipo de operação: {tipo}\n"
            f"Alíquota IR: {result.aliquota_aplicada * 100:.0f}%{isento}\n"
            f"IR devido: {fmt(result.ir_devido)}\n"
            f"IRRF retido na fonte: {fmt(result.irrf_retido)}\n"
            f"Taxas B3: {fmt(result.taxas_totais.total)}\n"
            f"Ganho/Prejuízo líquido: {fmt(result.ganho_prejuizo_liquido)}\n"
            f"Valor líquido a receber: {fmt(result.valor_liquido)}\n"
        )

        context_block = f"\nCONTEXTO REGULATÓRIO:\n{context}\n" if context else ""
        user_msg = f"Explique este resultado de cálculo:{context_block}\n\n{summary}"

        try:
            return self._call_model(self.model_explainer, EXPLAIN_CALCULATION_SYSTEM, user_msg)
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}", exc_info=True)
            return result.mensagem or f"Cálculo concluído para {result.ativo}. IR devido: {fmt(result.ir_devido)}."

    def answer_question(self, question: str, context: str = "") -> str:
        """
        Answer a general financial question using regulatory context from ChromaDB.
        """
        context_block = f"CONTEXTO:\n{context}\n\n" if context else ""
        user_msg = f"{context_block}Pergunta: {question}"

        try:
            return self._call_model(self.model_explainer, ANSWER_QUESTION_SYSTEM, user_msg)
        except Exception as e:
            logger.error(f"Failed to answer question: {e}", exc_info=True)
            return "Desculpe, não consegui processar sua pergunta. Tente novamente."

    def chat(self, system_prompt: str, user_message: str, use_haiku: bool = False) -> str:
        """Generic chat call — use_haiku=True for fast classification tasks."""
        model = self.model_parser if use_haiku else self.model_explainer
        return self._call_model(model, system_prompt, user_message)

    def classify_intent(self, message: str) -> dict:
        """
        Classify message intent (acao/bdr/fii/opcao/pergunta) using Haiku.
        Returns dict with keys: tipo, ativo, confianca.
        """
        import json as _json
        try:
            raw = self._call_model(self.model_parser, ORCHESTRATOR_SYSTEM, message).strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1].lstrip("json").strip()
            return _json.loads(raw)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            return {"tipo": "pergunta", "ativo": None, "confianca": 0.5}

    def _call_model(self, model: str, system_prompt: str, user_message: str) -> str:
        message = self.client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text


_client: Optional[ClaudeClient] = None


def get_claude_client() -> Optional[ClaudeClient]:
    """Return a shared ClaudeClient, or None if ANTHROPIC_API_KEY is not configured."""
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            return None
        try:
            _client = ClaudeClient()
        except Exception as e:
            logger.error(f"Failed to initialize ClaudeClient: {e}")
            return None
    return _client
