import streamlit as st


def fmt_brl(value: float) -> str:
    """Format float as Brazilian Real: R$ 1.234,56"""
    formatted = f"{abs(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    prefix = "-R$ " if value < 0 else "R$ "
    return f"{prefix}{formatted}"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def render_result(result: dict) -> None:
    """Render a TaxCalculationResult as a formatted card."""
    ativo = result.get("ativo", "—")
    ganho = result.get("ganho_prejuizo_bruto", 0.0)
    ir = result.get("ir_devido", 0.0)
    irrf = result.get("irrf_retido", 0.0)
    aliquota = result.get("aliquota_aplicada", 0.0)
    isento = result.get("isenção_aplicada", False)
    valor_fin = result.get("valor_financeiro", 0.0)
    valor_liq = result.get("valor_liquido", 0.0)
    classificacao = result.get("tipo_operacao_classificacao", "swing")
    mensagem = result.get("mensagem", "")
    taxas = result.get("taxas_totais", {})

    st.subheader(f"Resultado — {ativo}")
    if mensagem:
        st.caption(mensagem)

    col1, col2, col3 = st.columns(3)

    with col1:
        label = "Ganho Bruto" if ganho >= 0 else "Prejuízo Bruto"
        st.metric(label, fmt_brl(ganho))
        if isento:
            st.success("Isenção R$20.000 aplicada")

    with col2:
        st.metric("IR Devido", fmt_brl(ir))
        tipo_label = classificacao.replace("_", " ").title()
        st.caption(f"Alíquota: {fmt_pct(aliquota)} · {tipo_label}")
        if irrf > 0:
            st.caption(f"IRRF retido na fonte: {fmt_brl(irrf)}")

    with col3:
        st.metric("Valor Líquido", fmt_brl(valor_liq))
        st.caption(f"Valor financeiro: {fmt_brl(valor_fin)}")

    with st.expander("Detalhamento de taxas B3"):
        if isinstance(taxas, dict):
            rows = {
                "Taxa": ["Liquidação", "Registro", "Emolumentos", "Corretagem", "ISS s/ Corretagem"],
                "Valor": [
                    fmt_brl(taxas.get("taxa_liquidacao", 0)),
                    fmt_brl(taxas.get("taxa_registro", 0)),
                    fmt_brl(taxas.get("emolumentos", 0)),
                    fmt_brl(taxas.get("corretagem", 0)),
                    fmt_brl(taxas.get("iss_sobre_corretagem", 0)),
                ],
            }
            st.table(rows)
