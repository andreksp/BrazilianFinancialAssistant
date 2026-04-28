"""
API routes for trade processing and calculation.

Endpoints:
- POST /api/trades/process - Process a single trade and calculate taxes/fees
- GET /api/trades/history - Get user's trade history
- POST /api/trades/batch - Batch process multiple trades
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.models.trade import TradeInput, TaxCalculationResult, AssetType, OperationType
from app.calculations.equity.acoes import AcoesCalculator

logger = logging.getLogger(__name__)
router = APIRouter()

# TODO: Move to service layer
_tax_engine = None  # Will be initialized from database/storage


@router.post("/process", response_model=TaxCalculationResult)
async def process_trade(trade: TradeInput) -> TaxCalculationResult:
    """
    Process a single trade and calculate taxes, fees, and net value.

    Business Logic:
    1. Validate trade input
    2. Get average price from portfolio (if selling)
    3. Calculate gain/loss
    4. Calculate B3 fees
    5. Calculate IR based on asset type and operation
    6. Return detailed breakdown

    Args:
        trade: Trade input with asset, quantity, price, date, etc.

    Returns:
        Complete calculation result with IR, fees, and net value

    Example:
        POST /api/trades/process
        {
            "ativo": "PETR4",
            "tipo_ativo": "acao",
            "tipo_operacao": "venda",
            "quantidade": 100,
            "preco_unitario": 25.50,
            "data_operacao": "2025-03-15",
            "corretora": "C6"
        }
    """
    try:
        logger.info(f"Processing trade: {trade.ativo} - {trade.tipo_operacao}")

        # Validate trade
        if trade.tipo_operacao == OperationType.VENDA:
            # For sales, average price is needed (TODO: fetch from DB)
            # For MVP, use current price as fallback
            average_price = None  # Should fetch from portfolio
        else:
            average_price = trade.preco_unitario

        # Route to appropriate calculator
        result = None
        if trade.tipo_ativo == AssetType.ACAO:
            calculator = AcoesCalculator()
            result = calculator.calculate_result(trade, average_price)
        elif trade.tipo_ativo == AssetType.BDR:
            # BDR uses same rules as Ações
            calculator = AcoesCalculator()
            result = calculator.calculate_result(trade, average_price)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Asset type {trade.tipo_ativo} not yet supported (Phase 2)",
            )

        logger.info(f"Trade processed successfully: {trade.ativo}")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing trade: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history", response_model=List[TaxCalculationResult])
async def get_trade_history(
    user_id: str = Query(..., description="User ID"),
    month: int = Query(None, description="Filter by month (1-12)"),
    year: int = Query(None, description="Filter by year"),
):
    """
    Get user's trade history with calculation results.

    TODO: Implement with database storage
    """
    # TODO: Fetch from database
    return []


@router.post("/batch", response_model=List[TaxCalculationResult])
async def batch_process_trades(trades: List[TradeInput]) -> List[TaxCalculationResult]:
    """
    Process multiple trades in batch.

    Useful for importing monthly statements from brokers.

    Args:
        trades: List of trades to process

    Returns:
        List of calculation results
    """
    results = []
    for trade in trades:
        try:
            # Reuse single-trade processing logic
            # result = await process_trade(trade)
            # results.append(result)
            pass
        except HTTPException:
            # Continue processing other trades
            logger.warning(f"Failed to process {trade.ativo}, continuing...")
            pass

    return results
