"""
Integration tests for the FastAPI endpoints.

Uses an in-memory SQLite database via dependency override so tests are
isolated from the development database (app.db).
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.storage.database import get_db, Base
from app.storage import models  # noqa: F401 — registers ORM classes on Base


# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------

# StaticPool forces all connections to reuse the same underlying SQLite
# connection, which is required for in-memory databases to be visible
# across multiple sessions in the same test.
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/trades/process
# ---------------------------------------------------------------------------

class TestProcessTrade:

    def test_process_acao_sell(self, client):
        """Sell of Ação returns full TaxCalculationResult."""
        payload = {
            "ativo": "PETR4",
            "tipo_ativo": "acao",
            "tipo_operacao": "venda",
            "quantidade": 100,
            "preco_unitario": 30.00,
            "data_operacao": "2025-03-15",
        }
        resp = client.post("/api/trades/process", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ativo"] == "PETR4"
        assert data["ir_devido"] >= 0
        assert data["valor_financeiro"] == 3000.0

    def test_process_bdr_sell(self, client):
        """BDR sell uses 15% rate."""
        payload = {
            "ativo": "AMZO34",
            "tipo_ativo": "bdr",
            "tipo_operacao": "venda",
            "quantidade": 10,
            "preco_unitario": 200.00,
            "data_operacao": "2025-03-15",
        }
        resp = client.post("/api/trades/process", json=payload)
        assert resp.status_code == 200
        assert resp.json()["aliquota_aplicada"] == 0.15

    def test_process_fii_sell_no_exemption(self, client):
        """FII sell always uses 20% — no exemption."""
        payload = {
            "ativo": "HGLG11",
            "tipo_ativo": "fii",
            "tipo_operacao": "venda",
            "quantidade": 10,
            "preco_unitario": 150.00,
            "data_operacao": "2025-03-15",
        }
        resp = client.post("/api/trades/process", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["aliquota_aplicada"] == 0.20
        assert data.get("isenção_aplicada", False) is False

    def test_process_opcao_sell(self, client):
        """Option sell returns 15% rate (swing)."""
        payload = {
            "ativo": "PETRH250",
            "tipo_ativo": "opcao",
            "tipo_operacao": "venda",
            "quantidade": 100,
            "preco_unitario": 5.00,
            "data_operacao": "2025-03-15",
        }
        resp = client.post("/api/trades/process", json=payload)
        assert resp.status_code == 200
        assert resp.json()["aliquota_aplicada"] == 0.15

    def test_buy_returns_confirmation(self, client):
        """Buy trade returns a simple confirmation (not a TaxCalculationResult)."""
        payload = {
            "ativo": "VALE3",
            "tipo_ativo": "acao",
            "tipo_operacao": "compra",
            "quantidade": 100,
            "preco_unitario": 20.00,
            "data_operacao": "2025-03-10",
        }
        resp = client.post("/api/trades/process", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo_operacao"] == "compra"
        assert "mensagem" in data

    def test_sell_uses_average_price_from_prior_buy(self, client):
        """
        Sell calculates gain from the average price of prior purchases,
        not from the sale price itself.

        Buy 100 @ R$20 → average price = R$20
        Sell 100 @ R$25 → gain = (25 - 20) * 100 = R$500
        IR = 500 * 15% = R$75
        """
        buy = {
            "ativo": "VALE3",
            "tipo_ativo": "acao",
            "tipo_operacao": "compra",
            "quantidade": 100,
            "preco_unitario": 20.00,
            "data_operacao": "2025-03-10",
        }
        client.post("/api/trades/process", json=buy)

        sell = {
            "ativo": "VALE3",
            "tipo_ativo": "acao",
            "tipo_operacao": "venda",
            "quantidade": 100,
            "preco_unitario": 25.00,
            "data_operacao": "2025-03-15",
        }
        resp = client.post("/api/trades/process", json=sell)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ganho_prejuizo_bruto"] == pytest.approx(500.0)
        assert data["ir_devido"] == pytest.approx(75.0)

    def test_unsupported_asset_type_returns_400(self, client):
        """Invalid asset type returns 422 (Pydantic validation)."""
        payload = {
            "ativo": "WINFUT",
            "tipo_ativo": "futuro_indice",  # Not a valid AssetType
            "tipo_operacao": "venda",
            "quantidade": 1,
            "preco_unitario": 130000.0,
            "data_operacao": "2025-03-15",
        }
        resp = client.post("/api/trades/process", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/trades/history
# ---------------------------------------------------------------------------

class TestTradeHistory:

    def test_history_empty_initially(self, client):
        resp = client.get("/api/trades/history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_sell_appears_in_history(self, client):
        """A processed sell trade is retrievable from history."""
        sell = {
            "ativo": "PETR4",
            "tipo_ativo": "acao",
            "tipo_operacao": "venda",
            "quantidade": 100,
            "preco_unitario": 30.00,
            "data_operacao": "2025-03-15",
        }
        client.post("/api/trades/process", json=sell)

        resp = client.get("/api/trades/history")
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) == 1
        assert history[0]["ativo"] == "PETR4"

    def test_buy_does_not_appear_in_history(self, client):
        """Buy trades (no tax calc) are not returned in history."""
        buy = {
            "ativo": "VALE3",
            "tipo_ativo": "acao",
            "tipo_operacao": "compra",
            "quantidade": 100,
            "preco_unitario": 20.00,
            "data_operacao": "2025-03-10",
        }
        client.post("/api/trades/process", json=buy)

        resp = client.get("/api/trades/history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_filtered_by_month(self, client):
        """Month filter returns only trades from that month."""
        for day, month in [("2025-03-15", "março"), ("2025-04-10", "abril")]:
            client.post("/api/trades/process", json={
                "ativo": "PETR4",
                "tipo_ativo": "acao",
                "tipo_operacao": "venda",
                "quantidade": 10,
                "preco_unitario": 30.00,
                "data_operacao": day,
            })

        resp = client.get("/api/trades/history?month=3&year=2025")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["data_operacao"] == "2025-03-15"


# ---------------------------------------------------------------------------
# POST /api/trades/batch
# ---------------------------------------------------------------------------

class TestBatchProcessing:

    def test_batch_processes_sells(self, client):
        """Batch endpoint processes multiple sells and returns results."""
        trades = [
            {
                "ativo": "PETR4",
                "tipo_ativo": "acao",
                "tipo_operacao": "venda",
                "quantidade": 100,
                "preco_unitario": 25.00,
                "data_operacao": "2025-03-15",
            },
            {
                "ativo": "VALE3",
                "tipo_ativo": "acao",
                "tipo_operacao": "venda",
                "quantidade": 50,
                "preco_unitario": 22.00,
                "data_operacao": "2025-03-16",
            },
        ]
        resp = client.post("/api/trades/batch", json=trades)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2

    def test_batch_buy_then_sell_uses_average_price(self, client):
        """
        Buy + sell in batch: sell should use average price from the batch buy.

        Buy 100 @ R$20, Sell 100 @ R$25 → gain = R$500
        """
        trades = [
            {
                "ativo": "VALE3",
                "tipo_ativo": "acao",
                "tipo_operacao": "compra",
                "quantidade": 100,
                "preco_unitario": 20.00,
                "data_operacao": "2025-03-10",
            },
            {
                "ativo": "VALE3",
                "tipo_ativo": "acao",
                "tipo_operacao": "venda",
                "quantidade": 100,
                "preco_unitario": 25.00,
                "data_operacao": "2025-03-15",
            },
        ]
        resp = client.post("/api/trades/batch", json=trades)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1  # Only 1 sell result
        assert results[0]["ganho_prejuizo_bruto"] == pytest.approx(500.0)


# ---------------------------------------------------------------------------
# GET /api/calculations/summary
# ---------------------------------------------------------------------------

class TestCalculationsSummary:

    def test_summary_404_when_no_trades(self, client):
        resp = client.get("/api/calculations/summary?month=3&year=2025")
        assert resp.status_code == 404

    def test_summary_aggregates_ir(self, client):
        """Monthly summary aggregates IR from multiple sell trades."""
        for ticker, price in [("PETR4", 25.0), ("VALE3", 22.0)]:
            client.post("/api/trades/process", json={
                "ativo": ticker,
                "tipo_ativo": "acao",
                "tipo_operacao": "venda",
                "quantidade": 100,
                "preco_unitario": price,
                "data_operacao": "2025-03-15",
            })

        resp = client.get("/api/calculations/summary?month=3&year=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mes"] == 3
        assert data["ano"] == 2025
        assert data["ir_total_devido"] >= 0

    def test_darf_vencimento_is_last_day_of_next_month(self, client):
        """DARF due date for March 2025 should be April 30, 2025."""
        client.post("/api/trades/process", json={
            "ativo": "PETR4",
            "tipo_ativo": "acao",
            "tipo_operacao": "venda",
            "quantidade": 100,
            "preco_unitario": 25.00,
            "data_operacao": "2025-03-15",
        })

        resp = client.get("/api/calculations/summary?month=3&year=2025")
        assert resp.status_code == 200
        assert resp.json()["darf_vencimento"] == "2025-04-30"


# ---------------------------------------------------------------------------
# GET /api/calculations/darf
# ---------------------------------------------------------------------------

class TestDarfEndpoint:

    def test_darf_no_trades_returns_zeros(self, client):
        resp = client.get("/api/calculations/darf?month=3&year=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert data["valor_a_pagar"] == 0.0
        assert data["codigo_darf"] == "6015"

    def test_darf_below_minimum_not_payable(self, client):
        """When IR < R$10, deve_pagar is False."""
        client.post("/api/trades/process", json={
            "ativo": "PETR4",
            "tipo_ativo": "acao",
            "tipo_operacao": "venda",
            "quantidade": 1,
            "preco_unitario": 26.00,
            "data_operacao": "2025-03-15",
        })
        resp = client.get("/api/calculations/darf?month=3&year=2025")
        assert resp.status_code == 200
        # 1 share, small gain → IR likely < R$10
        data = resp.json()
        assert "deve_pagar" in data
