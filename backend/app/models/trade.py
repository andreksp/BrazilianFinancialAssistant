"""
Pydantic models for trade data structures.
These models define the input and output schemas for all trade-related operations.

Reference: Documentation/research.md for tax rules and calculations.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Enum for supported asset types (Phase 1)."""

    ACAO = "acao"  # Stocks
    BDR = "bdr"  # Brazilian Depositary Receipts
    FII = "fii"  # Real Estate Investment Funds
    OPCAO = "opcao"  # Stock Options
    # Phase 2: FUTURO_DOLAR, FUTURO_INDICE, FUTURO_CRIPTO


class OperationType(str, Enum):
    """Enum for buy/sell operations."""

    COMPRA = "compra"  # Buy
    VENDA = "venda"  # Sell


class TradeOperationType(str, Enum):
    """
    Enum for trade operation classification.

    Critical for IR calculation:
    - Swing trade: 15% (swing) or 0% if < R$20,000 total sold in month
    - Day trade: 20% (always), no exemption
    """

    SWING = "swing"  # Bought and sold on different days
    DAY_TRADE = "day_trade"  # Bought and sold same day


class TradeInput(BaseModel):
    """
    Input model for a single trade operation.

    Business Logic Reference (research.md):
    - Preço médio calculation: weighted average of all purchases
    - Gain/Loss: (sale_price - average_price) * quantity
    - Taxes vary by asset type and operation type (swing vs day trade)
    """

    # Asset identification
    ativo: str = Field(..., min_length=1, max_length=20, description="Asset ticker (e.g., PETR4)")
    tipo_ativo: AssetType = Field(..., description="Type of asset")
    tipo_operacao: OperationType = Field(..., description="Buy or sell")

    # Trade details
    quantidade: float = Field(..., gt=0, description="Quantity of units")
    preco_unitario: float = Field(..., gt=0, description="Price per unit (in BRL)")
    data_operacao: date = Field(..., description="Operation date (DD/MM/YYYY)")

    # Costs
    corretora: Optional[str] = Field(None, description="Broker name (optional)")
    corretagem_percentual: float = Field(
        default=0.0, ge=0, le=1, description="Broker fee as percentage (0.01 = 1%)"
    )
    corretagem_fixa: float = Field(default=0.0, ge=0, description="Fixed broker fee in BRL")

    # Optional metadata
    nota: Optional[str] = Field(None, description="User notes about the trade")


class FeesBreakdown(BaseModel):
    """
    Detailed breakdown of all fees and costs.

    Reference: research.md section 2 (B3 fees)
    - Taxa de liquidação: 0,0275% on financial value
    - Taxa de registro: 0,0034% (ações) or variable
    - Emolumentos: 0,003%
    - ISS: 5% on corretagem
    """

    taxa_liquidacao: float = Field(..., ge=0, description="B3 settlement fee (BRL)")
    taxa_registro: float = Field(..., ge=0, description="B3 registration fee (BRL)")
    emolumentos: float = Field(..., ge=0, description="B3 emoluments (BRL)")
    corretagem: float = Field(..., ge=0, description="Broker fee (BRL)")
    iss_sobre_corretagem: float = Field(..., ge=0, description="ISS tax on broker fee (BRL)")

    @property
    def total(self) -> float:
        """Total fees."""
        return (
            self.taxa_liquidacao
            + self.taxa_registro
            + self.emolumentos
            + self.corretagem
            + self.iss_sobre_corretagem
        )


