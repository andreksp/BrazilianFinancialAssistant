"""
Calculation module for Ações (Stocks) - Phase 1.

Business Logic Reference: Documentation/research.md section 1
- Swing trade: 15% IR (with R$20,000/month exemption), 0,005% IRRF
- Day trade: 20% IR (no exemption), 1% IRRF
- Average price: Weighted moving average
- Loss compensation: Within same category (swing or day), same month

CRITICAL RULES:
1. Exemption R$20,000 applies to TOTAL sold in month (not per asset)
2. Day trade and swing trade are separate tax bases (no compensation between them)
3. Prejudice in day trade does NOT carry to next month (only swing trade)
"""

from datetime import date
from typing import Optional

from app.models.trade import (
    TradeInput,
    TradeOperationType,
    TaxCalculationResult,
    AssetType,
    FeesBreakdown,
)
from app.calculations.base import BaseCalculator
from app.calculations.fees.b3_fees import calculate_b3_fees


class AcoesCalculator(BaseCalculator):
    """
    Calculator for Ações (stock) trades.

    Tax Rules (from research.md):
    - Alíquota: 15% (swing) or 20% (day trade)
    - Isenção: R$20.000 total vendido/mês (swing trade only)
    - IRRF: 0,005% (swing) or 1% (day trade)
    """

    SWING_TRADE_RATE = 0.15  # 15%
    DAY_TRADE_RATE = 0.20  # 20%
    EXEMPTION_LIMIT = 20000.0  # R$20,000 per month
    SWING_IRRF_RATE = 0.00005  # 0,005%
    DAY_IRRF_RATE = 0.01  # 1%

    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        """
        Calculate gain or loss.

        Simple formula: (sale_price - purchase_price) * quantity
        In practice, purchase_price is the weighted average price.

        Args:
            quantity: Number of shares sold
            purchase_price: Average price (weighted moving average)
            sale_price: Sale price per share

        Returns:
            Gain (positive) or loss (negative)
        """
        return (sale_price - purchase_price) * quantity

    def get_tax_rate(self, is_day_trade: bool = False) -> float:
        """Get applicable tax rate for Ações."""
        return self.DAY_TRADE_RATE if is_day_trade else self.SWING_TRADE_RATE

    def get_irrf_rate(self, is_day_trade: bool = False) -> float:
        """Get IRRF (withholding tax) rate."""
        return self.DAY_IRRF_RATE if is_day_trade else self.SWING_IRRF_RATE

    def is_day_trade(self, trade: TradeInput) -> bool:
        """
        Classify if trade is day trade.

        Day Trade: Buy and sell same asset on same trading day.
        For MVP, using simple date comparison. In production, need trading day logic.
        """
        # TODO: Implement trading day classification
        # For now, assume manually classified or based on same-day rule
        return False  # Default to swing trade unless explicitly marked

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        """
        Calculate complete tax and fee result for a stock trade.

        Args:
            trade: The trade input
            average_price: Weighted average price (for sells)

        Returns:
            Complete calculation result with all taxes and fees
        """
        # Validate trade
        assert trade.tipo_ativo == AssetType.ACAO, "This calculator is for Ações only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles sales"

        # Calculate basic metrics
        valor_financeiro = trade.quantidade * trade.preco_unitario
        pm = average_price or trade.preco_unitario  # Use average price if provided
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, pm, trade.preco_unitario)

        # Classify operation type
        is_day_trade = self.is_day_trade(trade)
        tipo_operacao = TradeOperationType.DAY_TRADE if is_day_trade else TradeOperationType.SWING

        # Calculate fees
        fees = calculate_b3_fees(valor_financeiro, AssetType.ACAO, trade)

        # Determine tax rate
        aliquota = self.get_tax_rate(is_day_trade)
        isenção_aplicada = False

        # Apply exemption if applicable (swing trade only, must be < R$20,000)
        if not is_day_trade and valor_financeiro < self.EXEMPTION_LIMIT:
            aliquota = 0.0
            isenção_aplicada = True

        # Calculate IR
        ir_devido = max(0, ganho_bruto) * aliquota
        irrf_retido = valor_financeiro * self.get_irrf_rate(is_day_trade)

        # Calculate net values
        ganho_liquido = ganho_bruto - fees.total
        valor_liquido = valor_financeiro - fees.total - ir_devido - irrf_retido

        # Prepare result
        result = TaxCalculationResult(
            ativo=trade.ativo,
            tipo_ativo=trade.tipo_ativo,
            quantidade=trade.quantidade,
            preco_unitario=trade.preco_unitario,
            data_operacao=trade.data_operacao,
            valor_financeiro=valor_financeiro,
            ganho_prejuizo_bruto=ganho_bruto,
            taxas_totais=fees,
            aliquota_aplicada=aliquota,
            ir_devido=ir_devido,
            irrf_retido=irrf_retido,
            isenção_aplicada=isenção_aplicada,
            ganho_prejuizo_liquido=ganho_liquido,
            valor_liquido=valor_liquido,
            tipo_operacao_classificacao=tipo_operacao,
            mensagem=self._generate_message(
                trade, ganho_bruto, ir_devido, isenção_aplicada, is_day_trade
            ),
        )

        return result

    def _generate_message(
        self,
        trade: TradeInput,
        ganho_bruto: float,
        ir_devido: float,
        isenção: bool,
        day_trade: bool,
    ) -> str:
        """Generate user-friendly summary message."""
        tipo = "day trade" if day_trade else "swing trade"
        ganho_str = f"R$ {ganho_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        msg = f"Operação {tipo} de {trade.ativo}: {ganho_str}"

        if isenção:
            msg += " (isenção de R$ 20.000 aplicada)"
        elif ir_devido > 0:
            ir_str = f"R$ {ir_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            msg += f" - IR devido: {ir_str}"

        return msg
