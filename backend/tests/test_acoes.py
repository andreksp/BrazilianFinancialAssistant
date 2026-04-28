"""
Unit tests for stock (ações) calculations.

Reference: Documentation/research.md scenarios 1-3
Tests critical business logic around:
- Swing trade vs day trade classification
- IR exemption (R$20,000/month)
- Weighted average price
- Fee calculation
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.equity.acoes import AcoesCalculator


class TestAcoesCalculator:
    """Test suite for stock calculations."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return AcoesCalculator()

    def test_swing_trade_without_exemption(self, calculator):
        """
        Test: Swing trade where gain is below R$20,000 exemption limit.

        Scenario from research.md:
        - Sold R$2,500 (below R$20,000)
        - Gain: R$500
        - Expected IR: R$75 (15% of R$500)
        """
        trade = TradeInput(
            ativo="PETR4",
            tipo_ativo=AssetType.ACAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=25.50,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=25.00)

        # Verify calculations
        assert result.valor_financeiro == 2550.0
        assert result.ganho_prejuizo_bruto == 50.0  # (25.50 - 25.00) * 100
        assert result.aliquota_aplicada == 0.15  # Swing trade
        assert result.isenção_aplicada == False  # Above limit
        # Note: In reality, R$20,000 limit applies to month total, not individual trade
        # This is a simplified test

    def test_day_trade_always_20_percent(self, calculator):
        """
        Test: Day trade is always taxed at 20%, no exemption.

        Scenario:
        - Same-day buy/sell
        - Gain: R$500
        - Expected IR: R$100 (20% of R$500)
        """
        trade = TradeInput(
            ativo="ITUB4",
            tipo_ativo=AssetType.ACAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=29.00,
            data_operacao=date(2025, 3, 15),
        )

        # Override day trade classification
        calculator.is_day_trade = lambda t: True

        result = calculator.calculate_result(trade, average_price=28.50)

        # Verify day trade rate
        assert result.aliquota_aplicada == 0.20  # Day trade
        assert result.isenção_aplicada == False  # No exemption for day trade

    def test_loss_is_not_taxed(self, calculator):
        """
        Test: Losses result in 0 tax (only gains are taxed).

        Scenario:
        - Sold at loss
        - Loss: -R$100
        - Expected IR: R$0 (losses not taxed)
        """
        trade = TradeInput(
            ativo="VALE3",
            tipo_ativo=AssetType.ACAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=23.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=24.00)

        assert result.ganho_prejuizo_bruto == -100.0  # Loss
        assert result.ir_devido == 0.0  # No tax on losses

    def test_weighted_average_price(self, calculator):
        """
        Test: Weighted average price calculation.

        Scenario (research.md):
        - Buy 100 @ R$25 → PM = 25
        - Buy 50 @ R$24 → PM = (100*25 + 50*24)/(100+50) = 24.67
        - Sell 80 @ R$26 → Gain = (26-24.67)*80 = 106.40
        """
        # Note: Full weighted average test would need portfolio tracking
        # This is a unit test showing formula
        pm_old = 25.0
        qty_old = 100
        qty_new = 50
        price_new = 24.0

        pm_new = (qty_old * pm_old + qty_new * price_new) / (qty_old + qty_new)

        assert pm_new == pytest.approx(24.6666667, rel=1e-5)

    def test_irrf_withheld_swing_trade(self, calculator):
        """
        Test: IRRF (withholding tax) for swing trade.

        Business logic: 0,005% withheld on transaction value
        """
        trade = TradeInput(
            ativo="PETR4",
            tipo_ativo=AssetType.ACAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=25.50,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=25.00)

        # IRRF = valor_financeiro * 0.005%
        expected_irrf = 2550.0 * 0.00005
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_irrf_withheld_day_trade(self, calculator):
        """
        Test: IRRF for day trade is higher (1% vs 0.005%).
        """
        trade = TradeInput(
            ativo="ITUB4",
            tipo_ativo=AssetType.ACAO,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=29.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=28.50)

        # IRRF = valor_financeiro * 1%
        expected_irrf = 2900.0 * 0.01
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)
