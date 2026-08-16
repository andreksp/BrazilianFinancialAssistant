"""
Calculation module for FIIs (Fundos Imobiliários) - Phase 1.

Key differences from Ações:
- Alíquota: 20% flat (swing AND day trade — no 15% rate)
- Sem isenção: R$20,000 exemption does NOT apply to FIIs
- Sem compensação: losses cannot be carried to next month

Reference: Documentation/research.md
"""

from typing import Optional

from app.models.trade import (
    TradeInput,
    TradeOperationType,
    TaxCalculationResult,
    AssetType,
)
from app.calculations.base import BaseCalculator
from app.calculations.fees.b3_fees import calculate_b3_fees


class FIICalculator(BaseCalculator):
    """
    Calculator for FII (Real Estate Investment Trust) trades.

    Tax Rules:
    - Alíquota: 20% (both swing and day trade)
    - Isenção: NONE (R$20,000 exemption does not apply)
    - Loss compensation: NOT allowed between months
    - IRRF: 0,005% (swing) or 1% (day trade) — same as stocks
    """

    TAX_RATE = 0.20
    SWING_IRRF_RATE = 0.00005  # 0,005%
    DAY_IRRF_RATE = 0.01       # 1%

    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        return (sale_price - purchase_price) * quantity

    def get_tax_rate(self, is_day_trade: bool = False) -> float:
        """FIIs are always 20% — no reduced rate for swing trade."""
        return self.TAX_RATE

    def get_irrf_rate(self, is_day_trade: bool = False) -> float:
        return self.DAY_IRRF_RATE if is_day_trade else self.SWING_IRRF_RATE

    def is_day_trade(self, trade: TradeInput) -> bool:
        return False  # Default to swing; override for day trade classification

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        assert trade.tipo_ativo == AssetType.FII, "This calculator is for FIIs only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles sales"

        valor_financeiro = trade.quantidade * trade.preco_unitario
        pm = average_price or trade.preco_unitario
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, pm, trade.preco_unitario)

        is_day_trade = self.is_day_trade(trade)
        tipo_operacao = TradeOperationType.DAY_TRADE if is_day_trade else TradeOperationType.SWING

        fees = calculate_b3_fees(valor_financeiro, AssetType.FII, trade)

        aliquota = self.get_tax_rate(is_day_trade)

        # FIIs never get the R$20,000 exemption
        isenção_aplicada = False
        ir_devido = max(0, ganho_bruto) * aliquota
        irrf_retido = valor_financeiro * self.get_irrf_rate(is_day_trade)

        ganho_liquido = ganho_bruto - fees.total
        valor_liquido = valor_financeiro - fees.total - ir_devido - irrf_retido

        return TaxCalculationResult(
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
                trade, ganho_bruto, ir_devido, is_day_trade
            ),
        )

    def _generate_message(
        self,
        trade: TradeInput,
        ganho_bruto: float,
        ir_devido: float,
        day_trade: bool,
    ) -> str:
        tipo = "day trade" if day_trade else "swing trade"
        ganho_str = f"R$ {ganho_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        msg = f"FII {tipo} de {trade.ativo}: {ganho_str}"
        if ir_devido > 0:
            ir_str = f"R$ {ir_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            msg += f" - IR devido: {ir_str} (sem isenção)"
        return msg
