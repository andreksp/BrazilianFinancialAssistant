"""Specialist agent for Ações (stocks) and BDRs."""

from app.models.trade import AssetType
from app.calculations.equity.acoes import AcoesCalculator
from app.calculations.equity.bdrs import BDRCalculator
from app.llm.prompts import EXPLAIN_ACOES_SYSTEM
from app.agents.base_agent import BaseAgent


class AcoesAgent(BaseAgent):
    name = "Agente Especialista em Ações e BDRs"
    supported_asset_types = [AssetType.ACAO, AssetType.BDR]
    chroma_scope = "acoes"

    _calculators = {
        AssetType.ACAO: AcoesCalculator(),
        AssetType.BDR: BDRCalculator(),
    }

    def get_explain_system_prompt(self) -> str:
        return EXPLAIN_ACOES_SYSTEM

    def get_calculator(self, asset_type: AssetType):
        return self._calculators.get(asset_type, AcoesCalculator())
