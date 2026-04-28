"""
Anthropic Claude API client integration (Phase 3).

Models:
- claude-haiku-4-5: Fast, cheap parsing of natural language trades
- claude-sonnet-4-6: Intelligent explanations of calculations

Reference: Documentation/research.md for tax rules used in prompts
"""

import json
import logging
from typing import Optional

from anthropic import Anthropic

from app.models.trade import TradeInput, TaxCalculationResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for interacting with Claude API.

    Responsibilities:
    1. Parse natural language trade input → TradeInput
    2. Explain calculation results in Portuguese
    3. Answer questions about regulations with ChromaDB context
    """

    def __init__(self):
        """Initialize Claude client with API key."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model_parser = settings.LLM_MODEL_PARSER
        self.model_explainer = settings.LLM_MODEL_EXPLAINER

    def parse_trade(self, user_message: str) -> Optional[TradeInput]:
        """
        Parse natural language trade description to structured TradeInput.

        Uses Claude Haiku for speed and cost efficiency.

        Args:
            user_message: User's natural language trade description in Portuguese

        Returns:
            Extracted TradeInput or None if no trade found

        Example:
            Input: "Vendi 100 ações da PETR4 por R$25,50 cada em 15/03/2025"
            Output: TradeInput(
                ativo="PETR4",
                tipo_ativo="acao",
                tipo_operacao="venda",
                quantidade=100,
                preco_unitario=25.50,
                data_operacao=date(2025, 3, 15)
            )
        """
        # Phase 3 implementation
        # TODO: Implement with prompt engineering
        return None

    def explain_calculation(self, result: TaxCalculationResult, context: str = "") -> str:
        """
        Explain calculation result in Portuguese.

        Uses Claude Sonnet for better reasoning and explanation quality.

        Args:
            result: Tax calculation result
            context: Optional regulatory context from ChromaDB

        Returns:
            User-friendly explanation of the calculation

        Example:
            Output: "Você vendeu 100 ações da PETR4 por R$2.550,00...
                    Ganho bruto: R$500,00
                    IR a pagar: R$75,00 (15%)
                    Você recebeu líquido: R$2.425,00..."
        """
        # Phase 3 implementation
        # TODO: Generate explanation with numbers formatted in PT-BR
        return ""

    def answer_question(self, question: str, context: str = "") -> str:
        """
        Answer user question about regulations and taxes.

        Uses ChromaDB context for accurate regulatory references.

        Args:
            question: User question in Portuguese
            context: Relevant regulations from ChromaDB

        Returns:
            Answer in Portuguese
        """
        # Phase 3 implementation
        return ""

    def _call_model(
        self, model: str, system_prompt: str, user_message: str
    ) -> str:
        """
        Internal method to call Claude model.

        Args:
            model: Model ID (haiku or sonnet)
            system_prompt: System prompt with instructions
            user_message: User message

        Returns:
            Model response
        """
        message = self.client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return message.content[0].text


# Module-level client instance
_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """Get or create global Claude client instance."""
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client
