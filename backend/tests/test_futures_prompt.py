import json
from unittest.mock import Mock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.llm.claude_client import ClaudeClient, explicit_entry_points
from app.models.trade import TradeInput
from app.calculations.derivatives.futuros import FuturosCalculator
from app.mcp_gateway import calculate_via_mcp
from app.storage.database import Base
from app.storage.repository import save_trade, record_to_result

PROMPT = ('Simule a venda para encerrar uma posição comprada de 2 contratos de mini-índice WIN, '
          'com preço médio de entrada de 130.000 pontos e saída em 131.000 pontos, '
          'em 02/10/2026. Foi day trade. Custos da operação: R$ 0.')

def trade(**kw):
    data=dict(ativo='WIN',tipo_ativo='futuro_indice',tipo_operacao='venda',
              quantidade=2,preco_unitario=131000,data_operacao='2026-10-02',
              classificacao='day_trade',custos_operacao=0)
    data.update(kw)
    return TradeInput(**data)

@pytest.mark.parametrize('text,value', [('entrada de 130.000 pontos',130000),
    ('entrada média em 5.000 pontos',5000),('cotação de abertura a 5.000,5 pontos',5000.5),
    ('saída em 131.000 pontos',None)])
def test_explicit_entry_points(text,value):
    assert explicit_entry_points(text)==value

def test_conflicting_entries_are_rejected():
    with pytest.raises(ValueError):
        explicit_entry_points('entrada de 130.000 pontos e entrada de 140.000 pontos')

def test_parser_recovers_explicit_entry_when_llm_omits_it():
    client=ClaudeClient.__new__(ClaudeClient)
    client.model_parser='offline-test'
    client._call_model=Mock(return_value=trade().model_dump_json())
    parsed=client.parse_trade(PROMPT)
    assert parsed.preco_medio_informado==130000
    assert parsed.irrf_informado is None

def test_parser_rejects_conflicting_llm_entry():
    client=ClaudeClient.__new__(ClaudeClient)
    client.model_parser='offline-test'
    client._call_model=Mock(return_value=trade(preco_medio_informado=130).model_dump_json())
    assert client.parse_trade(PROMPT) is None

@pytest.mark.parametrize('asset,ticker,entry,exit_value,gain,tax',[
    ('futuro_indice','WIN',130000,131000,400,80),
    ('futuro_dolar','WDO',5000,5010,200,40)])
def test_real_mcp_without_irrf(asset,ticker,entry,exit_value,gain,tax):
    result=calculate_via_mcp(trade(tipo_ativo=asset,ativo=ticker,preco_unitario=exit_value),entry)
    assert result.ganho_prejuizo_bruto==gain
    assert result.ir_devido==tax
    assert result.irrf_nao_informado is True
    assert 'IRRF não informado' in result.mensagem

@pytest.mark.parametrize('irrf',[0,4])
def test_explicit_retention_is_preserved(irrf):
    result=FuturosCalculator().calculate_result(trade(irrf_informado=irrf),130000)
    assert result.irrf_retido==irrf
    assert result.irrf_nao_informado is False

def test_unknown_retention_survives_history_round_trip():
    engine=create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        t=trade()
        result=FuturosCalculator().calculate_result(t,130000)
        record=save_trade(db,t,result,user_id='test')
        assert record_to_result(record).irrf_nao_informado is True
    engine.dispose()
