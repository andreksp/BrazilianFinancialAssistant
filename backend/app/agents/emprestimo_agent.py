"""Specialist agent for Empréstimo de Ações (securities lending, doador side)."""

from app.models.trade import AssetType
from app.calculations.lending.emprestimo import EmprestimoCalculator
from app.llm.prompts import EXPLAIN_EMPRESTIMO_SYSTEM
from app.agents.base_agent import BaseAgent


class EmprestimoAgent(BaseAgent):
    name = "Agente Especialista em Empréstimo de Ações"
    supported_asset_types = [AssetType.EMPRESTIMO_ACOES]
    chroma_scope = "geral"

    _calculator = EmprestimoCalculator()

    def get_explain_system_prompt(self) -> str:
        return EXPLAIN_EMPRESTIMO_SYSTEM

    def get_calculator(self, asset_type: AssetType):
        return self._calculator
