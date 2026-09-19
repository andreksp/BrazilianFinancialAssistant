"""Specialist agent for Criptomoedas (Bitcoin, altcoins, stablecoins)."""

from app.models.trade import AssetType
from app.calculations.crypto.criptomoedas import CriptomoedaCalculator
from app.llm.prompts import EXPLAIN_CRIPTO_SYSTEM
from app.agents.base_agent import BaseAgent


class CriptoAgent(BaseAgent):
    name = "Agente Especialista em Criptomoedas"
    supported_asset_types = [AssetType.CRIPTO]
    chroma_scope = "cripto"

    _calculator = CriptomoedaCalculator()

    def get_explain_system_prompt(self) -> str:
        return EXPLAIN_CRIPTO_SYSTEM

    def get_calculator(self, asset_type: AssetType):
        return self._calculator
