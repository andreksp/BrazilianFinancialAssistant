"""
API routes for chat-based trade input and LLM interaction.

Endpoints:
- POST /api/chat/message - Send message, get response with trade extraction
- GET /api/chat/history - Get chat history

Phase 1: Simple chat with placeholder LLM responses
Phase 3: Full integration with Claude API and ChromaDB
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.trade import ChatRequest, ChatResponse, TradeInput

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """
    Send a message and get assistant response with extracted trade.

    Phase 1 (MVP):
    - Parse trade from message (placeholder)
    - Return formatted response

    Phase 3:
    - Use Claude API for natural language parsing
    - Use ChromaDB for regulatory context
    - Calculate taxes with extracted trade

    Args:
        request: Chat message from user

    Returns:
        Assistant response with extracted trade (if recognized)

    Example:
        POST /api/chat/message
        {
            "message": "Vendi 100 ações da PETR4 por R$25,50 cada",
            "user_id": "user123"
        }

        Response:
        {
            "response": "Entendi. Você vendeu 100 ações da PETR4 a R$25,50...",
            "trade_extracted": {...},
            "calculation_result": {...},
            "confidence": 0.95
        }
    """
    try:
        logger.info(f"Processing chat message from user: {request.user_id}")

        # TODO: Phase 3 - Integrate Claude API
        # 1. Call Claude Haiku to parse trade
        # 2. Validate extracted trade
        # 3. Calculate with TaxEngine
        # 4. Call Claude Sonnet to explain result
        # 5. Save to ChatHistory

        # MVP Response (placeholder)
        response = ChatResponse(
            response="Desculpe, o chat ainda não está disponível. Use o formulário de entrada de trades.",
            trade_extracted=None,
            calculation_result=None,
            confidence=0.0,
        )

        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history")
async def get_chat_history(
    user_id: str = None,
    limit: int = 50,
):
    """
    Get chat history for a user.

    TODO: Implement with database storage
    """
    # TODO: Fetch from database
    return []
