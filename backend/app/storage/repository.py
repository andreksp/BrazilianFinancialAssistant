"""
CRUD operations for trade and chat history persistence.
"""

import json
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.models.trade import (
    TradeInput,
    TaxCalculationResult,
    AssetType,
    OperationType,
    FeesBreakdown,
)
from app.storage.models import TradeRecord, ChatHistoryRecord


# ---------------------------------------------------------------------------
# Trade persistence
# ---------------------------------------------------------------------------

def save_trade(
    db: Session,
    trade: TradeInput,
    result: Optional[TaxCalculationResult],
    user_id: str = "default",
) -> TradeRecord:
    """
    Persist a trade and its calculation result.

    For BUY trades result is None — only the trade fields are saved.
    For SELL trades the full calculation is stored alongside the trade.
    """
    record = TradeRecord(
        user_id=user_id,
        ativo=trade.ativo,
        tipo_ativo=trade.tipo_ativo.value,
        tipo_operacao=trade.tipo_operacao.value,
        quantidade=trade.quantidade,
        preco_unitario=trade.preco_unitario,
        data_operacao=trade.data_operacao,
        corretora=trade.corretora,
        corretagem_percentual=trade.corretagem_percentual,
        corretagem_fixa=trade.corretagem_fixa,
    )

    if result is not None:
        record.valor_financeiro = result.valor_financeiro
        record.ganho_prejuizo_bruto = result.ganho_prejuizo_bruto
        record.aliquota_aplicada = result.aliquota_aplicada
        record.ir_devido = result.ir_devido
        record.irrf_retido = result.irrf_retido
        record.isencao_aplicada = result.isenção_aplicada
        record.ganho_prejuizo_liquido = result.ganho_prejuizo_liquido
        record.valor_liquido = result.valor_liquido
        record.tipo_operacao_classificacao = result.tipo_operacao_classificacao.value
        record.mensagem = result.mensagem
        record.taxas_totais_json = result.taxas_totais.model_dump_json()

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_trades(
    db: Session,
    user_id: str = "default",
    month: Optional[int] = None,
    year: Optional[int] = None,
    tipo_operacao: Optional[str] = None,
    ativo: Optional[str] = None,
) -> List[TradeRecord]:
    """Load trades with optional filters. Results ordered by date ascending."""
    query = db.query(TradeRecord).filter(TradeRecord.user_id == user_id)

    if month is not None:
        query = query.filter(extract("month", TradeRecord.data_operacao) == month)
    if year is not None:
        query = query.filter(extract("year", TradeRecord.data_operacao) == year)
    if tipo_operacao is not None:
        query = query.filter(TradeRecord.tipo_operacao == tipo_operacao)
    if ativo is not None:
        query = query.filter(TradeRecord.ativo == ativo)

    return query.order_by(TradeRecord.data_operacao.asc()).all()


def get_average_price(db: Session, user_id: str, ativo: str) -> Optional[float]:
    """
    Compute the current weighted average purchase price for an asset.

    Algorithm (processes all trades in chronological order):
    - BUY: updates weighted average using standard formula
    - SELL: reduces quantity held (average price unchanged)

    Returns None if no purchases exist for the asset.
    """
    trades = get_trades(db, user_id=user_id, ativo=ativo)

    qty_held = 0.0
    preco_medio = 0.0

    for t in trades:
        if t.tipo_operacao == OperationType.COMPRA.value:
            # Weighted average: (qty_held * PM + qty_new * price) / (qty_held + qty_new)
            novo_investimento = t.quantidade * t.preco_unitario
            preco_medio = (
                (qty_held * preco_medio + novo_investimento) / (qty_held + t.quantidade)
                if (qty_held + t.quantidade) > 0
                else t.preco_unitario
            )
            qty_held += t.quantidade
        elif t.tipo_operacao == OperationType.VENDA.value:
            qty_held -= t.quantidade
            if qty_held < 0:
                qty_held = 0.0  # Safety guard against data inconsistency

    return preco_medio if qty_held > 0 else None


def record_to_result(record: TradeRecord) -> Optional[TaxCalculationResult]:
    """
    Reconstruct a TaxCalculationResult from a stored TradeRecord.

    Returns None if the record is a BUY (no calculation stored).
    """
    if record.ir_devido is None:
        return None

    fees_data = json.loads(record.taxas_totais_json)
    fees = FeesBreakdown(**fees_data)

    from app.models.trade import TradeOperationType
    return TaxCalculationResult(
        ativo=record.ativo,
        tipo_ativo=AssetType(record.tipo_ativo),
        quantidade=record.quantidade,
        preco_unitario=record.preco_unitario,
        data_operacao=record.data_operacao,
        valor_financeiro=record.valor_financeiro,
        ganho_prejuizo_bruto=record.ganho_prejuizo_bruto,
        taxas_totais=fees,
        aliquota_aplicada=record.aliquota_aplicada,
        ir_devido=record.ir_devido,
        irrf_retido=record.irrf_retido,
        isenção_aplicada=record.isencao_aplicada or False,
        ganho_prejuizo_liquido=record.ganho_prejuizo_liquido,
        valor_liquido=record.valor_liquido,
        tipo_operacao_classificacao=TradeOperationType(record.tipo_operacao_classificacao),
        mensagem=record.mensagem,
    )


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

def save_chat(
    db: Session,
    user_id: str,
    message: str,
    response: str,
    trade_extracted: Optional[TradeInput] = None,
    calculation: Optional[TaxCalculationResult] = None,
) -> ChatHistoryRecord:
    record = ChatHistoryRecord(
        user_id=user_id,
        message=message,
        response=response,
        trade_extracted_json=trade_extracted.model_dump_json() if trade_extracted else None,
        calculation_json=calculation.model_dump_json() if calculation else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_chat_history(
    db: Session,
    user_id: str = "default",
    limit: int = 50,
) -> List[ChatHistoryRecord]:
    return (
        db.query(ChatHistoryRecord)
        .filter(ChatHistoryRecord.user_id == user_id)
        .order_by(ChatHistoryRecord.created_at.desc())
        .limit(limit)
        .all()
    )
