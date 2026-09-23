"""Backend-controlled MCP dispatch; no direct-calculator fallback."""
import asyncio,json,logging,sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.models.trade import TaxCalculationResult
log=logging.getLogger(__name__)
SERVER=Path(__file__).resolve().parents[2]/'mcp_server'/'server.py'

def unpack(response):
    if response.isError:raise ValueError('Falha na ferramenta MCP; cálculo não executado com segurança.')
    if response.structuredContent is not None:return response.structuredContent
    return json.loads(next(c.text for c in response.content if c.type=='text'))

async def calculate_via_mcp_async(trade, average_price=None):
    async def invoke():
        params=StdioServerParameters(command=sys.executable,args=[str(SERVER)],env={'PYTHONIOENCODING':'utf-8'})
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write,read_timeout_seconds=timedelta(seconds=20)) as session:
                await session.initialize()
                policy=unpack(await session.call_tool('fee_policy',{'asset_type':trade.tipo_ativo.value}))
                payload=unpack(await session.call_tool('calculate_trade',{'trade':trade.model_dump(mode='json'),'average_price':average_price}))
                if not payload.get('ok'):raise ValueError(payload.get('error','Dados insuficientes para cálculo.'))
                result=TaxCalculationResult.model_validate(payload['result'])
                if (result.ativo,result.tipo_ativo,result.quantidade)!=(trade.ativo,trade.tipo_ativo,trade.quantidade):
                    raise ValueError('Resposta MCP incompatível com a operação solicitada.')
                if trade.custos_operacao is None:
                    result.mensagem=((result.mensagem or '')+' '+policy['warning']).strip()
                log.info('MCP tools=fee_policy,calculate_trade transport=stdio status=ok asset_type=%s',trade.tipo_ativo.value)
                return result
    try:return await asyncio.wait_for(invoke(),timeout=30)
    except Exception as exc:
        def detail(e):
            if isinstance(e,ValueError):return str(e)
            for child in getattr(e,'exceptions',[]):
                found=detail(child)
                if found:return found
            return None
        raise ValueError(detail(exc) or 'MCP indisponível ou resposta inválida; nenhum cálculo local alternativo foi executado.') from exc

def calculate_via_mcp(trade, average_price=None):
    try:asyncio.get_running_loop()
    except RuntimeError:return asyncio.run(calculate_via_mcp_async(trade,average_price))
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda:asyncio.run(calculate_via_mcp_async(trade,average_price))).result(timeout=40)
