"""
API routes for accessing calculation results and tax summaries.

Endpoints:
- GET /api/calculations/{id} - Get single calculation result
- GET /api/calculations/summary - Get monthly tax summary
- GET /api/calculations/darf - Get DARF information
"""

import logging
from typing import List
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.models.trade import MonthlyTaxSummary, TaxCalculationResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{calculation_id}", response_model=TaxCalculationResult)
async def get_calculation(calculation_id: str):
    """
    Get a specific calculation result by ID.

    TODO: Implement with database storage

    Args:
        calculation_id: UUID of calculation result

    Returns:
        Complete calculation with breakdown
    """
    # TODO: Fetch from database
    raise HTTPException(status_code=404, detail="Calculation not found")


@router.get("/summary", response_model=MonthlyTaxSummary)
async def get_monthly_summary(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2000, le=2100, description="Year"),
    user_id: str = Query(None, description="User ID"),
):
    """
    Get monthly tax summary for IR declaration.

    Business Logic (research.md):
    - Aggregates all trades for the month
    - Separates swing trade vs day trade
    - Calculates total IR due
    - Calculates DARF due date (last business day of following month)
    - Applies loss compensation rules

    Args:
        month: Month (1-12)
        year: Year
        user_id: User ID

    Returns:
        Monthly summary with gains, losses, IR due, DARF info

    Example:
        GET /api/calculations/summary?month=3&year=2025

        Response:
        {
            "mes": 3,
            "ano": 2025,
            "ganho_swing_trade": 5000.0,
            "ganho_day_trade": 1500.0,
            "ir_swing_trade": 750.0,
            "ir_day_trade": 300.0,
            "ir_total_devido": 1050.0,
            "irrf_retido_total": 850.0,
            "darf_vencimento": "2025-04-30"
        }
    """
    # TODO: Fetch from database and calculate
    # Using TaxEngine.get_monthly_summary(month, year)

    raise HTTPException(status_code=404, detail="Monthly summary not found")


@router.get("/darf", response_model=dict)
async def get_darf_info(
    month: int = Query(..., ge=1, le=12, description="Month"),
    year: int = Query(..., ge=2000, le=2100, description="Year"),
):
    """
    Get DARF (tax payment) information for a specific month.

    Reference: research.md section 5 - DARF
    - Código: 6015 (Pessoa Física - Ganho operações bolsa)
    - Vencimento: Último dia útil do mês seguinte
    - Valor mínimo: R$10,00 (valores menores acumulam)

    Returns:
        DARF details with amount due, due date, payment code
    """
    # TODO: Calculate from monthly summary

    return {
        "codigo_darf": "6015",
        "descricao": "Ganho operações bolsa - Pessoa Física",
        "mes": month,
        "ano": year,
        "ir_devido": 0.0,
        "irrf_retido": 0.0,
        "valor_a_pagar": 0.0,
        "vencimento": None,
        "minimo_para_pagar": 10.0,
    }
