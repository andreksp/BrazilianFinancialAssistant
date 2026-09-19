"""
Fee calculator for Criptomoedas trades.

Crypto exchanges (Binance, Mercado Bitcoin, Foxbit, etc.) don't follow the B3
fee schedule (taxa de liquidação/registro/emolumentos) — only the exchange's
own trading fee applies, which the user provides via corretagem_percentual /
corretagem_fixa. ISS doesn't apply either, since crypto exchanges aren't
brokerage firms subject to that municipal tax on corretagem.
"""

from app.models.trade import TradeInput, FeesBreakdown


def calculate_crypto_fees(valor_financeiro: float, trade: TradeInput) -> FeesBreakdown:
    """Calculate exchange fees for a crypto trade (no B3 fee schedule applies)."""
    corretagem = (valor_financeiro * trade.corretagem_percentual) + trade.corretagem_fixa

    return FeesBreakdown(
        taxa_liquidacao=0.0,
        taxa_registro=0.0,
        emolumentos=0.0,
        corretagem=corretagem,
        iss_sobre_corretagem=0.0,
    )
