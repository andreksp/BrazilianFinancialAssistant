"""
API routes for calculation summaries and DARF information.

Endpoints:
- GET /api/calculations/summary  — Monthly tax summary
- GET /api/calculations/darf     — DARF payment info for a month
- GET /api/calculations/{id}     — Single calculation (by trade record ID)

Note: /summary and /darf are declared BEFORE /{id} so FastAPI routes them correctly.
"""

import logging
from datetime import date

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.models.trade import MonthlyTaxSummary, TaxCalculationResult, TradeInput, OperationType
from app.calculations.taxes.ir_engine import TaxEngine
from app.storage.database import get_db
from app.storage.repository import get_trades, record_to_result

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary", response_model=MonthlyTaxSummary)
async def get_monthly_summary(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2000, le=2100, description="Year"),
    user_id: str = Query(default="default", description="User ID"),
    db: Session = Depends(get_db),
):
    """
    Monthly tax summary for IR declaration.

    Loads all sell trades for the month from the DB and aggregates them
    through the TaxEngine to produce gains, losses, IR due, and DARF date.
    """
    sell_records = get_trades(
        db,
        user_id=user_id,
        month=month,
        year=year,
        tipo_operacao=OperationType.VENDA.value,
    )

    if not sell_records:
        raise HTTPException(
            status_code=404,
            detail=f"No trades found for {month:02d}/{year}",
        )

    engine = TaxEngine()
    for record in sell_records:
        result = record_to_result(record)
        if result is None:
            continue
        trade = TradeInput(
            ativo=record.ativo,
            tipo_ativo=record.tipo_ativo,
            tipo_operacao=record.tipo_operacao,
            quantidade=record.quantidade,
            preco_unitario=record.preco_unitario,
            data_operacao=record.data_operacao,
            corretora=record.corretora,
            corretagem_percentual=record.corretagem_percentual,
            corretagem_fixa=record.corretagem_fixa,
        )
        engine.add_trade(trade, result)

    return engine.get_monthly_summary(month, year)


@router.get("/darf")
async def get_darf_info(
    month: int = Query(..., ge=1, le=12, description="Month"),
    year: int = Query(..., ge=2000, le=2100, description="Year"),
    user_id: str = Query(default="default", description="User ID"),
    db: Session = Depends(get_db),
):
    """
    DARF payment information for a specific month.

    Reference: Código 6015 — Ganho operações bolsa (Pessoa Física)
    Vencimento: último dia útil do mês seguinte
    Mínimo para recolhimento: R$10,00
    """
    try:
        summary = await get_monthly_summary(month=month, year=year, user_id=user_id, db=db)
    except HTTPException:
        summary = None

    ir_devido = summary.ir_total_devido if summary else 0.0
    irrf_retido = summary.irrf_retido_total if summary else 0.0
    valor_a_pagar = summary.ir_a_pagar if summary else 0.0
    vencimento = summary.darf_vencimento if summary else None

    return {
        "codigo_darf": "6015",
        "descricao": "Ganho operações bolsa - Pessoa Física",
        "mes": month,
        "ano": year,
        "ir_devido": ir_devido,
        "irrf_retido": irrf_retido,
        "valor_a_pagar": valor_a_pagar,
        "vencimento": vencimento,
        "minimo_para_pagar": 10.0,
        "deve_pagar": valor_a_pagar >= 10.0,
    }


@router.get("/{calculation_id}", response_model=TaxCalculationResult)
async def get_calculation(
    calculation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve a specific calculation by trade record ID."""
    from app.storage.models import TradeRecord
    record = db.query(TradeRecord).filter(TradeRecord.id == calculation_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Calculation not found")

    result = record_to_result(record)
    if result is None:
        raise HTTPException(status_code=404, detail="No calculation for this trade (buy trade)")

    return result
