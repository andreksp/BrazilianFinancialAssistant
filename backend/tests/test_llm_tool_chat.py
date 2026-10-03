import asyncio
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from app.agents import tool_chat
from app.models.trade import TradeInput
from app.calculations.equity.fiis import FIICalculator


def trade(**extra):
    data=dict(ativo='HGLG11', tipo_ativo='fii', tipo_operacao='venda', quantidade=10,
              preco_unitario=110, data_operacao='2026-09-20', custos_operacao=0)
    data.update(extra)
    return TradeInput(**data)


def call(name, ident, **args):
    return {'type':'tool_use', 'id':ident, 'name':name, 'input':args}


def reply(*blocks, stop='tool_use'):
    return SimpleNamespace(content=list(blocks), stop_reason=stop)


def done(text='O resultado calculado é R$ 20 de imposto.'):
    return reply({'type':'text','text':text}, stop='end_turn')


class LLM:
    def __init__(self, replies):
        self.replies=iter(replies)
        self.requests=[]
    def tool_turn(self, system, messages, tools):
        self.requests.append(deepcopy(messages))
        return next(self.replies)


class Session:
    def __init__(self):self.calls=[]
    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=n) for n in ['fee_policy','calculate_trade']])
    async def call_tool(self, name, args):
        self.calls.append((name,args))
        if name=='fee_policy':out={'warning':'Estimativas sem vigência validada','live_tariffs':False}
        else:
            t=TradeInput.model_validate(args['trade'])
            out={'ok':True,'result':FIICalculator().calculate_result(t,average_price=args['average_price']).model_dump(mode='json')}
        return SimpleNamespace(isError=False,structuredContent=out)


def run(llm, session=None, lookup=None, **extra):
    return asyncio.run(tool_chat.run_session(session or Session(), llm, 'Sistema', 'Venda', trade(**extra), '', lookup or (lambda:100)))


def successful():
    return [reply(call('consultar_preco_medio','c'),call('fee_policy','p')),
            reply(call('calculate_trade','t')),done()]


def test_llm_selects_tools_and_receives_results():
    llm=LLM(successful());session=Session();lookup=Mock(return_value=100)
    text,result=run(llm,session,lookup)
    assert result.ir_devido==20
    lookup.assert_called_once_with()
    assert [n for n,a in session.calls]==['fee_policy','calculate_trade']
    assert llm.requests[-1][-1]['content'][0]['tool_use_id']=='t'
    assert all('user_id' not in args for name,args in session.calls)


def test_real_mcp_with_scripted_llm():
    text,result=tool_chat.run_tool_chat(LLM(successful()),'Sistema','Venda',trade(),'',lambda:100)
    assert result.ir_devido==20


def test_real_mcp_wrapper_preserves_missing_cost_message():
    with pytest.raises(ValueError, match='custo médio'):
        tool_chat.run_tool_chat(LLM(successful()), 'Sistema', 'Venda', trade(), '', lambda: None)


@pytest.mark.parametrize('asset', ['fii', 'acao'])
def test_missing_lookup_then_clarification_preserves_specific_message(asset):
    session = Session()
    llm = LLM([reply(call('consultar_preco_medio', 'c'), call('fee_policy', 'p')),
               done('Poderia informar seu preço médio?')])
    with pytest.raises(ValueError, match='custo médio de aquisição de HGLG11'):
        run(llm, session, lambda: None, tipo_ativo=asset)
    assert [name for name, _ in session.calls] == ['fee_policy']
    output = llm.requests[-1][-1]['content'][0]
    assert output['is_error'] is True
    assert 'reenvie os dados completos' in output['content']


def test_missing_lookup_cannot_turn_invented_model_result_into_success():
    llm = LLM([reply(call('consultar_preco_medio', 'c')), done('Imposto zero. Venda registrada.')])
    with pytest.raises(ValueError, match='custo médio') as exc:
        run(llm, lookup=lambda: None)
    assert 'Imposto zero' not in str(exc.value)


