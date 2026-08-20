"""
Calculation module for Futuros (listed futures) — Dólar (WDO) e Índice (WIN).

Business Logic Reference: Documentation/plan.md Phase 2, backend/data/regulations/ir_futuros.txt
- Alíquota: 15% (operação normal) ou 20% (day trade) sobre o ganho líquido — Lei 11.033/2004 art. 2
- SEM isenção de R$20.000/mês — essa isenção vale só para venda de ações à vista
- IRRF: 0,005% (normal) ou 1% (day trade), DARF código 6015
- Base legal: Instrução Normativa RFB 1.585/2015

MVP SIMPLIFICATION: o motor de cálculo do projeto trabalha por operação (preço médio de
abertura vs. preço de fechamento), não pelo ajuste diário real (marcação a mercado D+1) do
mercado futuro. O usuário informa o preço de abertura (compra) e de fechamento (venda) da
posição e o resultado é tratado como o ganho agregado dessa operação — não a mecânica real
de liquidação diária de ajustes.
"""

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

_SUPPORTED = (AssetType.FUTURO_DOLAR, AssetType.FUTURO_INDICE)


class FuturosCalculator(BaseCalculator):
    """
    Calculator for listed futures (Futuro de Dólar / Futuro de Índice).

    Same alíquota structure as Ações, but without the R$20.000 monthly exemption.
    """

    NORMAL_RATE = 0.15  # 15%
    DAY_TRADE_RATE = 0.20  # 20%
    NORMAL_IRRF_RATE = 0.00005  # 0,005%
    DAY_IRRF_RATE = 0.01  # 1%

    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        """Ganho = (preço de fechamento - preço de abertura) × quantidade de contratos."""
        return (sale_price - purchase_price) * quantity

    def get_tax_rate(self, is_day_trade: bool = False) -> float:
        return self.DAY_TRADE_RATE if is_day_trade else self.NORMAL_RATE

    def get_irrf_rate(self, is_day_trade: bool = False) -> float:
        return self.DAY_IRRF_RATE if is_day_trade else self.NORMAL_IRRF_RATE

    def is_day_trade(self, trade: TradeInput) -> bool:
        """Same MVP limitation as AcoesCalculator: no automatic same-day detection yet."""
        return False

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        assert trade.tipo_ativo in _SUPPORTED, "This calculator is for Futuros only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles position closes"

        valor_financeiro = trade.quantidade * trade.preco_unitario
        pm = average_price or trade.preco_unitario
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, pm, trade.preco_unitario)

        is_day_trade = self.is_day_trade(trade)
        tipo_operacao = TradeOperationType.DAY_TRADE if is_day_trade else TradeOperationType.SWING

        fees = calculate_b3_fees(valor_financeiro, trade.tipo_ativo, trade)

        aliquota = self.get_tax_rate(is_day_trade)
        # Futuros não têm isenção de R$20.000 — sempre tributado
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
            isenção_aplicada=False,
            ganho_prejuizo_liquido=ganho_liquido,
            valor_liquido=valor_liquido,
            tipo_operacao_classificacao=tipo_operacao,
            mensagem=self._generate_message(trade, ganho_bruto, ir_devido, is_day_trade),
        )

    def _generate_message(
        self, trade: TradeInput, ganho_bruto: float, ir_devido: float, day_trade: bool
    ) -> str:
        tipo = "day trade" if day_trade else "operação normal"
        ganho_str = f"R$ {ganho_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ir_str = f"R$ {ir_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return (
            f"Operação {tipo} de {trade.ativo}: {ganho_str} "
            f"- IR devido: {ir_str} (sem isenção de R$20.000, aplicável apenas a ações à vista)"
        )
