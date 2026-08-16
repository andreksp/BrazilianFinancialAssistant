"""
Unit tests for B3 fees calculator.

Tests the fee breakdown across all asset types:
- Taxa de liquidação: 0,0275% (all assets)
- Taxa de registro: 0,0034% (ações, BDRs, FIIs, opções)
- Emolumentos: 0,003%
- Corretagem + ISS: configured per trade
"""

import pytest
from datetime import date

from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.fees.b3_fees import (
    calculate_b3_fees,
    B3_TAXA_LIQUIDACAO,
    B3_TAXA_REGISTRO_ACAO,
    B3_EMOLUMENTOS_ACAO,
    ISS_RATE,
)


def make_trade(asset_type: AssetType, valor: float, corretagem_pct: float = 0.0, corretagem_fixa: float = 0.0):
    """Helper to build a minimal trade for fee testing."""
    return TradeInput(
        ativo="TEST",
        tipo_ativo=asset_type,
        tipo_operacao=OperationType.VENDA,
        quantidade=1,
        preco_unitario=valor,
        data_operacao=date(2025, 3, 15),
        corretagem_percentual=corretagem_pct,
        corretagem_fixa=corretagem_fixa,
    )


class TestB3Fees:

    def test_liquidacao_fee_all_assets(self):
        """Taxa de liquidação is 0,0275% for all asset types."""
        for asset_type in [AssetType.ACAO, AssetType.BDR, AssetType.FII, AssetType.OPCAO]:
            trade = make_trade(asset_type, 10000.0)
            fees = calculate_b3_fees(10000.0, asset_type, trade)
            expected = 10000.0 * B3_TAXA_LIQUIDACAO
            assert fees.taxa_liquidacao == pytest.approx(expected, rel=1e-5), (
                f"Liquidação wrong for {asset_type}"
            )

    def test_registro_fee_acao(self):
        """Taxa de registro for Ações: 0,0034%."""
        trade = make_trade(AssetType.ACAO, 10000.0)
        fees = calculate_b3_fees(10000.0, AssetType.ACAO, trade)
        expected = 10000.0 * B3_TAXA_REGISTRO_ACAO
        assert fees.taxa_registro == pytest.approx(expected, rel=1e-5)

    def test_registro_fee_bdr_same_as_acao(self):
        """BDR registration fee is identical to Ações."""
        trade_acao = make_trade(AssetType.ACAO, 10000.0)
        trade_bdr = make_trade(AssetType.BDR, 10000.0)

        fees_acao = calculate_b3_fees(10000.0, AssetType.ACAO, trade_acao)
        fees_bdr = calculate_b3_fees(10000.0, AssetType.BDR, trade_bdr)

        assert fees_bdr.taxa_registro == pytest.approx(fees_acao.taxa_registro, rel=1e-5)
        assert fees_bdr.emolumentos == pytest.approx(fees_acao.emolumentos, rel=1e-5)

    def test_registro_fee_fii_same_as_acao(self):
        """FII registration fee is identical to Ações."""
        trade_acao = make_trade(AssetType.ACAO, 10000.0)
        trade_fii = make_trade(AssetType.FII, 10000.0)

        fees_acao = calculate_b3_fees(10000.0, AssetType.ACAO, trade_acao)
        fees_fii = calculate_b3_fees(10000.0, AssetType.FII, trade_fii)

        assert fees_fii.taxa_registro == pytest.approx(fees_acao.taxa_registro, rel=1e-5)

    def test_no_corretagem_when_zero(self):
        """Zero broker fee produces zero corretagem and zero ISS."""
        trade = make_trade(AssetType.ACAO, 10000.0, corretagem_pct=0.0, corretagem_fixa=0.0)
        fees = calculate_b3_fees(10000.0, AssetType.ACAO, trade)

        assert fees.corretagem == 0.0
        assert fees.iss_sobre_corretagem == 0.0

    def test_percentage_corretagem(self):
        """Percentage broker fee is correctly calculated."""
        trade = make_trade(AssetType.ACAO, 10000.0, corretagem_pct=0.001)  # 0.1%
        fees = calculate_b3_fees(10000.0, AssetType.ACAO, trade)

        expected_corretagem = 10000.0 * 0.001  # R$10
        expected_iss = expected_corretagem * ISS_RATE  # R$0.50
        assert fees.corretagem == pytest.approx(expected_corretagem, rel=1e-5)
        assert fees.iss_sobre_corretagem == pytest.approx(expected_iss, rel=1e-5)

    def test_fixed_corretagem(self):
        """Fixed broker fee is correctly applied."""
        trade = make_trade(AssetType.ACAO, 10000.0, corretagem_fixa=5.0)
        fees = calculate_b3_fees(10000.0, AssetType.ACAO, trade)

        assert fees.corretagem == pytest.approx(5.0, rel=1e-5)
        assert fees.iss_sobre_corretagem == pytest.approx(5.0 * ISS_RATE, rel=1e-5)

    def test_combined_corretagem(self):
        """Both fixed and percentage fees are summed."""
        trade = make_trade(AssetType.ACAO, 10000.0, corretagem_pct=0.001, corretagem_fixa=2.0)
        fees = calculate_b3_fees(10000.0, AssetType.ACAO, trade)

        expected_corretagem = 10000.0 * 0.001 + 2.0  # R$10 + R$2 = R$12
        assert fees.corretagem == pytest.approx(expected_corretagem, rel=1e-5)

    def test_total_is_sum_of_all_components(self):
        """FeesBreakdown.total equals sum of individual components."""
        trade = make_trade(AssetType.ACAO, 10000.0, corretagem_pct=0.001, corretagem_fixa=2.0)
        fees = calculate_b3_fees(10000.0, AssetType.ACAO, trade)

        expected_total = (
            fees.taxa_liquidacao
            + fees.taxa_registro
            + fees.emolumentos
            + fees.corretagem
            + fees.iss_sobre_corretagem
        )
        assert fees.total == pytest.approx(expected_total, rel=1e-5)

    def test_fees_scale_with_value(self):
        """Fees scale linearly with transaction value (no fixed component)."""
        trade_small = make_trade(AssetType.ACAO, 5000.0)
        trade_large = make_trade(AssetType.ACAO, 10000.0)

        fees_small = calculate_b3_fees(5000.0, AssetType.ACAO, trade_small)
        fees_large = calculate_b3_fees(10000.0, AssetType.ACAO, trade_large)

        assert fees_large.taxa_liquidacao == pytest.approx(fees_small.taxa_liquidacao * 2, rel=1e-5)
        assert fees_large.taxa_registro == pytest.approx(fees_small.taxa_registro * 2, rel=1e-5)
