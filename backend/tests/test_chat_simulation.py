"""Regression coverage for partial operations and simulations. No live LLM calls."""
import json
from datetime import date, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.agents import base_agent, orchestrator
from app.agents.acoes_agent import AcoesAgent
from app.agents.chat_policy import may_register, history_clarification
from app.llm.claude_client import ClaudeClient
from app.models.trade import TradeInput
from app.storage.database import Base
from app.storage.repository import save_trade, get_average_price, get_trades
from app.calculations.equity.acoes import AcoesCalculator


def trade(**kwargs):
    data = dict(ativo='PETR4', tipo_ativo='acao', tipo_operacao='venda',
                quantidade=4000, preco_unitario=51, data_operacao='2026-10-02',
                classificacao='swing', total_vendas_mes=204000, custos_operacao=0,
                irrf_informado=0)
    data.update(kwargs)
    return TradeInput(**data)


@pytest.fixture
def db(monkeypatch):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    monkeypatch.setattr(base_agent, 'get_chroma_client', lambda: None)
    with Session(engine) as session:
        save_trade(session, trade(tipo_operacao='compra', preco_unitario=40,
                                 data_operacao='2026-09-25'), None, user_id='alice')
        yield session
    engine.dispose()


@pytest.mark.parametrize('message', [
    'Se eu vender hoje PETR4 a 4000 a 51 reais hoje dia 02/10',
    'Simule a venda de 4000 PETR4', 'Venderia 4000 PETR4',
    'Comprei 4000 PETR4, mas simule a venda', 'Não vendi PETR4',
    'Vendi 4000 PETR4, não registre', 'Venda de 4000 PETR4',
    'Quero comprar 4000 PETR4', 'Registre uma simulação de venda',
    'Se eu tivesse comprado PETR4', 'Vendi PETR4, apenas como exemplo',
])
def test_unclear_or_hypothetical_messages_never_authorize_write(message):
    assert not may_register(message, trade())


@pytest.mark.parametrize('message', ['Vendi 4000 PETR4', 'Eu já comprei 4000 PETR4',
                                     'Registre a venda de 4000 PETR4'])
def test_explicit_actual_trade_can_be_registered(message):
    assert may_register(message, trade())


def test_future_date_cannot_be_recorded_as_completed():
    assert not may_register('Vendi 4000 PETR4', trade(data_operacao=date.today()+timedelta(days=1)))


def test_original_question_with_failed_extraction_looks_up_history(db):
    llm = Mock()
    result = AcoesAgent().process(
        'Se eu vender hoje PETR4 a 4000 a 51 reais hoje dia 02/10',
        None, db, 'alice', llm)
    assert 'R$ 40,00' in result['response']
    assert 'modalidade' in result['response']
    assert result['calculation_result'] is None
    assert len(get_trades(db, user_id='alice')) == 1
    llm.chat.assert_not_called()


def test_partial_query_is_scoped_to_current_user(db):
    result = AcoesAgent().process('Se eu vender PETR4', None, db, 'bob', Mock())
    assert 'Não encontrei preço médio' in result['response']
    assert 'R$ 40,00' not in result['response']


def test_multiple_tickers_do_not_select_an_arbitrary_cost():
    lookup = Mock()
    assert history_clarification('Simule PETR4 e VALE3', lookup) is None
    lookup.assert_not_called()


def test_general_route_can_look_up_price_without_full_trade(db, monkeypatch):
    llm = Mock()
    llm.classify_intent.return_value = {'tipo': 'pergunta', 'confianca': .9}
    monkeypatch.setattr(orchestrator, 'get_claude_client', lambda: llm)
    answer = orchestrator.Orchestrator().process('Qual meu preço médio de PETR4?', db, 'alice')
    assert 'R$ 40,00' in answer.response
    llm.answer_question.assert_not_called()


def fake_tools(claude, system, message, t, context, lookup):
    cost = lookup()
    assert cost == 40
    return 'Cálculo concluído.', AcoesCalculator().calculate_result(t, average_price=cost)


