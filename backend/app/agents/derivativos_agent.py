"""Specialist agent for listed futures (Futuro de Dólar / Futuro de Índice)."""

from app.models.trade import AssetType
from app.calculations.derivatives.futuros import FuturosCalculator
from app.llm.prompts import EXPLAIN_FUTUROS_SYSTEM
from app.agents.base_agent import BaseAgent


class DerivativosAgent(BaseAgent):
    name = "Agente Especialista em Mercado Futuro"
    supported_asset_types = [AssetType.FUTURO_DOLAR, AssetType.FUTURO_INDICE]
    chroma_scope = "geral"

    _calculator = FuturosCalculator()

    def get_explain_system_prompt(self) -> str:
        return EXPLAIN_FUTUROS_SYSTEM

    def get_calculator(self, asset_type: AssetType):
        return self._calculator
