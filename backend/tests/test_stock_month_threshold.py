import pytest
from app.models.trade import TradeInput
from app.calculations.equity.acoes import AcoesCalculator
from app.mcp_gateway import calculate_via_mcp


def trade(value=204000, **extra):
    data = dict(ativo='PETR4', tipo_ativo='acao', tipo_operacao='venda',
                quantidade=4000, preco_unitario=value / 4000,
                data_operacao='2026-10-02', classificacao='swing',
                custos_operacao=0, irrf_informado=0)
    data.update(extra)
    return TradeInput(**data)


@pytest.mark.parametrize('value', [20000.01, 180000, 204000])
def test_sale_alone_over_threshold_needs_no_month_total(value):
    t = trade(value)
    result = AcoesCalculator().calculate_result(t, average_price=1)
    assert not result.isenção_aplicada
    assert result.aliquota_aplicada == .15
    assert t.total_vendas_mes is None
    assert 'não representa a apuração completa' in result.mensagem


@pytest.mark.parametrize('value', [4500, 19999.99, 20000])
def test_at_or_below_threshold_still_requires_month_total(value):
    with pytest.raises(ValueError, match='total completo'):
        AcoesCalculator().calculate_result(trade(value), average_price=1)


@pytest.mark.parametrize('total', [0, 20000, 180000])
def test_contradictory_month_total_remains_rejected(total):
    with pytest.raises(ValueError, match='total completo'):
        AcoesCalculator().calculate_result(trade(total_vendas_mes=total), average_price=40)


def test_explicit_total_at_threshold_still_exempt():
    result = AcoesCalculator().calculate_result(trade(20000, total_vendas_mes=20000), average_price=1)
    assert result.isenção_aplicada
    assert result.ir_devido == 0


def test_day_trade_still_does_not_require_month_total():
    result = AcoesCalculator().calculate_result(trade(classificacao='day_trade'), average_price=40)
    assert result.ir_devido == 8800


def test_real_mcp_without_month_total():
    result = calculate_via_mcp(trade(), 40)
    assert result.ir_devido == 6600
    assert not result.isenção_aplicada
    assert 'não representa a apuração completa' in result.mensagem
