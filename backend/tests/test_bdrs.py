"""
Unit tests for BDR (Brazilian Depositary Receipts) calculations.

BDRs follow the same tax rules as Ações:
- Swing trade: 15% IR, R$20,000 exemption (monthly, tracked at portfolio level)
- Day trade: 20% IR, no exemption
- IRRF: 0,005% swing / 1% day trade
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.equity.bdrs import BDRCalculator


class TestBDRCalculator:

    @pytest.fixture
    def calculator(self):
        return BDRCalculator()

    def test_swing_trade_15_percent(self, calculator):
        """BDR swing trade applies 15% rate like Ações."""
        trade = TradeInput(
            ativo="AMZO34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=50,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        assert result.aliquota_aplicada == 0.15
        assert result.ganho_prejuizo_bruto == 500.0  # (100 - 90) * 50
        assert result.ir_devido == pytest.approx(75.0)  # 500 * 15%
        assert result.isenção_aplicada == False

    def test_day_trade_20_percent(self, calculator):
        """BDR day trade applies 20% — same as Ações, no exemption."""
        trade = TradeInput(
            ativo="GOGL34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=55.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=50.00)

        assert result.aliquota_aplicada == 0.20
        assert result.ganho_prejuizo_bruto == 500.0  # (55 - 50) * 100
        assert result.ir_devido == pytest.approx(100.0)  # 500 * 20%
        assert result.isenção_aplicada == False

    def test_loss_not_taxed(self, calculator):
        """Losses produce zero IR."""
        trade = TradeInput(
            ativo="MSFT34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=40.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=45.00)

        assert result.ganho_prejuizo_bruto == -500.0
        assert result.ir_devido == 0.0

    def test_irrf_swing_trade(self, calculator):
        """IRRF for swing trade: 0,005% of financial value."""
        trade = TradeInput(
            ativo="AMZO34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=50.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=45.00)

        expected_irrf = 5000.0 * 0.00005  # 0,005% of R$5,000
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_irrf_day_trade(self, calculator):
        """IRRF for day trade: 1% of financial value."""
        trade = TradeInput(
            ativo="GOGL34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=50.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=45.00)

        expected_irrf = 5000.0 * 0.01  # 1% of R$5,000
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_wrong_asset_type_raises(self, calculator):
        """Calculator rejects non-BDR asset types."""
        trade = TradeInput(
            ativo="PETR4",
            tipo_ativo=AssetType.ACAO,  # Wrong type
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
            ativo="AMZO34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=50.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=45.00)

        expected = (
            result.valor_financeiro
            - result.taxas_totais.total
            - result.ir_devido
            - result.irrf_retido
        )
        assert result.valor_liquido == pytest.approx(expected, rel=1e-5)
