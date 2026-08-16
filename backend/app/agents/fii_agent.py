"""Specialist agent for Fundos de Investimento Imobiliário (FIIs)."""

from app.models.trade import AssetType
from app.calculations.equity.fiis import FIICalculator
from app.llm.prompts import EXPLAIN_FII_SYSTEM
from app.agents.base_agent import BaseAgent


class FIIAgent(BaseAgent):
    name = "Agente Especialista em Fundos Imobiliários"
    supported_asset_types = [AssetType.FII]
    chroma_scope = "geral"

    _calculator = FIICalculator()

    def get_explain_system_prompt(self) -> str:
        return EXPLAIN_FII_SYSTEM

    def get_calculator(self, asset_type: AssetType):
        return self._calculator
