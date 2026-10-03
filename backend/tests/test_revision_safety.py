"""New contract: absent facts must not silently become a tax calculation."""
import pytest
from app.models.trade import TradeInput
from app.calculations.crypto.criptomoedas import CriptomoedaCalculator
from app.calculations.equity.acoes import AcoesCalculator
from app.calculations.derivatives.futuros import FuturosCalculator
from app.calculations.lending.emprestimo import EmprestimoCalculator

def trade(asset,**kw):
    return TradeInput(ativo={'cripto':'BTC','acao':'PETR4','futuro_indice':'WINV26','emprestimo_acoes':'PETR4'}[asset],
        tipo_ativo=asset,tipo_operacao='venda',quantidade=1,preco_unitario=100,data_operacao='2026-09-01',**kw)

@pytest.mark.parametrize('asset,calculator',[('acao',AcoesCalculator),('cripto',CriptomoedaCalculator)])
def test_missing_month_is_rejected(asset,calculator):
    with pytest.raises(ValueError,match='total completo'):calculator().calculate_result(trade(asset),average_price=50)

@pytest.mark.parametrize('asset,calculator',[('acao',AcoesCalculator),('cripto',CriptomoedaCalculator)])
def test_missing_cost_basis_is_rejected(asset,calculator):
    with pytest.raises(ValueError,match='custo médio'):calculator().calculate_result(trade(asset,total_vendas_mes=100))

def test_foreign_crypto_not_misrepresented_as_monthly():
    with pytest.raises(ValueError,match='anual'):
        CriptomoedaCalculator().calculate_result(trade('cripto',exchange_estrangeira=True),average_price=50)

def test_missing_lending_term():
    with pytest.raises(ValueError,match='prazo'):EmprestimoCalculator().calculate_result(trade('emprestimo_acoes'))

def test_futures_requires_actual_cost_and_withholding():
    with pytest.raises(ValueError,match='custos'):FuturosCalculator().calculate_result(trade('futuro_indice'),average_price=90)

def test_progressive_slices():
    assert CriptomoedaCalculator().progressive_tax(6000000)==925000
