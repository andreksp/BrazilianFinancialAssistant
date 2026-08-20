"""
Unit tests for Futuros (Futuro de Dólar / Futuro de Índice) calculations.

Key rules tested:
- 15% normal / 20% day trade — same structure as Ações
- NO R$20,000 exemption (unlike Ações swing trade)
- IRRF: 0,005% normal / 1% day trade
- Both WDO and WIN are handled by the same calculator
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.derivatives.futuros import FuturosCalculator


class TestFuturosCalculator:

    @pytest.fixture
    def calculator(self):
        return FuturosCalculator()

    def test_normal_operation_15_percent(self, calculator):
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=2,
            preco_unitario=5280.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=5230.00)

        assert result.aliquota_aplicada == 0.15
        assert result.ganho_prejuizo_bruto == pytest.approx(100.0)  # (5280-5230)*2
        assert result.ir_devido == pytest.approx(15.0)  # 100 * 15%

    def test_day_trade_20_percent(self, calculator):
        trade = TradeInput(
            ativo="WIN",
            tipo_ativo=AssetType.FUTURO_INDICE,
            tipo_operacao=OperationType.VENDA,
            quantidade=5,
            preco_unitario=130000.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=129800.00)

        assert result.aliquota_aplicada == 0.20
        assert result.ganho_prejuizo_bruto == pytest.approx(1000.0)  # (130000-129800)*5
        assert result.ir_devido == pytest.approx(200.0)  # 1000 * 20%

    def test_no_exemption_ever_applied(self, calculator):
        """Futuros never receive the R$20,000 exemption, even on small gains."""
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=1,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        assert result.isenção_aplicada is False
        assert result.ir_devido > 0

    def test_loss_not_taxed(self, calculator):
        trade = TradeInput(
            ativo="WIN",
            tipo_ativo=AssetType.FUTURO_INDICE,
            tipo_operacao=OperationType.VENDA,
            quantidade=1,
            preco_unitario=129000.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=130000.00)

        assert result.ganho_prejuizo_bruto == pytest.approx(-1000.0)
        assert result.ir_devido == 0.0

    def test_irrf_normal_operation(self, calculator):
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=10,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        expected_irrf = 1000.0 * 0.00005  # 0,005% of R$1,000
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_irrf_day_trade(self, calculator):
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=10,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=90.00)

        expected_irrf = 1000.0 * 0.01  # 1% of R$1,000
        assert result.irrf_retido == pytest.approx(expected_irrf, rel=1e-5)

    def test_wrong_asset_type_raises(self, calculator):
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
        trade = TradeInput(
            ativo="WIN",
            tipo_ativo=AssetType.FUTURO_INDICE,
            tipo_operacao=OperationType.VENDA,
            quantidade=3,
            preco_unitario=130000.00,
            data_operacao=date(2025, 3, 15),
        )

        result = calculator.calculate_result(trade, average_price=129500.00)

        expected = (
            result.valor_financeiro
            - result.taxas_totais.total
            - result.ir_devido
            - result.irrf_retido
        )
        assert result.valor_liquido == pytest.approx(expected, rel=1e-5)
