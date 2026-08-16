"""
Orchestrator — classifies user intent and routes to the right specialist agent.

Multi-Agent RAG flow:
  User message
       ↓
  Orchestrator.classify_intent()  ← Haiku (fast)
       ↓
  Specialist Agent  (AcoesAgent | FIIAgent | OpcoesAgent)
       ↓
  parse_trade → calculate → ChromaDB RAG → specialist explain  ← Sonnet
       ↓
  ChatResponse (with agent_name field)
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.trade import ChatResponse
from app.llm.claude_client import get_claude_client
from app.llm.prompts import ANSWER_QUESTION_SYSTEM
from app.agents.acoes_agent import AcoesAgent
from app.agents.fii_agent import FIIAgent
from app.agents.opcoes_agent import OpcoesAgent
from app.vector_db.chroma_client import get_chroma_client
from app.storage.repository import save_chat

logger = logging.getLogger(__name__)

_GENERAL_AGENT_NAME = "Agente Consultivo"

_AGENTS = {
    "acao": AcoesAgent(),
    "bdr": AcoesAgent(),
    "fii": FIIAgent(),
    "opcao": OpcoesAgent(),
}

_NO_LLM_RESPONSE = (
    "O assistente de IA não está configurado. "
    "Defina ANTHROPIC_API_KEY no arquivo .env e reinicie o servidor. "
    "Para calcular trades diretamente, use a página 'Calcular Trade'."
)


class Orchestrator:
    def process(self, message: str, db: Session, user_id: str) -> ChatResponse:
        """
        Entry point for all chat messages.
        1. Classify intent with Haiku
        2. Route to specialist agent or answer as general question
        """
        claude = get_claude_client()
        if claude is None:
            return ChatResponse(
                response=_NO_LLM_RESPONSE,
                confidence=0.0,
                agent_name=None,
            )

        # ── Step 1: Intent classification ─────────────────────────────────────
        classification = claude.classify_intent(message)
        intent_type: str = classification.get("tipo", "pergunta")
        confidence: float = float(classification.get("confianca", 0.5))

        logger.info(
            f"Orchestrator: '{message[:60]}' → '{intent_type}' "
            f"(confianca={confidence:.2f})"
        )

        # ── Step 2: Route to specialist agent ─────────────────────────────────
        if intent_type in _AGENTS:
            agent = _AGENTS[intent_type]

            # Parse trade (all agents share the same LLM parser)
            trade = claude.parse_trade(message)

            # Delegate full processing to the specialist
            agent_result = agent.process(message, trade, db, user_id, claude)

            return ChatResponse(
                response=agent_result["response"],
                trade_extracted=agent_result["trade_extracted"],
                calculation_result=agent_result["calculation_result"],
                confidence=confidence,
                agent_name=agent_result["agent_name"],
            )

        # ── Step 3: General question — search all regulation collections ───────
        chroma = get_chroma_client()
        context_docs: list = []
        if chroma:
            try:
                context_docs = chroma.search_regulations(message, asset_type="geral", top_k=3)
            except Exception as e:
                logger.warning(f"ChromaDB search failed: {e}")

        context = "\n\n---\n\n".join(context_docs) if context_docs else ""
        answer = claude.answer_question(message, context)

        save_chat(
            db,
            user_id=user_id,
            message=message,
            response=answer,
            trade_extracted=None,
            calculation=None,
        )

        return ChatResponse(
            response=answer,
            trade_extracted=None,
            calculation_result=None,
            confidence=confidence,
            agent_name=_GENERAL_AGENT_NAME,
        )


# Singleton — created once at import time
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
