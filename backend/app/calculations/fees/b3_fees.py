"""
B3 (Bolsa de Valores) and broker fees calculator.

Reference: Documentation/research.md section 2
- Taxa de liquidação: 0,0275% on financial value
- Taxa de registro: 0,0034% (ações), variable for derivatives
- Emolumentos: 0,003%
- Corretagem: Variable by broker (configurable)
- ISS: 5% on corretagem (municipal tax)

Business Logic:
Total fees = Liquidação + Registro + Emolumentos + Corretagem + ISS
"""

from typing import Optional

from app.models.trade import (
    TradeInput,
    AssetType,
    FeesBreakdown,
)


# B3 Fee Constants (in percentage)
B3_TAXA_LIQUIDACAO = 0.000275  # 0,0275%
B3_TAXA_REGISTRO_ACAO = 0.000034  # 0,0034%
B3_EMOLUMENTOS_ACAO = 0.00003  # 0,003%
B3_TAXA_REGISTRO_OPCAO = 0.000034  # Variable, using ação as baseline
B3_EMOLUMENTOS_OPCAO = 0.00003

# Tax rates
ISS_RATE = 0.05  # 5% on broker fee


def calculate_b3_fees(
    valor_financeiro: float,
    asset_type: AssetType,
    trade: TradeInput,
) -> FeesBreakdown:
    """
    Calculate all B3 and broker fees for a trade.

    Args:
        valor_financeiro: Total transaction value (quantity * price)
        asset_type: Type of asset (affects fee structure)
        trade: Trade details including broker and fees

    Returns:
        Detailed breakdown of all fees
    """

    # B3 settlement fee (always applies)
    taxa_liquidacao = valor_financeiro * B3_TAXA_LIQUIDACAO

    # Registration fee (varies by asset type)
    if asset_type == AssetType.ACAO or asset_type == AssetType.BDR:
        taxa_registro = valor_financeiro * B3_TAXA_REGISTRO_ACAO
        emolumentos = valor_financeiro * B3_EMOLUMENTOS_ACAO
    elif asset_type == AssetType.OPCAO:
        taxa_registro = valor_financeiro * B3_TAXA_REGISTRO_OPCAO
        emolumentos = valor_financeiro * B3_EMOLUMENTOS_OPCAO
    elif asset_type == AssetType.FII:
        # FII has same fees as stocks
        taxa_registro = valor_financeiro * B3_TAXA_REGISTRO_ACAO
        emolumentos = valor_financeiro * B3_EMOLUMENTOS_ACAO
    else:
        taxa_registro = 0
        emolumentos = 0

    # Broker fee (combines fixed and percentage)
    corretagem = (valor_financeiro * trade.corretagem_percentual) + trade.corretagem_fixa

    # ISS (municipal tax) on broker fee
    iss = corretagem * ISS_RATE

    return FeesBreakdown(
        taxa_liquidacao=taxa_liquidacao,
        taxa_registro=taxa_registro,
        emolumentos=emolumentos,
        corretagem=corretagem,
        iss_sobre_corretagem=iss,
    )


def calculate_minimum_broker_fee(asset_type: AssetType) -> float:
    """
    Calculate minimum broker fee (floor) for a transaction.

    Most brokers have minimum fees:
    - Ações: R$0,50 - R$2,00
    - BDR: R$0,50 - R$2,00
    - Opções: R$1,00 - R$5,00
    - FII: R$0,50 - R$2,00

    For MVP, using generic minimums. Should be configurable per broker.
    """
    minimums = {
        AssetType.ACAO: 0.50,
        AssetType.BDR: 0.50,
        AssetType.OPCAO: 1.00,
        AssetType.FII: 0.50,
    }
    return minimums.get(asset_type, 0.50)
