"""
Calculation module for Opções de Ações (Stock Options) - Phase 1.

Business rules:
- Gain/Loss: (sale_price - premium_paid) × quantity
  where `average_price` parameter = premium paid per option
- Tax: 15% swing trade, 20% day trade (same as underlying stock)
- IRRF: 0,005% swing, 1% day trade
- Exemption R$20,000: applies (options count toward monthly total)
  — tracked at monthly portfolio level, same as Ações

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


class OpcoesCalculator(BaseCalculator):
    """
    Calculator for Opções de Ações (stock options) trades.

    Tax Rules:
    - Alíquota: 15% swing / 20% day trade (mirrors underlying stock rules)
    - Isenção: R$20,000/month applies (tracked at portfolio level)
    - Gain = (exercise/sale price - premium paid) * quantity
    - IRRF: 0,005% swing / 1% day trade
    """

    SWING_TRADE_RATE = 0.15
    DAY_TRADE_RATE = 0.20
    SWING_IRRF_RATE = 0.00005  # 0,005%
    DAY_IRRF_RATE = 0.01       # 1%

    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        """
        Calculate option gain or loss.

        Args:
            quantity: Number of option contracts
            purchase_price: Premium paid per option (average cost)
            sale_price: Current sale/exercise price per option
        """
        return (sale_price - purchase_price) * quantity

    def get_tax_rate(self, is_day_trade: bool = False) -> float:
        return self.DAY_TRADE_RATE if is_day_trade else self.SWING_TRADE_RATE

    def get_irrf_rate(self, is_day_trade: bool = False) -> float:
        return self.DAY_IRRF_RATE if is_day_trade else self.SWING_IRRF_RATE

    def is_day_trade(self, trade: TradeInput) -> bool:
        return False  # Default to swing; override for day trade classification

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        """
        Calculate complete tax and fee result for an options trade.

        Args:
            trade: The trade input (preco_unitario = current sale/exercise price)
            average_price: Premium paid per option (cost basis). Defaults to preco_unitario
                           if not provided (zero gain scenario).
        """
        assert trade.tipo_ativo == AssetType.OPCAO, "This calculator is for Opções only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles sales/exercise"

        valor_financeiro = trade.quantidade * trade.preco_unitario
        premium_pago = average_price or trade.preco_unitario
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, premium_pago, trade.preco_unitario)

        is_day_trade = self.is_day_trade(trade)
        tipo_operacao = TradeOperationType.DAY_TRADE if is_day_trade else TradeOperationType.SWING

        fees = calculate_b3_fees(valor_financeiro, AssetType.OPCAO, trade)

        aliquota = self.get_tax_rate(is_day_trade)
        isenção_aplicada = False

        # Exemption R$20,000 tracked at monthly portfolio level
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

    def _generate_message(
        self,
        trade: TradeInput,
        ganho_bruto: float,
        ir_devido: float,
        isenção: bool,
        day_trade: bool,
    ) -> str:
        tipo = "day trade" if day_trade else "swing trade"
        ganho_str = f"R$ {ganho_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        msg = f"Opção {tipo} de {trade.ativo}: {ganho_str}"
        if isenção:
            msg += " (isenção de R$ 20.000 aplicada)"
        elif ir_devido > 0:
            ir_str = f"R$ {ir_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            msg += f" - IR devido: {ir_str}"
        return msg