class TaxCalculationResult(BaseModel):
    """
    Result of tax and fee calculations for a single trade.

    Business Logic (research.md):
    - IR alíquota: 15% (swing) or 20% (day trade)
    - Isenção: R$20,000/month for swing trades only
    - IRRF: 0,005% (swing) or 1% (day trade) - withholding tax
    - No tax compensation across different asset types (unless same type, same month)
    """

    # Trade reference
    ativo: str
    tipo_ativo: AssetType
    quantidade: float
    preco_unitario: float
    data_operacao: date

    # Calculation results
    valor_financeiro: float = Field(..., description="Total financial value (qty * price)")
    ganho_prejuizo_bruto: float = Field(
        ...,
        description="Gross gain/loss before fees (calculated from average price)",
    )
    taxas_totais: FeesBreakdown

    # Tax calculations
    aliquota_aplicada: float = Field(..., ge=0, le=1, description="Tax rate (15% or 20%)")
    ir_devido: float = Field(..., ge=0, description="Income tax due (imposto de renda)")
    irrf_retido: float = Field(..., ge=0, description="Withholding tax (retido na fonte)")
    isenção_aplicada: bool = Field(
        False, description="Whether R$20,000 exemption applied (swing trade only)"
    )

    # Final values
    ganho_prejuizo_liquido: float = Field(
        ..., description="Net gain/loss after all fees and taxes"
    )
    valor_liquido: float = Field(
        ..., description="Final amount after deducting all costs and taxes"
    )

    # Metadata
    tipo_operacao_classificacao: TradeOperationType = Field(
        ..., description="Classified as swing or day trade"
    )
    mensagem: Optional[str] = Field(None, description="Summary message for user")


class PortfolioPosition(BaseModel):
    """
    Current position in a specific asset.
    Used for tracking average price and quantities.

    Reference: research.md - Preço Médio (Weighted Moving Average)
    Formula: PM = (Qtd_anterior * PM_anterior + Qtd_nova * Preço_novo) / (Qtd_anterior + Qtd_nova)
    """

    ativo: str
    tipo_ativo: AssetType
    quantidade_total: float = Field(..., ge=0, description="Total quantity held")
    preco_medio: float = Field(..., ge=0, description="Weighted average price")
    data_primeira_compra: date
    data_ultima_compra: date
    valor_total_investido: float = Field(..., description="Total amount invested so far")


class MonthlyTaxSummary(BaseModel):
    """
    Monthly tax summary for a specific month/year.
    Used for DARF (Darf de Imposto de Renda Retido na Fonte).

    Reference: research.md section 5 (DARF)
    - Vencimento: último dia útil do mês seguinte
    - Código: 6015 (PF - Ganho operações bolsa)
    - Mínimo: R$10,00 (valores menores acumulam)
    """

    mes: int
    ano: int
    ganho_swing_trade: float = Field(default=0, description="Total swing trade gains")
    prejuizo_swing_trade: float = Field(default=0, description="Total swing trade losses")
    ganho_day_trade: float = Field(default=0, description="Total day trade gains")
    prejuizo_day_trade: float = Field(default=0, description="Total day trade losses")

    ir_swing_trade: float = Field(default=0, description="Income tax on swing trades")
    ir_day_trade: float = Field(default=0, description="Income tax on day trades")
    irrf_retido_total: float = Field(default=0, description="Total withholding tax")

    ir_total_devido: float = Field(default=0, description="Total IR due before IRRF credit")
    darf_vencimento: date = Field(..., description="DARF due date (último dia útil do mês)")

    @property
    def ir_a_pagar(self) -> float:
        """
        IR amount to pay = IR due - IRRF withheld.
        If negative, there's a credit to carry forward.
        """
        return max(0, self.ir_total_devido - self.irrf_retido_total)

    @property
    def ir_credito(self) -> float:
        """Credit if IRRF withheld > IR due."""
        return max(0, self.irrf_retido_total - self.ir_total_devido)


class ChatMessage(BaseModel):
    """Model for chat messages with LLM."""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    trade_extracted: Optional[TradeInput] = None
    calculation_result: Optional[TaxCalculationResult] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, description="User message in Portuguese")
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Assistant response in Portuguese")
    trade_extracted: Optional[TradeInput] = None
    calculation_result: Optional[TaxCalculationResult] = None
    confidence: float = Field(default=0.0, ge=0, le=1, description="Confidence in extraction")
    agent_name: Optional[str] = Field(default=None, description="Name of the specialist agent that handled this request")
