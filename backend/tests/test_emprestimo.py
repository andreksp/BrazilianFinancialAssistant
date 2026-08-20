"""
Unit tests for Empréstimo de Ações (securities lending, doador side) calculations.

Key rules tested:
- Taxed as renda fixa via regressive table by contract term (NOT the 15%/20% ações rules)
- IR is withheld at source and is definitive (ir_devido == 0, all tax is in irrf_retido)
- Missing prazo_dias defaults to the most conservative bracket (22,5%)
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.lending.emprestimo import EmprestimoCalculator, DEFAULT_PRAZO_DIAS


class TestEmprestimoCalculator:

    @pytest.fixture
    def calculator(self):
        return EmprestimoCalculator()

    def test_bracket_up_to_180_days(self, calculator):
        trade = TradeInput(
            ativo="VALE3",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=200,
            preco_unitario=0.50,
            data_operacao=date(2025, 3, 15),
            prazo_dias=90,
        )

        result = calculator.calculate_result(trade)

        assert result.aliquota_aplicada == 0.225
        assert result.valor_financeiro == pytest.approx(100.0)  # 200 * 0.50
        assert result.irrf_retido == pytest.approx(22.5)  # 100 * 22.5%
        assert result.ir_devido == 0.0  # tributação exclusiva na fonte

    def test_bracket_181_to_360_days(self, calculator):
        trade = TradeInput(
            ativo="PETR4",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=1.00,
            data_operacao=date(2025, 3, 15),
            prazo_dias=300,
        )

        result = calculator.calculate_result(trade)

        assert result.aliquota_aplicada == 0.20
        assert result.irrf_retido == pytest.approx(20.0)  # 100 * 20%

    def test_bracket_361_to_720_days(self, calculator):
        trade = TradeInput(
            ativo="ITUB4",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=1.00,
            data_operacao=date(2025, 3, 15),
            prazo_dias=500,
        )

        result = calculator.calculate_result(trade)
        assert result.aliquota_aplicada == 0.175

    def test_bracket_above_720_days(self, calculator):
        trade = TradeInput(
            ativo="BBDC4",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=1.00,
            data_operacao=date(2025, 3, 15),
            prazo_dias=800,
        )

        result = calculator.calculate_result(trade)
        assert result.aliquota_aplicada == 0.15

    def test_missing_prazo_defaults_to_conservative_bracket(self, calculator):
        trade = TradeInput(
            ativo="VALE3",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=1.00,
            data_operacao=date(2025, 3, 15),
        )

        assert trade.prazo_dias is None
        result = calculator.calculate_result(trade)

        assert DEFAULT_PRAZO_DIAS == 180
        assert result.aliquota_aplicada == 0.225
        assert "não informado" in result.mensagem

    def test_no_fees_charged(self, calculator):
        """Empréstimo de ações doesn't go through the standard B3 trading fee schedule."""
        trade = TradeInput(
            ativo="VALE3",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=1.00,
            data_operacao=date(2025, 3, 15),
            prazo_dias=90,
        )

        result = calculator.calculate_result(trade)
        assert result.taxas_totais.total == 0.0

    def test_valor_liquido_equals_gross_minus_irrf(self, calculator):
        trade = TradeInput(
            ativo="VALE3",
            tipo_ativo=AssetType.EMPRESTIMO_ACOES,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=2.00,
            data_operacao=date(2025, 3, 15),
            prazo_dias=90,
        )

        result = calculator.calculate_result(trade)

        assert result.valor_liquido == pytest.approx(
            result.valor_financeiro - result.irrf_retido, rel=1e-5
        )

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
            calculator.calculate_result(trade)
