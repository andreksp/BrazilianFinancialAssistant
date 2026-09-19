"""
Unit tests for BDR (Brazilian Depositary Receipts) calculations.

BDRs do not receive the stock-sales exemption:
- Swing trade: 15% IR, no R$20,000 exemption
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
        """BDR common-operation gains are taxed at 15%."""
        trade = TradeInput(
            ativo="AMZO34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=50,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
            total_vendas_mes=25000.0,
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        assert result.aliquota_aplicada == 0.15
        assert result.ganho_prejuizo_bruto == 500.0  # (100 - 90) * 50
        assert result.ir_devido == pytest.approx(75.0, abs=0.5)  # 500 * 15%, minus tiny B3 fees
        assert result.isenção_aplicada == False

    def test_swing_trade_below_stock_exemption_is_taxed(self, calculator):
        """The R$20,000 stock exemption never applies to a BDR sale."""
        trade = TradeInput(
            ativo="AMZO34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=50,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
            total_vendas_mes=5000.0,
            custos_operacao=0.0,
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        assert result.isenção_aplicada is False
        assert result.aliquota_aplicada == 0.15
        assert result.ir_devido == 75.0

    @pytest.mark.parametrize("monthly_sales", [None, 2000.0, 20000.0, 20001.0])
    def test_regression_bdr_no_monthly_exemption(self, calculator, monthly_sales):
        trade = TradeInput(
            ativo="AAPL34", tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA, quantidade=10,
            preco_unitario=200, data_operacao=date(2026, 9, 13),
            total_vendas_mes=monthly_sales, custos_operacao=0, irrf_informado=0,
        )
        result = calculator.calculate_result(trade, average_price=100)
        assert result.ganho_prejuizo_bruto == 1000
        assert result.ir_devido == 150
        assert result.aliquota_aplicada == 0.15
        assert result.isenção_aplicada is False
        assert "isenção de R$ 20.000 aplicada" not in result.mensagem

    def test_missing_average_price_is_rejected(self, calculator):
        trade = TradeInput(
            ativo="AAPL34", tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA, quantidade=10,
            preco_unitario=200, data_operacao=date(2026, 9, 13),
        )
        with pytest.raises(ValueError, match="custo médio"):
            calculator.calculate_result(trade)

    def test_explicit_costs_reduce_bdr_tax_base(self, calculator):
        trade = TradeInput(
            ativo="AAPL34", tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA, quantidade=10,
            preco_unitario=200, data_operacao=date(2026, 9, 13),
            custos_operacao=100, irrf_informado=0,
        )
        result = calculator.calculate_result(trade, average_price=100)
        assert result.taxas_totais.total == 100
        assert result.ir_devido == 135
        assert result.isenção_aplicada is False

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
        assert result.ir_devido == pytest.approx(100.0, abs=0.5)  # 500 * 20%, minus tiny B3 fees
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
            total_vendas_mes=4000.0,
        )

        result = calculator.calculate_result(trade, average_price=45.00)

        assert result.ganho_prejuizo_bruto == -500.0
        assert result.ir_devido == 0.0

    def test_irrf_swing_trade(self, calculator):
        """IRRF is no longer estimated — it echoes trade.irrf_informado (nota real)."""
        trade = TradeInput(
            ativo="AMZO34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=50.00,
            data_operacao=date(2025, 3, 15),
            total_vendas_mes=5000.0,
            irrf_informado=0.25,
        )

        result = calculator.calculate_result(trade, average_price=45.00)

        assert result.irrf_retido == pytest.approx(0.25, rel=1e-5)

    def test_irrf_day_trade(self, calculator):
        """Day trade IRRF also echoes trade.irrf_informado."""
        trade = TradeInput(
            ativo="GOGL34",
            tipo_ativo=AssetType.BDR,
            tipo_operacao=OperationType.VENDA,
            quantidade=100,
            preco_unitario=50.00,
            data_operacao=date(2025, 3, 15),
            irrf_informado=50.00,
        )

        calculator.is_day_trade = lambda t: True
        result = calculator.calculate_result(trade, average_price=45.00)

        assert result.irrf_retido == pytest.approx(50.00, rel=1e-5)

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
            total_vendas_mes=5000.0,
        )

        result = calculator.calculate_result(trade, average_price=45.00)

        # irrf_retido is a credit against ir_devido, not an extra deduction —
        # only the larger of the two is subtracted (matches AcoesCalculator).
        expected = (
            result.valor_financeiro
            - result.taxas_totais.total
            - max(result.ir_devido, result.irrf_retido)
        )
        assert result.valor_liquido == pytest.approx(expected, rel=1e-5)
