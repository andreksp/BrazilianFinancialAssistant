"""
Testes de falha via camada HTTP real (TestClient + FastAPI + gateway MCP real,
subprocess stdio real — não mockado), usando SQLite e Chroma temporários.

Cobre: custo médio ausente, total mensal ausente, prazo ausente, campos
inválidos, NaN/infinito, e processamento parcial em lote (batch).
Verifica que uma venda com falha NÃO é gravada no histórico.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
BACKEND = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND))

tmp_dir = tempfile.mkdtemp(prefix="mcp_fail_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp_dir}/test.db"
os.environ["CHROMA_DB_PATH"] = f"{tmp_dir}/chroma"
os.environ["ANTHROPIC_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app

_cm = TestClient(app)
client = _cm.__enter__()  # triggers lifespan startup -> Base.metadata.create_all()
results = []


def record(name, resp, expect_status, note=""):
    ok = resp.status_code == expect_status
    body = None
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    results.append({
        "case": name,
        "expected_status": expect_status,
        "actual_status": resp.status_code,
        "ok": ok,
        "body": body,
        "note": note,
    })
    print(f"[{'OK' if ok else 'FALHA'}] {name}: status={resp.status_code} (esperado {expect_status})")


# 1. Custo médio ausente (nenhuma compra registrada, sem preco_medio_informado)
r = client.post("/api/trades/process?user_id=fail_test_1", json={
    "ativo": "PETR4", "tipo_ativo": "acao", "tipo_operacao": "venda",
    "quantidade": 100, "preco_unitario": 30.0, "data_operacao": "2026-09-16",
})
record("custo_medio_ausente", r, 400)

# Verify nothing was recorded in history for this user
r_hist = client.get("/api/trades/history?user_id=fail_test_1")
results.append({
    "case": "custo_medio_ausente_sem_gravacao",
    "ok": r_hist.json() == [],
    "history_returned": r_hist.json(),
})
print(f"[{'OK' if r_hist.json() == [] else 'FALHA'}] custo_medio_ausente_sem_gravacao: history={r_hist.json()}")

# 2. Total mensal ausente (ações exigem total_vendas_mes)
r = client.post("/api/trades/process?user_id=fail_test_2", json={
    "ativo": "PETR4", "tipo_ativo": "acao", "tipo_operacao": "venda",
    "quantidade": 100, "preco_unitario": 30.0, "data_operacao": "2026-09-16",
    "preco_medio_informado": 25.0,
})
record("total_mensal_ausente", r, 400)

# 3. Prazo ausente (empréstimo de ações)
r = client.post("/api/trades/process?user_id=fail_test_3", json={
    "ativo": "VALE3", "tipo_ativo": "emprestimo_acoes", "tipo_operacao": "venda",
    "quantidade": 200, "preco_unitario": 0.60, "data_operacao": "2026-09-16",
})
record("prazo_ausente_emprestimo", r, 400)

# 4. Campos inválidos — tipo_ativo desconhecido (validação Pydantic -> 422)
r = client.post("/api/trades/process?user_id=fail_test_4", json={
    "ativo": "XXXX", "tipo_ativo": "futuro_cripto", "tipo_operacao": "venda",
    "quantidade": 1, "preco_unitario": 100.0, "data_operacao": "2026-09-16",
})
record("tipo_ativo_invalido", r, 422)

# 4b. quantidade negativa (validação Pydantic -> 422)
r = client.post("/api/trades/process?user_id=fail_test_4b", json={
    "ativo": "PETR4", "tipo_ativo": "acao", "tipo_operacao": "venda",
    "quantidade": -10, "preco_unitario": 30.0, "data_operacao": "2026-09-16",
    "preco_medio_informado": 25.0, "total_vendas_mes": 3000,
})
record("quantidade_negativa", r, 422)

# 5. NaN / infinito no preco_medio_informado
for label, bad_value in [("nan", float("nan")), ("inf", float("inf"))]:
    payload = {
        "ativo": "PETR4", "tipo_ativo": "acao", "tipo_operacao": "venda",
        "quantidade": 100, "preco_unitario": 30.0, "data_operacao": "2026-09-16",
        "preco_medio_informado": bad_value, "total_vendas_mes": 3000,
    }
    try:
        # Pydantic/FastAPI JSON encoding of NaN/inf is itself a relevant edge case;
        # send as raw content to bypass client-side json.dumps restrictions.
        raw = json.dumps(payload).replace('"__NAN__"', "NaN").replace('"__INF__"', "Infinity")
        r = client.post(
            f"/api/trades/process?user_id=fail_test_5_{label}",
            content=json.dumps(payload, allow_nan=True),
            headers={"Content-Type": "application/json"},
        )
        record(f"preco_medio_{label}", r, 400, note="Esperado: rejeitado como custo não-finito (gateway) ou 422 se o transporte JSON já recusar NaN/Infinity")
    except Exception as e:
        results.append({"case": f"preco_medio_{label}", "ok": None, "exception": f"{type(e).__name__}: {e}"})
        print(f"[EXC] preco_medio_{label}: {type(e).__name__}: {e}")

# 6. Batch parcial: 1 compra válida, 1 venda inválida (sem total mensal), 1 venda válida
batch = [
    {"ativo": "VALE3", "tipo_ativo": "acao", "tipo_operacao": "compra",
     "quantidade": 100, "preco_unitario": 20.0, "data_operacao": "2026-09-10"},
    {"ativo": "VALE3", "tipo_ativo": "acao", "tipo_operacao": "venda",
     "quantidade": 50, "preco_unitario": 25.0, "data_operacao": "2026-09-16"},  # missing total_vendas_mes -> should fail
    {"ativo": "HGLG11", "tipo_ativo": "fii", "tipo_operacao": "venda",
     "quantidade": 10, "preco_unitario": 110.0, "data_operacao": "2026-09-16",
     "preco_medio_informado": 100.0},  # should succeed
]
r = client.post("/api/trades/batch?user_id=fail_test_batch", json=batch)
batch_results = r.json()
results.append({
    "case": "batch_parcial",
    "status": r.status_code,
    "n_input": len(batch),
    "n_results": len(batch_results),
    "results": batch_results,
    "note": "Compra não retorna resultado; venda 2 (sem total mensal) deve falhar e ser omitida; venda 3 (FII) deve aparecer.",
})
print(f"[INFO] batch_parcial: {len(batch_results)} resultado(s) de {len(batch)} entradas -> {[b.get('ativo') for b in batch_results]}")

# 7. Servidor MCP ausente (simulado apontando o gateway para um caminho inexistente)
from app import mcp_gateway as gateway
original_server = gateway.SERVER
gateway.SERVER = Path(tmp_dir) / "servidor_inexistente.py"
r = client.post("/api/trades/process?user_id=fail_test_7", json={
    "ativo": "PETR4", "tipo_ativo": "acao", "tipo_operacao": "venda",
    "quantidade": 100, "preco_unitario": 30.0, "data_operacao": "2026-09-16",
    "preco_medio_informado": 25.0, "total_vendas_mes": 3000,
})
record("servidor_mcp_ausente", r, 400)
gateway.SERVER = original_server

out = Path(__file__).resolve().parent / "resultados_falhas_http.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"\nResultados salvos em {out}")
_cm.__exit__(None, None, None)
