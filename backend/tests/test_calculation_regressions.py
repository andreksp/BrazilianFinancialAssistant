"""Regression cases for the independent MCP/tool-use audit."""
import pytest
from app.models.trade import TradeInput
from app.calculations.equity.fiis import FIICalculator
from app.calculations.equity.opcoes import OpcoesCalculator


@pytest.fixture(params=[('fii', FIICalculator, .20), ('opcao', OpcoesCalculator, .15)])
def case(request):
    asset, calculator, rate = request.param
    trade = TradeInput(ativo='TEST11', tipo_ativo=asset, tipo_operacao='venda',
                      quantidade=10, preco_unitario=110,
                      data_operacao='2026-09-20', custos_operacao=22)
    return trade, calculator(), rate


@pytest.mark.parametrize('cost', [None, 0, -1, float('nan'), float('inf')])
def test_direct_calculator_rejects_invalid_cost(case, cost):
    trade, calculator, _ = case
    with pytest.raises(ValueError, match='custo médio'):
        calculator.calculate_result(trade, average_price=cost)


def test_tax_deducts_actual_costs(case):
    trade, calculator, rate = case
    result = calculator.calculate_result(trade, average_price=100)
    assert result.ganho_prejuizo_bruto == 100
    assert result.ganho_prejuizo_liquido == 78
    assert result.ir_devido == round(78 * rate, 2)
    assert not result.isenção_aplicada


def test_costs_exceeding_gain_produce_zero_tax(case):
    trade, calculator, _ = case
    result = calculator.calculate_result(trade.model_copy(update={'custos_operacao': 101}), average_price=100)
    assert result.ir_devido == 0


def test_explicit_cost_has_priority(case):
    trade, calculator, rate = case
    result = calculator.calculate_result(trade.model_copy(update={'preco_medio_informado': 105}), average_price=100)
    assert result.ir_devido == round(28 * rate, 2)