def test_repeated_simulations_never_reduce_position(db, monkeypatch):
    monkeypatch.setattr(base_agent, 'run_tool_chat', fake_tools)
    for _ in range(2):
        answer = AcoesAgent().process('Se eu vender 4000 PETR4, operação comum',
                                     trade(), db, 'alice', Mock())
        assert 'Simulação: nenhuma operação foi registrada.' in answer['response']
        assert answer['calculation_result'].ganho_prejuizo_bruto == 44000
        assert 'Simulação' in answer['calculation_result'].mensagem
    assert len(get_trades(db, user_id='alice')) == 1
    assert get_average_price(db, user_id='alice', ativo='PETR4') == 40


def test_simulation_with_real_mcp_and_scripted_llm_keeps_position(db):
    from tests.test_llm_tool_chat import LLM, successful
    answer = AcoesAgent().process('Simule a venda de 4000 PETR4, operação comum',
                                 trade(), db, 'alice', LLM(successful()))
    assert answer['calculation_result'].ganho_prejuizo_bruto == 44000
    assert answer['calculation_result'].ir_devido == 6600
    assert 'Simulação' in answer['response']
    assert len(get_trades(db, user_id='alice')) == 1
    assert get_average_price(db, user_id='alice', ativo='PETR4') == 40


def test_specialist_route_failed_extraction_returns_stored_cost(db, monkeypatch):
    llm = Mock()
    llm.classify_intent.return_value = {'tipo': 'acao', 'confianca': .95}
    llm.parse_trade.return_value = None
    monkeypatch.setattr(orchestrator, 'get_claude_client', lambda: llm)
    answer = orchestrator.Orchestrator().process(
        'Se eu vender hoje PETR4 a 4000 a 51 reais hoje dia 02/10', db, 'alice')
    assert 'R$ 40,00' in answer.response
    assert answer.calculation_result is None
    assert len(get_trades(db, user_id='alice')) == 1


def test_actual_sale_still_persists_once(db, monkeypatch):
    monkeypatch.setattr(base_agent, 'run_tool_chat', fake_tools)
    answer = AcoesAgent().process('Vendi 4000 PETR4, operação comum',
                                 trade(), db, 'alice', Mock())
    assert 'Venda registrada' in answer['response']
    assert len(get_trades(db, user_id='alice')) == 2
    assert get_average_price(db, user_id='alice', ativo='PETR4') is None


def test_hypothetical_purchase_does_not_change_average(db):
    answer = AcoesAgent().process('Se eu comprar 4000 PETR4 a 51',
                                 trade(tipo_operacao='compra'), db, 'alice', Mock())
    assert 'Nenhuma operação foi registrada' in answer['response']
    assert len(get_trades(db, user_id='alice')) == 1
    assert get_average_price(db, user_id='alice', ativo='PETR4') == 40


def parser(*responses):
    client = ClaudeClient.__new__(ClaudeClient)
    client.model_parser = 'offline-test'
    client._call_model = Mock(side_effect=[json.dumps(r) for r in responses])
    return client


def test_incomplete_extraction_retries_once_and_keeps_explicit_data():
    client = parser({'erro': 'campo ausente: quantidade'}, trade().model_dump(mode='json'))
    answer = client.parse_trade('Se eu vender PETR4 a 4000 a 51 reais dia 02/10, operação comum')
    assert answer.quantidade == 4000
    assert answer.preco_unitario == 51
    assert answer.preco_medio_informado is None
    assert client._call_model.call_count == 2
    assert 'PETR4 a 4000 a 51 reais' in client._call_model.call_args.args[1]


def test_ambiguous_data_does_not_get_fabricated():
    client = parser(*[{'erro': 'campo ausente: quantidade'}]*2)
    assert client.parse_trade('Se eu vender PETR4') is None
    assert client._call_model.call_count == 2


def test_undeclared_sale_modality_is_not_silently_swing():
    data = trade().model_dump(mode='json')
    del data['classificacao']
    assert parser(data).parse_trade('Se eu vender PETR4 a 4000 a 51 reais') is None


@pytest.mark.parametrize('payload', [[], None, 123, 'not an object'])
def test_invalid_parser_payload_is_rejected(payload):
    assert parser(payload).parse_trade('PETR4') is None
