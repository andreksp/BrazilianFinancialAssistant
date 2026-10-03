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

_SUPPORTED = (AssetType.FUTURO_DOLAR, AssetType.FUTURO_INDICE)


def _fees_from_custos(custos_operacao: float) -> FeesBreakdown:
    """
    Custos reais informados pelo usuário (nota de corretagem) substituem a
    estimativa B3 — ver TradeInput.custos_operacao. Todo o valor é registrado
    em `corretagem` apenas para preencher o breakdown; o total é o que importa.
    """
    return FeesBreakdown(
        taxa_liquidacao=0.0,
        taxa_registro=0.0,
        emolumentos=0.0,
        corretagem=custos_operacao,
        iss_sobre_corretagem=0.0,
    )


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
        return trade.classificacao == TradeOperationType.DAY_TRADE

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        assert trade.tipo_ativo in _SUPPORTED, "This calculator is for Futuros only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles position closes"

        prefix = 'WDO' if trade.tipo_ativo == AssetType.FUTURO_DOLAR else 'WIN'
        if not trade.ativo.upper().startswith(prefix):
            raise ValueError("Somente minicontratos WIN e WDO são suportados nesta simulação.")
        if average_price is None:
            raise ValueError("Informe a cotação de abertura da posição comprada.")
        if trade.custos_operacao is None:
            raise ValueError("Informe custos da operação, inclusive zero quando aplicável.")
        multiplier = 10.0 if prefix == 'WDO' else 0.20
        valor_financeiro = trade.quantidade * trade.preco_unitario * multiplier
        pm = average_price
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, pm, trade.preco_unitario) * multiplier

        is_day_trade = self.is_day_trade(trade)
        tipo_operacao = TradeOperationType.DAY_TRADE if is_day_trade else TradeOperationType.SWING

        fees = _fees_from_custos(trade.custos_operacao)

        aliquota = self.get_tax_rate(is_day_trade)
        # Futuros não têm isenção de R$20.000 — sempre tributado
        ir_devido = round(max(0, ganho_bruto - fees.total) * aliquota, 2)
        irrf_nao_informado = trade.irrf_informado is None
        # Zero is only the numeric placeholder: expose unknown status explicitly.
        irrf_retido = trade.irrf_informado if not irrf_nao_informado else 0.0
        warning = (
            " IRRF não informado: retenção desconhecida, sem crédito de IRRF considerado."
            " O zero no campo numérico não confirma ausência de retenção."
            " Resultado estimado antes da conciliação do IRRF, não é DARF mensal definitivo."
        ) if irrf_nao_informado else ""

        ganho_liquido = ganho_bruto - fees.total
        valor_liquido = ganho_liquido - max(ir_devido, irrf_retido)

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
            irrf_nao_informado=irrf_nao_informado,
            isenção_aplicada=False,
            ganho_prejuizo_liquido=ganho_liquido,
            valor_liquido=valor_liquido,
            tipo_operacao_classificacao=tipo_operacao,
            mensagem=self._generate_message(trade, ganho_bruto, ir_devido, is_day_trade) + " Simulação de posição comprada encerrada, sem ajustes diários intermediários ou compensação mensal; valor financeiro é nocional, não recebimento." + warning,
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
