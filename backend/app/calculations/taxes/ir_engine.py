"""
Central IR (Imposto de Renda) calculation engine.

Business Logic Reference: Documentation/research.md sections 1-5
- IR rates: 15% (swing) or 20% (day trade)
- Exemption: R$20,000/month for swing trades only
- IRRF: 0,005% (swing) or 1% (day trade)
- Loss compensation: Within same category (swing or day trade), same month
- Average price: Weighted moving average for each asset
"""

import calendar
from datetime import date
from typing import Dict, List, Optional
from decimal import Decimal

from app.models.trade import (
    TradeInput,
    TradeOperationType,
    TaxCalculationResult,
    PortfolioPosition,
    MonthlyTaxSummary,
    AssetType,
    OperationType,
)


class TaxEngine:
    """
    Central engine for managing all tax calculations.

    Responsibilities:
    1. Track portfolio positions (average price per asset)
    2. Classify trades (swing vs day trade)
    3. Calculate monthly tax summaries
    4. Track losses for compensation
    5. Calculate DARF due dates and amounts
    """

    def __init__(self):
        """Initialize the tax engine."""
        # Portfolio tracking: {ativo: PortfolioPosition}
        self.positions: Dict[str, PortfolioPosition] = {}

        # Monthly results: {(month, year): {asset_type: [TaxCalculationResult]}}
        self.monthly_results: Dict[tuple, List[TaxCalculationResult]] = {}

        # Loss tracking: {(month, year): {asset_type: {swing_loss, day_loss}}}
        self.monthly_losses: Dict[tuple, Dict[str, Dict[str, float]]] = {}

    def add_trade(self, trade: TradeInput, calculation_result: TaxCalculationResult) -> None:
        """
        Add a trade result to the engine for tracking and compensation.

        Args:
            trade: The trade input
            calculation_result: Calculated result from specific calculator
        """
        month_year = (trade.data_operacao.month, trade.data_operacao.year)

        # Store result
        if month_year not in self.monthly_results:
            self.monthly_results[month_year] = []
        self.monthly_results[month_year].append(calculation_result)

        # Update position (if buy operation)
        if trade.tipo_operacao == OperationType.COMPRA:
            self._update_position(trade)

    def _update_position(self, trade: TradeInput) -> None:
        """
        Update portfolio position with new purchase.

        Implements weighted average price formula:
        PM = (Qtd_anterior * PM_anterior + Qtd_nova * Preço_novo) / (Qtd_anterior + Qtd_nova)
        """
        if trade.ativo not in self.positions:
            # First purchase
            self.positions[trade.ativo] = PortfolioPosition(
                ativo=trade.ativo,
                tipo_ativo=trade.tipo_ativo,
                quantidade_total=trade.quantidade,
                preco_medio=trade.preco_unitario,
                data_primeira_compra=trade.data_operacao,
                data_ultima_compra=trade.data_operacao,
                valor_total_investido=trade.quantidade * trade.preco_unitario,
            )
        else:
            # Update existing position with new purchase
            pos = self.positions[trade.ativo]
            novo_investimento = trade.quantidade * trade.preco_unitario

            # Weighted average formula
            novo_preco_medio = (
                pos.quantidade_total * pos.preco_medio + novo_investimento
            ) / (pos.quantidade_total + trade.quantidade)

            pos.quantidade_total += trade.quantidade
            pos.preco_medio = novo_preco_medio
            pos.data_ultima_compra = trade.data_operacao
            pos.valor_total_investido += novo_investimento

    def get_average_price(self, ativo: str) -> Optional[float]:
        """Get current weighted average price for an asset."""
        return self.positions.get(ativo, {}).preco_medio if ativo in self.positions else None

    def get_monthly_summary(self, mes: int, ano: int) -> MonthlyTaxSummary:
        """
        Generate monthly tax summary for a specific month.

        Used for:
        1. DARF calculation (tax due date)
        2. IR reporting
        3. Loss compensation tracking
        """
        month_year = (mes, ano)
        results = self.monthly_results.get(month_year, [])

        summary = MonthlyTaxSummary(
            mes=mes,
            ano=ano,
            darf_vencimento=self._calculate_darf_deadline(mes, ano),
        )

        # Aggregate results by type
        for result in results:
            if result.tipo_operacao_classificacao == TradeOperationType.SWING:
                if result.ganho_prejuizo_bruto >= 0:
                    summary.ganho_swing_trade += result.ganho_prejuizo_bruto
                else:
                    summary.prejuizo_swing_trade += abs(result.ganho_prejuizo_bruto)
                summary.ir_swing_trade += result.ir_devido
            else:  # DAY_TRADE
                if result.ganho_prejuizo_bruto >= 0:
                    summary.ganho_day_trade += result.ganho_prejuizo_bruto
                else:
                    summary.prejuizo_day_trade += abs(result.ganho_prejuizo_bruto)
                summary.ir_day_trade += result.ir_devido

            summary.irrf_retido_total += result.irrf_retido

        # Calculate total IR (before loss compensation)
        summary.ir_total_devido = summary.ir_swing_trade + summary.ir_day_trade

        # TODO: Apply loss compensation rules here
        # Regra: Prejuízo swing compensa ganho swing
        # Prejuízo day compensa ganho day
        # Não se compensam entre si

        return summary

    def _calculate_darf_deadline(self, mes: int, ano: int) -> date:
        """
        Calculate DARF due date: last day of the following month.

        Reference: research.md - DARF vencimento (último dia útil do mês seguinte)
        MVP: uses last calendar day. Production should check actual business days.
        """
        next_month = (mes % 12) + 1
        next_year = ano + 1 if mes == 12 else ano
        last_day = calendar.monthrange(next_year, next_month)[1]
        return date(next_year, next_month, last_day)

    def get_total_ir_due(self) -> float:
        """Calculate total IR due across all months."""
        total = 0.0
        for month_year, _ in self.monthly_results.items():
            summary = self.get_monthly_summary(month_year[0], month_year[1])
            total += summary.ir_a_pagar
        return total

    def export_monthly_summaries(self) -> List[MonthlyTaxSummary]:
        """Export all monthly summaries for user review."""
        summaries = []
        for month_year in sorted(self.monthly_results.keys()):
            summary = self.get_monthly_summary(month_year[0], month_year[1])
            if summary.ir_total_devido > 0 or summary.ganho_swing_trade > 0:
                summaries.append(summary)
        return summaries
