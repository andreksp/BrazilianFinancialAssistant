"""
Chat API — Phase 7 Multi-Agent implementation.

Flow:
  POST /api/chat/
    Orchestrator.classify_intent()  ← Haiku (asset type detection)
        ↓
    Specialist Agent (AcoesAgent | FIIAgent | OpcoesAgent | General)
        ↓
    parse_trade → calculate → ChromaDB RAG → specialist explain  ← Sonnet
        ↓
    ChatResponse (includes agent_name to show which specialist handled it)

GET /api/chat/history — paginated chat history
"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.trade import ChatRequest, ChatResponse
from app.agents.orchestrator import get_orchestrator
from app.storage.database import get_db
from app.storage.repository import get_chat_history as db_get_chat_history

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Process a chat message via the multi-agent orchestrator.
    The orchestrator classifies intent, routes to a specialist agent,
    and returns a domain-expert response with calculation results when applicable.
    """
    user_id = request.user_id or "default"
    message = request.message.strip()
    logger.info(f"Chat message from '{user_id}': {message[:80]}")

    orchestrator = get_orchestrator()
    return orchestrator.process(message, db, user_id)


@router.get("/history")
async def get_history(
    user_id: str = Query(default="default"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return recent chat history for a user."""
    records = db_get_chat_history(db, user_id=user_id, limit=limit)
    return [
        {
            "id": str(r.id),
            "message": r.message,
            "response": r.response,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
