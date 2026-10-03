"""
Unit tests for Futuros (Futuro de Dólar / Futuro de Índice) calculations.

Key rules tested:
- 15% normal / 20% day trade — same structure as Ações
- NO R$20,000 exemption (unlike Ações swing trade)
- Contract multiplier: WDO = R$10,00/ponto, WIN = R$0,20/ponto (B3) — applied to
  both valor_financeiro and ganho_prejuizo_bruto
- custos_operacao (nota real) replaces the old B3 fee estimate; irrf_informado
  (nota real) replaces the old estimated IRRF rate — both are now required inputs,
  and the system no longer guesses either
- Both WDO and WIN are handled by the same calculator
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType, TradeOperationType
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
            custos_operacao=0.0,
            irrf_informado=0.0,
        )

        result = calculator.calculate_result(trade, average_price=5230.00)

        # WDO: 1 ponto = R$10,00 por contrato
        assert result.aliquota_aplicada == 0.15
        assert result.ganho_prejuizo_bruto == pytest.approx(1000.0)  # (5280-5230)*2*10
        assert result.ir_devido == pytest.approx(150.0)  # 1000 * 15%

    def test_day_trade_20_percent(self, calculator):
        trade = TradeInput(
            ativo="WIN",
            tipo_ativo=AssetType.FUTURO_INDICE,
            tipo_operacao=OperationType.VENDA,
            quantidade=5,
            preco_unitario=130000.00,
            data_operacao=date(2025, 3, 15),
            classificacao=TradeOperationType.DAY_TRADE,
            custos_operacao=0.0,
            irrf_informado=0.0,
        )

        result = calculator.calculate_result(trade, average_price=129800.00)

        # WIN: 1 ponto = R$0,20 por contrato
        assert result.aliquota_aplicada == 0.20
        assert result.ganho_prejuizo_bruto == pytest.approx(200.0)  # (130000-129800)*5*0.20
        assert result.ir_devido == pytest.approx(40.0)  # 200 * 20%

    def test_no_exemption_ever_applied(self, calculator):
        """Futuros never receive the R$20,000 exemption, even on small gains."""
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=1,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
            custos_operacao=0.0,
            irrf_informado=0.0,
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
            custos_operacao=0.0,
            irrf_informado=0.0,
        )

        result = calculator.calculate_result(trade, average_price=130000.00)

        assert result.ganho_prejuizo_bruto == pytest.approx(-200.0)  # (129000-130000)*1*0.20
        assert result.ir_devido == 0.0

    def test_irrf_is_the_value_informed_by_the_user(self, calculator):
        """
        IRRF is no longer estimated by the system (0,005%/1%) — it must be the
        actual value withheld per the corretora's nota (trade.irrf_informado),
        which the system echoes back as a credit against ir_devido.
        """
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=10,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
            custos_operacao=0.0,
            irrf_informado=0.50,
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        assert result.irrf_retido == pytest.approx(0.50, rel=1e-5)

    def test_irrf_day_trade_is_the_value_informed_by_the_user(self, calculator):
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=10,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
            classificacao=TradeOperationType.DAY_TRADE,
            custos_operacao=0.0,
            irrf_informado=10.00,
        )

        result = calculator.calculate_result(trade, average_price=90.00)

        assert result.irrf_retido == pytest.approx(10.00, rel=1e-5)

    def test_missing_custos_raises(self, calculator):
        """Costs remain required; missing withholding is explicitly unknown."""
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=10,
            preco_unitario=100.00,
            data_operacao=date(2025, 3, 15),
        )

        with pytest.raises(ValueError, match="custos"):
            calculator.calculate_result(trade, average_price=90.00)

    def test_custos_operacao_replaces_fee_estimate(self, calculator):
        """custos_operacao (nota real) is used as-is; no B3 fee-schedule estimate is added on top."""
        trade = TradeInput(
            ativo="WDO",
            tipo_ativo=AssetType.FUTURO_DOLAR,
            tipo_operacao=OperationType.VENDA,
            quantidade=2,
            preco_unitario=5280.00,
            data_operacao=date(2025, 3, 15),
            custos_operacao=12.34,
            irrf_informado=0.0,
        )

        result = calculator.calculate_result(trade, average_price=5230.00)

        assert result.taxas_totais.total == pytest.approx(12.34, rel=1e-5)

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

    def test_valor_liquido_is_net_gain_minus_max_of_ir_and_irrf(self, calculator):
        """
        valor_financeiro é nocional (não é recebido); o valor líquido real da
        operação é o ganho líquido (após custos) menos o maior entre IR devido
        e IRRF já retido (que é um crédito contra o IR, não um custo adicional).
        """
        trade = TradeInput(
            ativo="WIN",
            tipo_ativo=AssetType.FUTURO_INDICE,
            tipo_operacao=OperationType.VENDA,
            quantidade=3,
            preco_unitario=130000.00,
            data_operacao=date(2025, 3, 15),
            custos_operacao=0.0,
            irrf_informado=0.0,
        )

        result = calculator.calculate_result(trade, average_price=129500.00)

        expected = result.ganho_prejuizo_liquido - max(result.ir_devido, result.irrf_retido)
        assert result.valor_liquido == pytest.approx(expected, rel=1e-5)
