"""
API routes for trade processing and history.

Endpoints:
- POST /api/trades/process  — Process a single trade (buy or sell)
- GET  /api/trades/history  — Get user's trade history
- POST /api/trades/batch    — Batch process multiple trades
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.models.trade import TradeInput, TaxCalculationResult, AssetType, OperationType
from app.calculations.equity.acoes import AcoesCalculator
from app.calculations.equity.bdrs import BDRCalculator
from app.calculations.equity.fiis import FIICalculator
from app.calculations.equity.opcoes import OpcoesCalculator
from app.storage.database import get_db
from app.storage.repository import save_trade, get_trades, get_average_price, record_to_result

logger = logging.getLogger(__name__)
router = APIRouter()

_CALCULATORS = {
    AssetType.ACAO: AcoesCalculator,
    AssetType.BDR: BDRCalculator,
    AssetType.FII: FIICalculator,
    AssetType.OPCAO: OpcoesCalculator,
}


@router.post("/process")
async def process_trade(
    trade: TradeInput,
    user_id: str = Query(default="default", description="User ID"),
    db: Session = Depends(get_db),
):
    """
    Process a single trade and calculate taxes, fees, and net value.

    For BUY: saves to portfolio history (no tax calculated).
    For SELL: computes average price from prior buys, calculates IR + fees.

    Returns TaxCalculationResult for sells, or a confirmation dict for buys.
    """
    try:
        logger.info(f"Processing trade: {trade.ativo} {trade.tipo_operacao.value}")

        if trade.tipo_operacao == OperationType.COMPRA:
            save_trade(db, trade, result=None, user_id=user_id)
            return {
                "tipo_operacao": "compra",
                "ativo": trade.ativo,
                "quantidade": trade.quantidade,
                "preco_unitario": trade.preco_unitario,
                "mensagem": f"Compra de {trade.ativo} registrada. Preço médio atualizado.",
            }

        # SELL — calculate taxes
        calculator_cls = _CALCULATORS.get(trade.tipo_ativo)
        if calculator_cls is None:
            raise HTTPException(
                status_code=400,
                detail=f"Asset type '{trade.tipo_ativo}' not supported",
            )

        avg_price = get_average_price(db, user_id=user_id, ativo=trade.ativo)
        if avg_price is None:
            avg_price = trade.preco_unitario  # No prior buys; assume zero gain

        calculator = calculator_cls()
        result = calculator.calculate_result(trade, average_price=avg_price)

        save_trade(db, trade, result=result, user_id=user_id)

        logger.info(f"Trade processed: {trade.ativo} — IR devido: R${result.ir_devido:.2f}")
        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing trade {trade.ativo}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history", response_model=List[TaxCalculationResult])
async def get_trade_history(
    user_id: str = Query(default="default", description="User ID"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    db: Session = Depends(get_db),
):
    """Return past sell calculations for the user, optionally filtered by month/year."""
    records = get_trades(
        db,
        user_id=user_id,
        month=month,
        year=year,
        tipo_operacao=OperationType.VENDA.value,
    )
    results = [record_to_result(r) for r in records]
    return [r for r in results if r is not None]


@router.post("/batch", response_model=List[TaxCalculationResult])
async def batch_process_trades(
    trades: List[TradeInput],
    user_id: str = Query(default="default", description="User ID"),
    db: Session = Depends(get_db),
):
    """
    Process multiple trades in sequence.

    Trades are processed in the order received. Average prices accumulate
    across the batch so subsequent sells use updated portfolio state.
    """
    results = []
    for trade in trades:
        try:
            if trade.tipo_operacao == OperationType.COMPRA:
                save_trade(db, trade, result=None, user_id=user_id)
                continue

            calculator_cls = _CALCULATORS.get(trade.tipo_ativo)
            if calculator_cls is None:
                logger.warning(f"Skipping unsupported asset type: {trade.tipo_ativo}")
                continue

            avg_price = get_average_price(db, user_id=user_id, ativo=trade.ativo)
            if avg_price is None:
                avg_price = trade.preco_unitario

            calculator = calculator_cls()
            result = calculator.calculate_result(trade, average_price=avg_price)
            save_trade(db, trade, result=result, user_id=user_id)
            results.append(result)

        except Exception as e:
            logger.warning(f"Failed to process {trade.ativo}: {e}")

    return results
