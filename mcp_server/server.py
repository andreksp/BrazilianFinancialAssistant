"""
Brazilian Financial Assistant — Internal MCP Server

Development-only tool. NOT deployed with the application.
Provides Claude Code with context and domain knowledge during implementation:
  - Brazilian IR tax rules per asset class
  - B3 fee structures
  - Worked calculation examples
  - Regulation document search
  - Calculation validation
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Brazilian Financial Assistant")

BASE_DIR = Path(__file__).parent.parent
REGULATIONS_DIR = BASE_DIR / "backend" / "data" / "regulations"

# ─── Tax rules ────────────────────────────────────────────────────────────────

_TAX_RULES: dict = {
    "acao": {
        "descricao": "Ações negociadas no mercado à vista (B3)",
        "swing_trade": {
            "aliquota": 0.15,
            "irrf": 0.00005,
            "isencao_mensal": 20000.0,
            "nota": (
                "Isenção se o TOTAL vendido no mês (todas as ações + BDRs) "
                "<= R$20.000. Se ultrapassar, TODO o ganho do mês é tributado."
            ),
        },
        "day_trade": {
            "aliquota": 0.20,
            "irrf": 0.01,
            "isencao_mensal": None,
            "nota": "Day Trade: sem isenção. IRRF = 1% sobre o GANHO (não sobre o valor).",
        },
        "compensacao_prejuizo": "Swing com swing, day com day. Arrastado para meses seguintes (swing).",
        "darf_codigo": 6015,
        "prazo_pagamento": "Último dia útil do mês seguinte à operação",
        "base_legal": "Lei 11.033/2004; IN RFB 1.585/2015",
    },
    "bdr": {
        "descricao": "Brazilian Depositary Receipts — mesmas regras que ações",
        "swing_trade": {
            "aliquota": 0.15,
            "irrf": 0.00005,
            "isencao_mensal": 20000.0,
            "nota": "Isenção compartilhada com ações: R$20.000/mês no total (ações + BDRs).",
        },
        "day_trade": {
            "aliquota": 0.20,
            "irrf": 0.01,
            "isencao_mensal": None,
        },
        "compensacao_prejuizo": "Sim, mesmas regras das ações",
        "darf_codigo": 6015,
        "prazo_pagamento": "Último dia útil do mês seguinte",
        "base_legal": "Resolução CVM 3/2020; IN RFB 1.585/2015",
    },
    "fii": {
        "descricao": "Fundos de Investimento Imobiliário — 20% SEMPRE, sem isenção de R$20k",
        "swing_trade": {
            "aliquota": 0.20,
            "irrf": 0.00005,
            "isencao_mensal": None,
            "nota": "FII: alíquota única de 20%. Sem isenção de R$20.000.",
        },
        "day_trade": {
            "aliquota": 0.20,
            "irrf": 0.01,
            "isencao_mensal": None,
        },
        "rendimentos_mensais": "ISENTOS para pessoa física (distribuição mensal de renda do FII).",
        "compensacao_prejuizo": "Sim, dentro da categoria FII",
        "darf_codigo": 6015,
        "prazo_pagamento": "Último dia útil do mês seguinte",
        "base_legal": "Lei 11.033/2004; Lei 9.779/1999; IN RFB 1.585/2015",
    },
    "opcao": {
        "descricao": "Opções sobre ações — sem isenção de R$20k",
        "swing_trade": {
            "aliquota": 0.15,
            "irrf": 0.00005,
            "isencao_mensal": None,
            "nota": "Opções NÃO têm isenção de R$20.000. Todo ganho é tributado.",
        },
        "day_trade": {
            "aliquota": 0.20,
            "irrf": 0.01,
            "isencao_mensal": None,
        },
        "ganho_calculo": (
            "Ganho = (preço_venda_opção - prêmio_pago) × quantidade. "
            "Se expirar sem valor: prejuízo = prêmio_pago × quantidade."
        ),
        "exercicio_opcao": "Exercício: tributado como a ação subjacente pelo lucro no exercício.",
        "compensacao_prejuizo": "Sim, com outras opções ou ações (mesma categoria)",
        "darf_codigo": 6015,
        "prazo_pagamento": "Último dia útil do mês seguinte",
        "base_legal": "IN RFB 1.585/2015",
    },
}

# ─── B3 fee structure ──────────────────────────────────────────────────────────

_B3_FEES: dict = {
    "taxa_liquidacao": {
        "percentual": 0.000275,
        "percentual_display": "0,0275%",
        "aplicacao": "Sobre o valor financeiro da operação (compra e venda)",
        "base": "B3",
    },
    "taxa_registro_acoes": {
        "percentual": 0.000034,
        "percentual_display": "0,0034%",
        "aplicacao": "Ações, BDRs e FIIs",
        "base": "B3",
    },
    "emolumentos_acoes": {
        "percentual": 0.00003,
        "percentual_display": "0,003%",
        "aplicacao": "Ações, BDRs e FIIs",
        "base": "B3",
    },
    "iss_corretagem": {
        "percentual": 0.05,
        "percentual_display": "5%",
        "aplicacao": "Sobre a corretagem paga à corretora (imposto municipal — varia por cidade)",
        "base": "Prefeitura Municipal",
    },
    "corretagem": {
        "descricao": "Varia por corretora",
        "exemplos": {
            "clear_rico": "R$0,00 (taxa zero)",
            "xp_btg": "R$0,50–R$2,50 fixo ou percentual (negociado)",
            "percentual_tipico": "0,035% sobre o valor financeiro",
        },
    },
    "formula_total": "Total = taxa_liquidacao + taxa_registro + emolumentos + corretagem + iss",
    "exemplo_R2500": {
        "valor_operacao": 2500.0,
        "taxa_liquidacao": round(2500 * 0.000275, 4),
        "taxa_registro": round(2500 * 0.000034, 4),
        "emolumentos": round(2500 * 0.00003, 4),
        "total_b3_sem_corretagem": round(2500 * (0.000275 + 0.000034 + 0.00003), 4),
    },
}

# ─── Worked examples ──────────────────────────────────────────────────────────

_EXAMPLES: dict = {
    "acao": {
        "titulo": "Swing Trade PETR4 com isenção (total <= R$20k no mês)",
        "cenario": (
            "Comprei 100 PETR4 a R$20,00 em 01/03/2025. "
            "Vendi 100 PETR4 a R$25,50 em 15/03/2025. "
            "Este foi o único trade de ação em março."
        ),
        "passo_a_passo": {
            "1_preco_medio": "PM = R$20,00 (único lote)",
            "2_valor_financeiro": "100 × R$25,50 = R$2.550,00",
            "3_ganho_bruto": "(R$25,50 - R$20,00) × 100 = R$550,00",
            "4_isencao": "Total vendido no mês = R$2.550 ≤ R$20.000 → ISENTO",
            "5_ir_devido": "R$0,00 (isenção aplicada)",
            "6_irrf": "R$2.550 × 0,005% = R$0,13 (devolve ao ajustar a declaração)",
            "7_taxa_liquidacao": "R$2.550 × 0,0275% = R$0,70",
            "8_taxa_registro": "R$2.550 × 0,0034% = R$0,087",
            "9_emolumentos": "R$2.550 × 0,003% = R$0,077",
            "10_valor_liquido": "R$2.550 - R$0,00 - R$0,13 - R$0,86 = R$2.549,01",
        },
        "resultado": {
            "valor_financeiro": 2550.0,
            "ganho_bruto": 550.0,
            "ir_devido": 0.0,
            "irrf_retido": 0.1275,
            "taxas_b3": 0.865,
            "valor_liquido": 2549.01,
            "isencao_aplicada": True,
        },
    },
    "acao_sem_isencao": {
        "titulo": "Swing Trade VALE3 sem isenção (total > R$20k no mês)",
        "cenario": (
            "Comprei 1.000 VALE3 a R$20,00. Vendi a R$25,00. "
            "Total vendido no mês: R$25.000 (acima de R$20k)."
        ),
        "passo_a_passo": {
            "1_valor_financeiro": "1.000 × R$25,00 = R$25.000,00",
            "2_ganho_bruto": "(R$25,00 - R$20,00) × 1.000 = R$5.000,00",
            "3_isencao": "Total vendido no mês = R$25.000 > R$20.000 → SEM ISENÇÃO",
            "4_aliquota": "15% (swing trade ação)",
            "5_ir_devido": "R$5.000 × 15% = R$750,00",
            "6_irrf": "R$25.000 × 0,005% = R$1,25",
            "7_taxas_b3": "R$25.000 × (0,0275%+0,0034%+0,003%) = R$8,46",
            "8_valor_liquido": "R$25.000 - R$750 - R$1,25 - R$8,46 = R$24.240,29",
        },
        "resultado": {
            "valor_financeiro": 25000.0,
            "ganho_bruto": 5000.0,
            "ir_devido": 750.0,
            "irrf_retido": 1.25,
            "taxas_b3": 8.46,
            "valor_liquido": 24240.29,
            "isencao_aplicada": False,
        },
    },
    "fii": {
        "titulo": "Venda de cotas HGLG11 — sempre 20%",
        "cenario": (
            "Comprei 100 cotas HGLG11 a R$150,00. "
            "Vendi a R$165,00. FII nunca tem isenção."
        ),
        "passo_a_passo": {
            "1_valor_financeiro": "100 × R$165,00 = R$16.500,00",
            "2_ganho_bruto": "(R$165 - R$150) × 100 = R$1.500,00",
            "3_isencao": "FII: SEM isenção de R$20.000",
            "4_aliquota": "20% (FII — alíquota única)",
            "5_ir_devido": "R$1.500 × 20% = R$300,00",
            "6_irrf": "R$16.500 × 0,005% = R$0,83",
            "7_taxas_b3": "R$16.500 × 0,0309% = R$5,10",
            "8_valor_liquido": "R$16.500 - R$300 - R$0,83 - R$5,10 = R$16.194,07",
        },
        "resultado": {
            "valor_financeiro": 16500.0,
            "ganho_bruto": 1500.0,
            "ir_devido": 300.0,
            "irrf_retido": 0.825,
            "taxas_b3": 5.10,
            "valor_liquido": 16194.07,
            "isencao_aplicada": False,
        },
    },
    "bdr": {
        "titulo": "Venda de AMZO34 (BDR Amazon) — mesmas regras que ação",
        "cenario": "Comprei 10 BDRs AMZO34 a R$200,00. Vendi a R$230,00. Único trade do mês.",
        "passo_a_passo": {
            "1_valor_financeiro": "10 × R$230 = R$2.300,00",
            "2_ganho_bruto": "(R$230 - R$200) × 10 = R$300,00",
            "3_isencao": "Total vendido = R$2.300 ≤ R$20.000 → ISENTO",
            "4_ir_devido": "R$0,00 (isenção — mesmas regras que ações)",
            "5_irrf": "R$2.300 × 0,005% = R$0,12",
            "6_taxas_b3": "R$2.300 × 0,0309% ≈ R$0,71",
            "7_valor_liquido": "R$2.300 - R$0 - R$0,12 - R$0,71 ≈ R$2.299,17",
        },
        "resultado": {
            "valor_financeiro": 2300.0,
            "ganho_bruto": 300.0,
            "ir_devido": 0.0,
            "irrf_retido": 0.115,
            "taxas_b3": 0.711,
            "valor_liquido": 2299.17,
            "isencao_aplicada": True,
        },
    },
    "opcao": {
        "titulo": "Venda de calls PETRH250 — sem isenção",
        "cenario": (
            "Comprei 100 calls PETRH250 pagando prêmio de R$2,00. "
            "Vendi as opções a R$5,00 antes do vencimento."
        ),
        "passo_a_passo": {
            "1_valor_financeiro_venda": "100 × R$5,00 = R$500,00",
            "2_custo_premios": "100 × R$2,00 = R$200,00 (base de custo)",
            "3_ganho_bruto": "(R$5,00 - R$2,00) × 100 = R$300,00",
            "4_isencao": "Opção: SEM isenção de R$20.000",
            "5_aliquota": "15% (swing trade)",
            "6_ir_devido": "R$300 × 15% = R$45,00",
            "7_irrf": "R$500 × 0,005% = R$0,025",
            "8_taxas_b3": "R$500 × 0,0309% ≈ R$0,15",
            "9_valor_liquido": "R$500 - R$45 - R$0,025 - R$0,15 ≈ R$454,83",
        },
        "caso_expiracao": (
            "Se a opção expirar sem valor (virar pó): "
            "prejuízo = R$200 (prêmio pago). "
            "Pode ser compensado com ganhos em opções/ações no mesmo mês."
        ),
        "resultado": {
            "valor_financeiro": 500.0,
            "ganho_bruto": 300.0,
            "ir_devido": 45.0,
            "irrf_retido": 0.025,
            "taxas_b3": 0.155,
            "valor_liquido": 454.83,
            "isencao_aplicada": False,
        },
    },
}

# ─── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def get_tax_rules(asset_type: str) -> str:
    """
    Returns IR (income tax) rules for a Brazilian financial asset type.

    asset_type: acao | bdr | fii | opcao
    """
    key = asset_type.lower().strip()
    if key not in _TAX_RULES:
        available = ", ".join(_TAX_RULES.keys())
        return f"Tipo de ativo '{asset_type}' não encontrado. Disponíveis: {available}"
    return json.dumps(_TAX_RULES[key], ensure_ascii=False, indent=2)


@mcp.tool()
def get_fee_structure(asset_type: str = "acao") -> str:
    """
    Returns B3 fee structure for a given asset type.

    asset_type: acao | bdr | fii | opcao (all use same B3 rates for equities)
    """
    return json.dumps(_B3_FEES, ensure_ascii=False, indent=2)


@mcp.tool()
def example_calculation(asset_type: str) -> str:
    """
    Returns a worked step-by-step calculation example for an asset type.

    asset_type: acao | acao_sem_isencao | fii | bdr | opcao
    """
    key = asset_type.lower().strip()
    if key not in _EXAMPLES:
        available = ", ".join(_EXAMPLES.keys())
        return f"Exemplo para '{asset_type}' não encontrado. Disponíveis: {available}"
    return json.dumps(_EXAMPLES[key], ensure_ascii=False, indent=2)


@mcp.tool()
def get_regulation(keyword: str) -> str:
    """
    Searches regulation text files for a keyword and returns matching excerpts.

    keyword: Any term, e.g. "isenção", "alíquota", "day trade", "preço médio"
    """
    if not REGULATIONS_DIR.exists():
        return f"Diretório de regulações não encontrado: {REGULATIONS_DIR}"

    keyword_lower = keyword.lower()
    results: list[dict] = []

    for reg_file in sorted(REGULATIONS_DIR.glob("*.txt")):
        content = reg_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        matches: list[str] = []
        for i, line in enumerate(lines):
            if keyword_lower in line.lower():
                start = max(0, i - 1)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end])
                if context not in matches:
                    matches.append(context)

        if matches:
            results.append({
                "arquivo": reg_file.name,
                "trechos_encontrados": matches[:5],
            })

    if not results:
        return f"Nenhum resultado encontrado para '{keyword}' nos arquivos de regulação."

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def validate_calculation(
    asset_type: str,
    params: str,
    result: str,
) -> str:
    """
    Validates a tax calculation against known Brazilian IR rules.

    asset_type: acao | bdr | fii | opcao
    params: JSON string with keys: ganho_bruto, valor_financeiro, is_day_trade,
            total_vendido_mes (optional), isencao_aplicada (optional)
    result: JSON string with keys: aliquota_aplicada, ir_devido, irrf_retido
    """
    try:
        p = json.loads(params)
        r = json.loads(result)
    except json.JSONDecodeError as e:
        return f"Erro ao parsear JSON: {e}"

    key = asset_type.lower().strip()
    if key not in _TAX_RULES:
        return f"Tipo '{asset_type}' desconhecido."

    rules = _TAX_RULES[key]
    is_day = bool(p.get("is_day_trade", False))
    trade_rules = rules["day_trade"] if is_day else rules["swing_trade"]

    errors: list[str] = []
    warnings: list[str] = []
    ok: list[str] = []

    # Validate aliquota
    expected_aliquota = trade_rules["aliquota"]
    actual_aliquota = r.get("aliquota_aplicada")
    if actual_aliquota is not None:
        if not math.isclose(actual_aliquota, expected_aliquota, rel_tol=0.001):
            errors.append(
                f"Alíquota incorreta: esperado {expected_aliquota*100:.0f}%, "
                f"recebido {actual_aliquota*100:.2f}%"
            )
        else:
            ok.append(f"Alíquota {actual_aliquota*100:.0f}% correta")

    # Check isenção logic (swing trade only)
    ganho_bruto = p.get("ganho_bruto", 0)
    total_mes = p.get("total_vendido_mes", p.get("valor_financeiro", 0))
    isencao_aplicada = p.get("isencao_aplicada", r.get("isencao_aplicada", False))
    isencao_limit = trade_rules.get("isencao_mensal")

    if not is_day and isencao_limit:
        if total_mes <= isencao_limit and not isencao_aplicada:
            warnings.append(
                f"Total vendido no mês (R${total_mes:,.2f}) <= R${isencao_limit:,.2f} "
                f"— isenção deveria ser aplicada"
            )
        elif total_mes > isencao_limit and isencao_aplicada:
            errors.append(
                f"Isenção aplicada incorretamente: total vendido R${total_mes:,.2f} "
                f"> R${isencao_limit:,.2f}"
            )
        else:
            ok.append("Aplicação da isenção correta")
    elif is_day and isencao_aplicada:
        errors.append("Day trade não tem isenção — isenção não deve ser aplicada")
    elif not is_day and not isencao_limit and isencao_aplicada:
        errors.append(f"{asset_type.upper()} não tem isenção de R$20k — verifique a lógica")

    # Validate IR due
    ir_expected = 0.0
    if isencao_aplicada or (not is_day and isencao_limit and total_mes <= isencao_limit):
        ir_expected = 0.0
    else:
        ir_expected = max(0, ganho_bruto) * expected_aliquota

    actual_ir = r.get("ir_devido")
    if actual_ir is not None and not math.isclose(actual_ir, ir_expected, abs_tol=0.10):
        errors.append(
            f"IR devido incorreto: esperado R${ir_expected:,.2f}, recebido R${actual_ir:,.2f}"
        )
    elif actual_ir is not None:
        ok.append(f"IR devido R${actual_ir:,.2f} correto")

    # Validate IRRF
    valor_financeiro = p.get("valor_financeiro", 0)
    expected_irrf_rate = trade_rules["irrf"]
    irrf_base = max(0, ganho_bruto) if is_day else valor_financeiro
    expected_irrf = irrf_base * expected_irrf_rate
    actual_irrf = r.get("irrf_retido")
    if actual_irrf is not None and not math.isclose(actual_irrf, expected_irrf, abs_tol=0.10):
        warnings.append(
            f"IRRF: esperado R${expected_irrf:,.4f} "
            f"({expected_irrf_rate*100:.3f}% × R${irrf_base:,.2f}), "
            f"recebido R${actual_irrf:,.4f}"
        )
    elif actual_irrf is not None:
        ok.append(f"IRRF R${actual_irrf:,.4f} correto")

    # Summary
    status = "VÁLIDO" if not errors else "INVÁLIDO"
    return json.dumps(
        {
            "status": status,
            "aprovado": ok,
            "erros": errors,
            "avisos": warnings,
            "regras_aplicadas": {
                "tipo": key,
                "modalidade": "day_trade" if is_day else "swing_trade",
                "aliquota_esperada": expected_aliquota,
                "irrf_rate_esperado": expected_irrf_rate,
                "isencao_mensal": isencao_limit,
            },
        },
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
