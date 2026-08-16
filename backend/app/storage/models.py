"""
SQLAlchemy ORM models for persisting trades and chat history.
"""

import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Float, Boolean, Date, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.database import Base


class TradeRecord(Base):
    """
    Persisted record for a single trade operation (buy or sell).

    For BUY trades: tax fields are NULL (no calculation at purchase time).
    For SELL trades: all fields populated from TaxCalculationResult.
    """

    __tablename__ = "trades"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)

    # TradeInput fields
    ativo: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tipo_ativo: Mapped[str] = mapped_column(String, nullable=False)
    tipo_operacao: Mapped[str] = mapped_column(String, nullable=False)  # compra / venda
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    preco_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    data_operacao: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    corretora: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    corretagem_percentual: Mapped[float] = mapped_column(Float, default=0.0)
    corretagem_fixa: Mapped[float] = mapped_column(Float, default=0.0)

    # TaxCalculationResult fields (NULL for BUY trades)
    valor_financeiro: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ganho_prejuizo_bruto: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    aliquota_aplicada: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ir_devido: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    irrf_retido: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    isencao_aplicada: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    ganho_prejuizo_liquido: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    valor_liquido: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tipo_operacao_classificacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mensagem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # FeesBreakdown serialized as JSON string
    taxas_totais_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ChatHistoryRecord(Base):
    """Persisted chat message and assistant response."""

    __tablename__ = "chat_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    trade_extracted_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calculation_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
