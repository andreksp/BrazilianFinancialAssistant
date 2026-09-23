"""Application MCP server: stateless, stdio-only, reuse existing calculators."""
from pathlib import Path
import sys, math
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from mcp.server.fastmcp import FastMCP
from app.models.trade import TradeInput, AssetType, OperationType
from app.calculations.equity.acoes import AcoesCalculator
from app.calculations.equity.bdrs import BDRCalculator
from app.calculations.equity.fiis import FIICalculator
from app.calculations.equity.opcoes import OpcoesCalculator
from app.calculations.derivatives.futuros import FuturosCalculator
from app.calculations.lending.emprestimo import EmprestimoCalculator
from app.calculations.crypto.criptomoedas import CriptomoedaCalculator
mcp = FastMCP('Financial calculations runtime')
CALCULATORS = {AssetType.ACAO:AcoesCalculator, AssetType.BDR:BDRCalculator,
    AssetType.FII:FIICalculator, AssetType.OPCAO:OpcoesCalculator,
    AssetType.FUTURO_DOLAR:FuturosCalculator, AssetType.FUTURO_INDICE:FuturosCalculator,
    AssetType.EMPRESTIMO_ACOES:EmprestimoCalculator, AssetType.CRIPTO:CriptomoedaCalculator}

@mcp.tool()
def fee_policy(asset_type: str) -> dict:
    """Disclose cost policy. Not a live or validated current B3 tariff quote."""
    asset = AssetType(asset_type)
    return {'asset_type':asset.value, 'source':'existing Python calculators; user supplied transaction costs',
            'effective_date':None, 'live_tariffs':False,
            'warning':'Custos informados são preferidos. Eventuais tarifas parametrizadas são estimativas legadas, sem vigência validada; não constituem tabela atual da B3.'}

@mcp.tool()
def calculate_trade(trade: dict, average_price: float | None = None) -> dict:
    """Validate inputs and execute the existing calculator; never persist a trade."""
    try:
        parsed = TradeInput.model_validate(trade)
        if parsed.tipo_operacao != OperationType.VENDA:
            raise ValueError('Esta ferramenta calcula vendas/remuneração; compras são registradas pelo backend.')
        cost = parsed.preco_medio_informado if parsed.preco_medio_informado is not None else average_price
        if parsed.tipo_ativo != AssetType.EMPRESTIMO_ACOES and (cost is None or not math.isfinite(cost) or cost <= 0):
            raise ValueError('Informe o custo médio positivo antes de calcular.')
        result = CALCULATORS[parsed.tipo_ativo]().calculate_result(parsed, average_price=cost)
        return {'ok':True,'result':result.model_dump(mode='json')}
    except (ValueError, AssertionError) as exc:
        return {'ok':False,'error':str(exc)}

if __name__ == '__main__':mcp.run(transport='stdio')
