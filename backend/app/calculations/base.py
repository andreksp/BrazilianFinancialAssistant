"""
Base classes and utilities for financial calculations.

Reference: Documentation/research.md for all business rules.
"""

from decimal import Decimal
from abc import ABC, abstractmethod
from datetime import date

from app.models.trade import TradeInput, TaxCalculationResult, AssetType


class BaseCalculator(ABC):
    """
    Abstract base class for asset-specific calculators.

    Each asset type (Ações, BDR, FII, Opções) inherits from this and implements:
    - calculate_gain_loss(): Calculate gross gain/loss
    - get_tax_rate(): Get applicable tax rate (15% or 20%)
    - get_irrf_rate(): Get withholding tax rate (0.005% or 1%)
    """

    @abstractmethod
    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        """Calculate gain or loss on a transaction."""
        pass

    @abstractmethod
    def get_tax_rate(self, is_day_trade: bool = False) -> float:
        """
        Get applicable tax rate.
        Returns: 0.15 (15%), 0.20 (20%), etc.
        """
        pass

    @abstractmethod
    def get_irrf_rate(self, is_day_trade: bool = False) -> float:
        """Get withholding tax (IRRF) rate."""
        pass

    @abstractmethod
    def calculate_result(self, trade: TradeInput, average_price: float = None) -> TaxCalculationResult:
        """Calculate complete tax and fee result for a trade."""
        pass


def use_decimal_for_precision(value: float) -> Decimal:
    """
    Convert float to Decimal for precise financial calculations.

    Important: Python floats have rounding errors. Financial calculations must use Decimal.
    Example: 0.1 + 0.2 = 0.30000000000000004 (float) vs 0.3 (Decimal)
    """
    return Decimal(str(value))


def format_currency(value: float) -> str:
    """Format value as Brazilian currency (BRL)."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
