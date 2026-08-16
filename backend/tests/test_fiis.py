"""
Unit tests for FII (Fundo de Investimento Imobiliário) calculations.

Key rules tested:
- 20% flat rate (no 15% swing trade rate)
- NO R$20,000 exemption (unlike Ações)
- Losses produce zero IR (loss tracking handled at portfolio level)
- IRRF: 0,005% swing / 1% day trade
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.equity.fiis import FIICalculator


class TestFIICalculator:

    @pytest.fixture
    def calculator(self):
        return FIICalculator()

    def test_swing_trade_always_20_percent(self, calculator):
        """
        FII swing trade uses 20% — NOT the 15% that applies to Ações.

        This is the most critical distinction for FIIs.
        """
        trade = TradeInput(
            ativo="HGLG11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=150.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=130.00)

        assert result.aliquota_aplicada == 0.20  # Always 20%, not 15%
        assert result.ganho_prejuizo_bruto == 2000.0  # (150 - 130) * 100
        assert result.ir_devido == pytest.approx(400.0)  # 2000 * 20%

    def test_day_trade_also_20_percent(self, calculator):
        """Day trade rate is 20% — same as swing trade for FIIs."""
        trade = TradeInput(
            ativo="XPML11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=50,
            preco_unitario=110.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=100.00)

        assert result.aliquota_aplicada == 0.20
        assert result.ir_devido == pytest.approx(100.0)  # (110-100)*50 * 20%

    def test_no_exemption_applied(self, calculator):
        """
        FIIs never receive the R$20,000 exemption.
        Even when financial value is below R$20,000, isenção is False.
        """
        trade = TradeInput(
            ativo="HGLG11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=10,
            preco_unitario=150.00,  # R$1,500 total — well below R$20,000
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=100.00)

        assert result.isenção_aplicada == False
        assert result.ir_devido > 0  # IR is charged even on small amounts

    def test_loss_not_taxed(self, calculator):
        """Losses produce zero IR for FIIs (no loss carryover)."""
        trade = TradeInput(
            ativo="KNRI11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=90.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=100.00)

        assert result.ganho_prejuizo_bruto == -1000.0
        assert result.ir_devido == 0.0

    def test_irrf_swing_trade(self, calculator):
        """IRRF swing trade: 0,005% of financial value."""
        trade = TradeInput(
            ativo="HGLG11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=150.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=130.00)

        expected_irrf = 15000.0 * 0.00005  # 0,005% of R$15,000
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_irrf_day_trade(self, calculator):
        """IRRF day trade: 1% of financial value."""
        trade = TradeInput(
            ativo="HGLG11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=150.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=130.00)

        expected_irrf = 15000.0 * 0.01  # 1% of R$15,000
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_wrong_asset_type_raises(self, calculator):
        """Calculator rejects non-FII asset types."""
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
            ativo="HGLG11",
            tipo_ativo=AssetType.FII,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=150.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=130.00)

        expected = (
            result.valor_financeiro
            - result.taxas_totais.total
            - result.ir_devido
            - result.irrf_retido
        )
        assert result.valor_liquido == pytest.approx(expected, rel=1e-5)
