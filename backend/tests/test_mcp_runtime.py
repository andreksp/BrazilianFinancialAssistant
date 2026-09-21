import asyncio
from pathlib import Path
import pytest
from app.models.trade import TradeInput
from app import mcp_gateway as gateway

def trade(**changes):
    values=dict(ativo='HGLG11',tipo_ativo='fii',tipo_operacao='venda',quantidade=10,preco_unitario=110,data_operacao='2026-09-16',custos_operacao=0)
    values.update(changes)
    return TradeInput(**values)

def test_real_stdio_calculation():
    result=gateway.calculate_via_mcp(trade(),100)
    assert result.ir_devido==20
    assert result.taxas_totais.total==0

def test_single_server_entrypoint():
    import json
    root=Path(__file__).resolve().parents[2]
    config=json.loads((root/'.mcp.json').read_text(encoding='utf8'))
    assert gateway.SERVER.resolve()==(root/'mcp_server/server.py').resolve()
    assert Path(config['mcpServers']['brazilian-financial']['args'][0]).resolve()==gateway.SERVER.resolve()
    assert not (root/'mcp_server/runtime_server.py').exists()

def test_real_stdio_rejects_missing_cost():
    with pytest.raises(ValueError,match='custo médio'):gateway.calculate_via_mcp(trade())

def test_real_stdio_prefers_explicit_cost():
    assert gateway.calculate_via_mcp(trade(preco_medio_informado=105),100).ir_devido==10

def test_real_stdio_missing_month():
    with pytest.raises(ValueError,match='total completo'):
        gateway.calculate_via_mcp(trade(ativo='PETR4',tipo_ativo='acao'),100)

def test_transport_failure_has_no_fallback(monkeypatch,tmp_path):
    monkeypatch.setattr(gateway,'SERVER',tmp_path/'missing_server.py')
    with pytest.raises(ValueError,match='MCP indisponível'):gateway.calculate_via_mcp(trade(),100)

def test_sync_agent_inside_event_loop():
    async def invoke():return gateway.calculate_via_mcp(trade(),100)
    assert asyncio.run(invoke()).ir_devido==20
