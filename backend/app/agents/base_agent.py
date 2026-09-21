"""Abstract base class for all specialist agents."""

from abc import ABC, abstractmethod
from app.agents.tool_chat import run_tool_chat
from typing import Optional

from sqlalchemy.orm import Session

from app.models.trade import (
    AssetType,
    OperationType,
    TradeInput,
    TaxCalculationResult,
)
from app.storage.repository import get_average_price, save_trade, save_chat
from app.vector_db.chroma_client import get_chroma_client


class BaseAgent(ABC):
    name: str = "Agente"
    supported_asset_types: list = []
    chroma_scope: str = "geral"

    @abstractmethod
    def get_explain_system_prompt(self) -> str:
        """Domain-specific system prompt for result explanations."""

    @abstractmethod
    def get_calculator(self, asset_type: AssetType):
        """Return the calculator instance for the given asset type."""

    def process(self, message, trade, db, user_id, claude):
        try:
            return self._process(message, trade, db, user_id, claude)
        except ValueError as exc:
            db.rollback()
            response = f"Não foi possível calcular com segurança: {exc} Nenhuma venda foi registrada."
            save_chat(db, user_id=user_id, message=message, response=response,
                      trade_extracted=trade, calculation=None)
            return dict(response=response, trade_extracted=trade,
                        calculation_result=None, agent_name=self.name)

    def _process(
        self,
        message: str,
        trade: Optional[TradeInput],
        db: Session,
        user_id: str,
        claude,
    ) -> dict:
        """
        Full processing pipeline for a message.
        Returns dict with response, trade_extracted, calculation_result, agent_name.
        """
        chroma = get_chroma_client()
        result: Optional[TaxCalculationResult] = None

        if trade is not None:
            if trade.tipo_operacao == OperationType.COMPRA:
                save_trade(db, trade, result=None, user_id=user_id)
                explanation = self._buy_confirmation(trade)
            else:
                context_docs = []
                if chroma:
                    context_docs = chroma.search_regulations(
                        message, asset_type=self.chroma_scope, top_k=2
                    )
                context = "\n\n---\n\n".join(context_docs) if context_docs else ""
                explanation, result = run_tool_chat(
                    claude, self.get_explain_system_prompt(), message, trade, context,
                    lambda: get_average_price(db, user_id=user_id, ativo=trade.ativo),
                )
                save_trade(db, trade, result=result, user_id=user_id)
        else:
            context_docs = []
            if chroma:
                context_docs = chroma.search_regulations(
                    message, asset_type=self.chroma_scope, top_k=3
                )
            context = "\n\n---\n\n".join(context_docs) if context_docs else ""
            ctx_block = f"CONTEXTO:\n{context}\n\n" if context else ""
            explanation = claude.chat(
                self.get_explain_system_prompt(),
                f"{ctx_block}Pergunta: {message}",
            )

        save_chat(
            db,
            user_id=user_id,
            message=message,
            response=explanation,
            trade_extracted=trade,
            calculation=result,
        )

        return {
            "response": explanation,
            "trade_extracted": trade,
            "calculation_result": result,
            "agent_name": self.name,
        }

    # ── helpers ───────────────────────────────────────────────────────────────

    def _buy_confirmation(self, trade: TradeInput) -> str:
        qty = f"{trade.quantidade:g}"
        price = f"R$ {trade.preco_unitario:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        date = trade.data_operacao.strftime("%d/%m/%Y")
        return (
            f"[{self.name}] Registrei a compra de {qty} {trade.ativo} "
            f"a {price} em {date}. "
            "Preço médio atualizado. Quando você vender, calcularei o IR automaticamente."
        )

    def _format_result_prompt(self, result: TaxCalculationResult, context: str) -> str:
        def fmt(v: float) -> str:
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        tipo = result.tipo_operacao_classificacao.value.replace("_", " ").title()
        limite = "35.000" if result.tipo_ativo == AssetType.CRIPTO else "20.000"
        isento = f" (ISENÇÃO — total mensal informado até R$ {limite})" if result.isenção_aplicada else ""

        summary = (
            f"Ativo: {result.ativo} ({result.tipo_ativo.value.upper()})\n"
            f"Data: {result.data_operacao.strftime('%d/%m/%Y')}\n"
            f"Quantidade: {result.quantidade:g} unidades\n"
            f"Preço de venda: {fmt(result.preco_unitario)}\n"
            f"Valor financeiro: {fmt(result.valor_financeiro)}\n"
            f"Ganho/Prejuízo bruto: {fmt(result.ganho_prejuizo_bruto)}\n"
            f"Tipo de operação: {tipo}\n"
            f"Alíquota IR: {result.aliquota_aplicada * 100:.0f}%{isento}\n"
            f"IR devido: {fmt(result.ir_devido)}\n"
            f"IRRF retido: {fmt(result.irrf_retido)}\n"
            f"Custos da operação: {fmt(result.taxas_totais.total)}\n"
            f"Ressalvas do motor: {result.mensagem or ''}\n"
            f"Ganho/Prejuízo líquido: {fmt(result.ganho_prejuizo_liquido)}\n"
            f"Valor líquido a receber: {fmt(result.valor_liquido)}\n"
        )

        ctx_block = f"\nCONTEXTO REGULATÓRIO:\n{context}\n" if context else ""
        return f"Explique este resultado de cálculo:{ctx_block}\n\n{summary}"
