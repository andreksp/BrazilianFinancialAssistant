"""Specialist agent for Opções sobre Ações (stock options)."""

from app.models.trade import AssetType
from app.calculations.equity.opcoes import OpcoesCalculator
from app.llm.prompts import EXPLAIN_OPCOES_SYSTEM
from app.agents.base_agent import BaseAgent


class OpcoesAgent(BaseAgent):
    name = "Agente Especialista em Opções"
    supported_asset_types = [AssetType.OPCAO]
    chroma_scope = "acoes"

    _calculator = OpcoesCalculator()

    def get_explain_system_prompt(self) -> str:
        return EXPLAIN_OPCOES_SYSTEM

    def get_calculator(self, asset_type: AssetType):
        return self._calculator
