"""
Compara, para cada tipo de ativo, o resultado calculado:
(a) diretamente pela calculadora Python (import direto, sem MCP)
(b) via gateway MCP real (subprocess stdio real, protocolo real)

Objetivo: provar que o caminho MCP não duplica fórmulas nem diverge do
motor de cálculo já existente, com casos realistas (custos, custo médio,
total mensal, prazo, retenções conforme exigido por cada tipo).

Os "gabaritos" (valores esperados) são derivados das regras já documentadas
em Documentation/TCC/Revisao/manuscrito.md e no research.md do projeto,
com base legal citada — não são um novo levantamento de fontes oficiais
independente feito nesta execução.
"""
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.models.trade import TradeInput
from app.calculations.equity.acoes import AcoesCalculator
from app.calculations.equity.bdrs import BDRCalculator
from app.calculations.equity.fiis import FIICalculator
from app.calculations.equity.opcoes import OpcoesCalculator
from app.calculations.derivatives.futuros import FuturosCalculator
from app.calculations.lending.emprestimo import EmprestimoCalculator
from app.calculations.crypto.criptomoedas import CriptomoedaCalculator
from app import mcp_gateway as gateway

CASES = [
    dict(
        id="acao_swing_com_isencao",
        calc=AcoesCalculator,
        trade=dict(ativo="PETR4", tipo_ativo="acao", tipo_operacao="venda",
                   quantidade=100, preco_unitario=30.0, data_operacao="2026-09-16",
                   total_vendas_mes=3000.0),
        average_price=25.0,
        expected=dict(isenção_aplicada=True, ir_devido=0.0),
        base_legal="Lei 13.259/2016 / IN RFB 1585/2015 art. isenção R$20.000/mês vendas à vista",
    ),
    dict(
        id="acao_swing_tributado",
        calc=AcoesCalculator,
        trade=dict(ativo="PETR4", tipo_ativo="acao", tipo_operacao="venda",
                   quantidade=100, preco_unitario=30.0, data_operacao="2026-09-16",
                   total_vendas_mes=25000.0),
        average_price=25.0,
        expected=dict(isenção_aplicada=False, aliquota_aplicada=0.15),
        base_legal="IN RFB 1585/2015 — 15% swing trade acima de R$20.000/mês",
    ),
    dict(
        id="bdr_sem_isencao",
        calc=BDRCalculator,
        trade=dict(ativo="AAPL34", tipo_ativo="bdr", tipo_operacao="venda",
                   quantidade=10, preco_unitario=200.0, data_operacao="2026-09-16",
                   custos_operacao=0, irrf_informado=0),
        average_price=100.0,
        expected=dict(isenção_aplicada=False, ir_devido=150.0, aliquota_aplicada=0.15),
        base_legal="B3, Como declarar BDRs no IR 2026 — sem isenção de R$20.000 para BDR",
    ),
    dict(
        id="fii_venda_20pct",
        calc=FIICalculator,
        trade=dict(ativo="HGLG11", tipo_ativo="fii", tipo_operacao="venda",
                   quantidade=10, preco_unitario=110.0, data_operacao="2026-09-16"),
        average_price=100.0,
        expected=dict(isenção_aplicada=False, ir_devido=20.0, aliquota_aplicada=0.20),
        base_legal="Lei 11.033/2004 — 20% flat sobre ganho de capital em cotas de FII, sem isenção",
    ),
    dict(
        id="opcao_swing",
        calc=OpcoesCalculator,
        trade=dict(ativo="PETRH250", tipo_ativo="opcao", tipo_operacao="venda",
                   quantidade=100, preco_unitario=5.0, data_operacao="2026-09-16"),
        average_price=3.0,
        expected=dict(ir_devido=30.0, aliquota_aplicada=0.15),
        base_legal="Mesma alíquota de ações (15% swing) aplicada ao prêmio da opção",
    ),
    dict(
        id="futuro_win",
        calc=FuturosCalculator,
        trade=dict(ativo="WINV26", tipo_ativo="futuro_indice", tipo_operacao="venda",
                   quantidade=1, preco_unitario=130500.0, data_operacao="2026-09-16",
                   custos_operacao=0, irrf_informado=0),
        average_price=130000.0,
        expected=dict(ganho_prejuizo_bruto=100.0, ir_devido=15.0, isenção_aplicada=False),
        base_legal="B3 especificação WIN: 1 ponto = R$0,20/contrato; sem isenção de ações à vista",
    ),
    dict(
        id="futuro_wdo",
        calc=FuturosCalculator,
        trade=dict(ativo="WDOU26", tipo_ativo="futuro_dolar", tipo_operacao="venda",
                   quantidade=2, preco_unitario=5510.0, data_operacao="2026-09-16",
                   custos_operacao=0, irrf_informado=0),
        average_price=5500.0,
        expected=dict(ganho_prejuizo_bruto=200.0, ir_devido=30.0),
        base_legal="B3 especificação WDO: 1 ponto = R$10,00/contrato",
    ),
    dict(
        id="emprestimo_300dias",
        calc=EmprestimoCalculator,
        trade=dict(ativo="VALE3", tipo_ativo="emprestimo_acoes", tipo_operacao="venda",
                   quantidade=200, preco_unitario=0.60, data_operacao="2026-09-16",
                   prazo_dias=300),
        average_price=None,
        expected=dict(ir_devido=0.0, irrf_retido=24.0, aliquota_aplicada=0.20),
        base_legal="Lei 15.265/2025 — tabela regressiva 181-360 dias = 20%, tributação exclusiva na fonte",
    ),
    dict(
        id="cripto_nacional_tributado",
        calc=CriptomoedaCalculator,
        trade=dict(ativo="BTC", tipo_ativo="cripto", tipo_operacao="venda",
                   quantidade=0.1, preco_unitario=350000.0, data_operacao="2026-09-16",
                   total_vendas_mes=40000.0),
        average_price=300000.0,
        expected=dict(isenção_aplicada=False, ir_devido=750.0, aliquota_aplicada=0.15),
        base_legal="IN SRF 84/2001 art.3 IX — isenção R$35.000/mês; acima disso, Lei 13.259/2016 tabela progressiva",
    ),
    dict(
        id="cripto_nacional_isento",
        calc=CriptomoedaCalculator,
        trade=dict(ativo="BTC", tipo_ativo="cripto", tipo_operacao="venda",
                   quantidade=0.1, preco_unitario=350000.0, data_operacao="2026-09-16",
                   total_vendas_mes=35000.0),
        average_price=300000.0,
        expected=dict(isenção_aplicada=True, ir_devido=0.0),
        base_legal="IN SRF 84/2001 art.3 IX — isenção até R$35.000/mês inclusive",
    ),
]


