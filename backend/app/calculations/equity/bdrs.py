"""
Calculation module for BDRs (Brazilian Depositary Receipts) - Phase 1.

Tax rules are identical to Ações (stocks):
- Swing trade: 15% IR (with R$20,000/month exemption), 0,005% IRRF
- Day trade: 20% IR (no exemption), 1% IRRF
- Average price: Weighted moving average

Reference: Documentation/research.md
"""

from typing import Optional

from app.models.trade import (
    TradeInput,
    TradeOperationType,
    TaxCalculationResult,
    AssetType,
)
from app.calculations.equity.acoes import AcoesCalculator
from app.calculations.fees.b3_fees import calculate_b3_fees


class BDRCalculator(AcoesCalculator):
    """
    Calculator for BDR trades.

    Tax rules are identical to Ações — only the asset type differs.
    Inherits all rate constants and helper methods from AcoesCalculator.
    """

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        assert trade.tipo_ativo == AssetType.BDR, "This calculator is for BDRs only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles sales"

        valor_financeiro = trade.quantidade * trade.preco_unitario
        pm = average_price or trade.preco_unitario
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, pm, trade.preco_unitario)

        is_day_trade = self.is_day_trade(trade)
        tipo_operacao = TradeOperationType.DAY_TRADE if is_day_trade else TradeOperationType.SWING

        fees = calculate_b3_fees(valor_financeiro, AssetType.BDR, trade)

        aliquota = self.get_tax_rate(is_day_trade)
        isenção_aplicada = False

        # Exemption R$20,000 tracked at monthly portfolio level, not per-trade
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
                trade, ganho_bruto, ir_devido, isenção_aplicada, is_day_trade
            ),
        )