def test_agent_real_mcp_clarification_without_calculation_does_not_save(monkeypatch):
    from app.agents import base_agent
    from app.agents.fii_agent import FIIAgent
    monkeypatch.setattr(base_agent, 'get_chroma_client', lambda: None)
    monkeypatch.setattr(base_agent, 'get_average_price', Mock(return_value=None))
    save = Mock()
    monkeypatch.setattr(base_agent, 'save_trade', save)
    monkeypatch.setattr(base_agent, 'save_chat', Mock())
    llm = LLM([reply(call('fee_policy', 'p'), call('consultar_preco_medio', 'c')),
               done('Qual foi o preço médio de compra?')])
    result = FIIAgent().process('Venda', trade(), Mock(), 'test-user', llm)
    assert 'custo médio de aquisição de HGLG11' in result['response']
    assert 'reenvie os dados completos' in result['response']
    assert result['calculation_result'] is None
    save.assert_not_called()


def test_wrapper_unwraps_nested_validation_errors(monkeypatch):
    def fail(coro):
        coro.close()
        raise ExceptionGroup('outer', [ExceptionGroup('inner', [ValueError('Informe o custo médio')])])
    monkeypatch.setattr(tool_chat.asyncio, 'run', fail)
    with pytest.raises(ValueError, match='Informe o custo médio'):
        tool_chat.run_tool_chat(None, '', '', trade(), '', lambda: None)


def test_wrapper_hides_transport_details(monkeypatch):
    def fail(coro):
        coro.close()
        raise RuntimeError('private transport detail')
    monkeypatch.setattr(tool_chat.asyncio, 'run', fail)
    with pytest.raises(ValueError, match='Falha na comunicação') as exc:
        tool_chat.run_tool_chat(None, '', '', trade(), '', lambda: None)
    assert 'private transport detail' not in str(exc.value)


def test_no_tool_use_does_not_calculate():
    session=Session()
    with pytest.raises(ValueError,match='não concluiu'):run(LLM([done('Inventei o imposto')]),session)
    assert session.calls==[]


@pytest.mark.parametrize('bad', [call('consultar_preco_medio','bad',user_id='outro'),call('calculate_trade','bad',average_price=1),call('delete_database','bad')])
def test_rejects_untrusted_arguments_and_tools(bad):
    llm=LLM([reply(bad),*successful()]);lookup=Mock(return_value=100)
    run(llm,lookup=lookup)
    assert llm.requests[1][-1]['content'][0]['is_error']
    lookup.assert_called_once_with()


def test_enforces_policy_before_calculation():
    llm=LLM([reply(call('calculate_trade','early')),*successful()]);session=Session()
    run(llm,session)
    assert llm.requests[1][-1]['content'][0]['is_error']
    assert len(session.calls)==2


def test_explicit_cost_needs_no_database_lookup():
    lookup=Mock(side_effect=AssertionError('No DB lookup expected'))
    llm=LLM([reply(call('fee_policy','p')),reply(call('calculate_trade','t')),done()])
    assert run(llm,lookup=lookup,preco_medio_informado=105)[1].ir_devido==10


def test_repeated_calculation_cached():
    llm=LLM([*successful()[:-1],reply(call('calculate_trade','again')),done()]);session=Session()
    run(llm,session)
    assert len(session.calls)==2


def test_round_limit():
    llm=LLM([reply(call('fee_policy',str(i))) for i in range(6)])
    with pytest.raises(ValueError,match='rodadas'):run(llm)


def test_truncated_response_rejected():
    llm=LLM([*successful()[:-1],reply({'type':'text','text':'incompleto'},stop='max_tokens')])
    with pytest.raises(ValueError,match='incompleta'):run(llm)


def test_invalid_result_rejected():
    class Bad(Session):
        async def call_tool(self,name,args):
            response=await super().call_tool(name,args)
            if name=='calculate_trade':response.structuredContent['result']['ativo']='OUTRO'
            return response
    with pytest.raises(ValueError,match='Resposta MCP incompatível'):run(LLM(successful()),Bad())


