"""
Unit tests for Opções de Ações (stock options) calculations.

Key rules tested:
- Gain = (sale_price - premium_paid) * quantity
- 15% swing / 20% day trade (mirrors underlying stock)
- IRRF: 0,005% swing / 1% day trade
- Exemption R$20,000 applies (tracked at monthly portfolio level)
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.equity.opcoes import OpcoesCalculator


class TestOpcoesCalculator:

    @pytest.fixture
    def calculator(self):
        return OpcoesCalculator()

    def test_gain_calculated_from_premium(self, calculator):
        """
        Gain = (sale_price - premium_paid) * quantity.

        Scenario: Bought call at R$2.00 premium, sold at R$5.00.
        Gain = (5.00 - 2.00) * 100 = R$300
        """
        trade = TradeInput(
            ativo="PETRH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=5.00,  # Current sale price
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=2.00)  # Premium paid

        assert result.ganho_prejuizo_bruto == pytest.approx(300.0)  # (5-2)*100

    def test_swing_trade_15_percent(self, calculator):
        """Options swing trade: 15% rate (same as underlying stock)."""
        trade = TradeInput(
            ativo="PETRH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=5.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=2.00)

        assert result.aliquota_aplicada == 0.15
        assert result.ir_devido == pytest.approx(45.0)  # 300 * 15%

    def test_day_trade_20_percent(self, calculator):
        """Options day trade: 20% rate, no exemption."""
        trade = TradeInput(
            ativo="ITUBH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=200,
            preco_unitario=3.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=1.50)

        assert result.aliquota_aplicada == 0.20
        assert result.ganho_prejuizo_bruto == pytest.approx(300.0)  # (3-1.5)*200
        assert result.ir_devido == pytest.approx(60.0)  # 300 * 20%

    def test_option_expiring_worthless_is_a_loss(self, calculator):
        """
        Option expires worthless: sale_price = 0, loss = full premium paid.

        Scenario: Paid R$2.00 premium, option expires at R$0.
        Loss = (0 - 2.00) * 100 = -R$200
        """
        trade = TradeInput(
            ativo="PETRH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=0.01,  # Near-zero expiry value
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=2.00)

        assert result.ganho_prejuizo_bruto < 0
        assert result.ir_devido == 0.0  # No IR on losses

    def test_loss_not_taxed(self, calculator):
        """Losses on options produce zero IR."""
        trade = TradeInput(
            ativo="VALEG250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=1.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=3.00)

        assert result.ganho_prejuizo_bruto == pytest.approx(-200.0)
        assert result.ir_devido == 0.0

    def test_irrf_swing_trade(self, calculator):
        """IRRF swing trade: 0,005% of financial value (not of gain)."""
        trade = TradeInput(
            ativo="PETRH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=5.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=2.00)

        expected_irrf = 500.0 * 0.00005  # 0,005% of R$500 financial value
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_irrf_day_trade(self, calculator):
        """IRRF day trade: 1% of financial value."""
        trade = TradeInput(
            ativo="PETRH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=5.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=2.00)

        expected_irrf = 500.0 * 0.01  # 1% of R$500 financial value
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_wrong_asset_type_raises(self, calculator):
        """Calculator rejects non-option asset types."""
        trade = TradeInput(
            ativo="PETR4",
            tipo_ativo=AssetType.ACAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=25.00,
            data_operacao=date(2025, 3, 15),
        )

        with pytest.raises(AssertionError):
            calculator.calculate_result(trade, average_price=20.00)

    def test_valor_liquido_deducts_all_costs(self, calculator):
        """Net value correctly deducts fees, IR, and IRRF."""
        trade = TradeInput(
            ativo="PETRH250",
            tipo_ativo=AssetType.OPCAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=5.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=2.00)

        expected = (
            result.valor_financeiro
            - result.taxas_totais.total
            - result.ir_devido
            - result.irrf_retido
        )
        assert result.valor_liquido == pytest.approx(expected, rel=1e-5)