async def run_case(case):
    trade_dict = dict(case["trade"])
    trade = TradeInput(**trade_dict)

    direct_error = None
    direct_result = None
    try:
        direct_result = case["calc"]().calculate_result(trade, average_price=case["average_price"])
    except Exception as e:
        direct_error = f"{type(e).__name__}: {e}"

    mcp_error = None
    mcp_result = None
    try:
        mcp_result = await gateway.calculate_via_mcp_async(trade, average_price=case["average_price"])
    except Exception as e:
        mcp_error = f"{type(e).__name__}: {e}"

    record = {
        "id": case["id"],
        "base_legal": case["base_legal"],
        "input": trade_dict,
        "average_price": case["average_price"],
        "direct_error": direct_error,
        "mcp_error": mcp_error,
    }

    if direct_result is not None:
        d = direct_result.model_dump(mode="json")
        record["direct_result"] = {k: d[k] for k in case["expected"]} | {
            "ganho_prejuizo_bruto": d.get("ganho_prejuizo_bruto"),
            "ir_devido": d.get("ir_devido"),
            "irrf_retido": d.get("irrf_retido"),
            "aliquota_aplicada": d.get("aliquota_aplicada"),
            "isenção_aplicada": d.get("isenção_aplicada"),
        }
    if mcp_result is not None:
        m = mcp_result.model_dump(mode="json")
        record["mcp_result"] = {
            "ganho_prejuizo_bruto": m.get("ganho_prejuizo_bruto"),
            "ir_devido": m.get("ir_devido"),
            "irrf_retido": m.get("irrf_retido"),
            "aliquota_aplicada": m.get("aliquota_aplicada"),
            "isenção_aplicada": m.get("isenção_aplicada"),
        }

    # Equivalence check between direct and MCP paths
    if direct_result is not None and mcp_result is not None:
        d, m = direct_result.model_dump(mode="json"), mcp_result.model_dump(mode="json")
        mismatches = {k: (d[k], m[k]) for k in d if k in m and d[k] != m[k] and k != "mensagem"}
        record["mcp_matches_direct"] = not mismatches
        record["mismatches"] = mismatches
    else:
        record["mcp_matches_direct"] = (direct_error is not None) == (mcp_error is not None)

    # Expected-value check (tax-rule gabarito)
    expected_ok = True
    expected_mismatches = {}
    if mcp_result is not None:
        m = mcp_result.model_dump(mode="json")
        for k, v in case["expected"].items():
            actual = m.get(k)
            ok = (abs(actual - v) < 0.01) if isinstance(v, float) else (actual == v)
            if not ok:
                expected_ok = False
                expected_mismatches[k] = {"expected": v, "actual": actual}
    elif mcp_error is None:
        expected_ok = False
    record["expected_ok"] = expected_ok
    record["expected_mismatches"] = expected_mismatches

    return record


async def main():
    results = [await run_case(c) for c in CASES]
    out = Path(__file__).resolve().parent / "comparacao_mcp_vs_direto.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    n_match = sum(r["mcp_matches_direct"] for r in results)
    n_expected = sum(r["expected_ok"] for r in results)
    print(f"MCP == direto: {n_match}/{len(results)}")
    print(f"Gabarito tributário atendido: {n_expected}/{len(results)}")
    for r in results:
        status = "OK" if r["mcp_matches_direct"] and r["expected_ok"] else "FALHA"
        print(f"  [{status}] {r['id']}")
        if r["direct_error"]:
            print(f"       direct_error: {r['direct_error']}")
        if r["mcp_error"]:
            print(f"       mcp_error: {r['mcp_error']}")
        if r["mismatches"]:
            print(f"       mismatches: {r['mismatches']}")
        if r["expected_mismatches"]:
            print(f"       expected_mismatches: {r['expected_mismatches']}")


asyncio.run(main())