def test_agent_does_not_persist_failed_tool_flow(monkeypatch):
    from app.agents import base_agent
    from app.agents.fii_agent import FIIAgent
    monkeypatch.setattr(base_agent,'get_chroma_client',lambda:None)
    monkeypatch.setattr(base_agent,'run_tool_chat',Mock(side_effect=ValueError('Recusado')))
    save=Mock();monkeypatch.setattr(base_agent,'save_trade',save)
    monkeypatch.setattr(base_agent,'save_chat',Mock())
    result=FIIAgent().process('Venda',trade(),Mock(),'user-a',Mock())
    save.assert_not_called()
    assert result['calculation_result'] is None


def test_chat_route_runs_in_worker_thread():
    import inspect
    from app.api.chat import send_message
    assert not inspect.iscoroutinefunction(send_message)


def test_real_mcp_missing_cost_refuses():
    with pytest.raises(ValueError):
        tool_chat.run_tool_chat(LLM(successful()),'Sistema','Venda',trade(),'',lambda:None)


def test_agent_real_wrapper_preserves_validation_and_does_not_save(monkeypatch):
    from app.agents import base_agent
    from app.agents.fii_agent import FIIAgent
    monkeypatch.setattr(base_agent, 'get_chroma_client', lambda: None)
    monkeypatch.setattr(base_agent, 'get_average_price', Mock(return_value=None))
    save = Mock()
    monkeypatch.setattr(base_agent, 'save_trade', save)
    monkeypatch.setattr(base_agent, 'save_chat', Mock())
    db = Mock()
    result = FIIAgent().process('Venda', trade(), db, 'test-user', LLM(successful()))
    assert 'custo médio' in result['response']
    assert 'Falha na comunicação' not in result['response']
    assert result['calculation_result'] is None
    save.assert_not_called()
    db.rollback.assert_called_once()


@pytest.mark.parametrize('asset,expected', [('fii', 15.6), ('opcao', 11.7)])
def test_real_mcp_deducts_costs(asset, expected):
    _, result = tool_chat.run_tool_chat(LLM(successful()), 'Sistema', 'Venda',
                                      trade(tipo_ativo=asset, custos_operacao=22), '', lambda: 100)
    assert result.ir_devido == expected


def test_duplicate_ids_rejected():
    llm=LLM([reply(call('fee_policy','same')),reply(call('fee_policy','same'))])
    with pytest.raises(ValueError,match='repetido'):run(llm)


def test_call_limit_rejects_before_execution():
    session=Session()
    with pytest.raises(ValueError,match='chamadas'):
        run(LLM([reply(*(call('fee_policy',str(i)) for i in range(9)))]),session)
    assert session.calls==[]


def test_tool_turn_uses_auto_and_preserves_sdk_response():
    from app.llm.claude_client import ClaudeClient
    client=ClaudeClient.__new__(ClaudeClient)
    client.model_explainer='test-model';client.client=Mock()
    messages=[{'role':'user','content':'test'}]
    result=client.tool_turn('system',messages,[])
    request=client.client.with_options.return_value.messages.create
    assert request.call_args.kwargs['tool_choice']=={'type':'auto'}
    assert request.call_args.kwargs['messages'] is messages
    assert result is request.return_value


def test_agent_binds_user_and_persists_once(monkeypatch):
    from app.agents import base_agent
    from app.agents.fii_agent import FIIAgent
    monkeypatch.setattr(base_agent,'get_chroma_client',lambda:None)
    lookup=Mock(return_value=100);monkeypatch.setattr(base_agent,'get_average_price',lookup)
    result=FIICalculator().calculate_result(trade(),average_price=100)
    def tool_run(claude,system,message,t,context,bound_lookup):
        assert bound_lookup()==100
        return 'Concluído',result
    monkeypatch.setattr(base_agent,'run_tool_chat',tool_run)
    save=Mock();monkeypatch.setattr(base_agent,'save_trade',save)
    monkeypatch.setattr(base_agent,'save_chat',Mock())
    db=Mock()
    FIIAgent().process('Vendi 10 cotas de HGLG11',trade(),db,'trusted-user',Mock())
    lookup.assert_called_once_with(db,user_id='trusted-user',ativo='HGLG11')
    assert save.call_count==1
