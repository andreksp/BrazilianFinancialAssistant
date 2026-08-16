import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from datetime import date

from utils.api_client import get_monthly_summary, get_darf_info, get_trade_history
from components.result_card import fmt_brl

st.set_page_config(page_title="Histórico", page_icon="📋", layout="wide")
st.title("📋 Histórico e Resumo Mensal")

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

col1, col2 = st.columns(2)
with col1:
    mes = st.selectbox(
        "Mês",
        options=list(range(1, 13)),
        index=date.today().month - 1,
        format_func=lambda m: MESES[m - 1],
    )
with col2:
    ano = st.number_input(
        "Ano", min_value=2020, max_value=2030, value=date.today().year, step=1
    )

if st.button("Carregar", type="primary"):
    summary = get_monthly_summary(int(mes), int(ano))
    darf = get_darf_info(int(mes), int(ano))

    if summary is None:
        st.warning(f"Nenhuma operação de venda encontrada em {mes:02d}/{int(ano)}.")
    else:
        st.subheader(f"Resumo — {MESES[mes - 1]} {int(ano)}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Ganho Swing", fmt_brl(summary.get("ganho_swing_trade", 0)))
            st.metric("Prejuízo Swing", fmt_brl(summary.get("prejuizo_swing_trade", 0)))
        with c2:
            st.metric("Ganho Day Trade", fmt_brl(summary.get("ganho_day_trade", 0)))
            st.metric("Prejuízo Day Trade", fmt_brl(summary.get("prejuizo_day_trade", 0)))
        with c3:
            st.metric("IR Swing", fmt_brl(summary.get("ir_swing_trade", 0)))
            st.metric("IR Day Trade", fmt_brl(summary.get("ir_day_trade", 0)))
        with c4:
            st.metric("IR Total Devido", fmt_brl(summary.get("ir_total_devido", 0)))
            st.metric("IRRF Retido", fmt_brl(summary.get("irrf_retido_total", 0)))

    # DARF card (always shown even when no trades)
    st.divider()
    st.subheader("DARF — Código 6015")

    if darf:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Valor a Pagar", fmt_brl(darf.get("valor_a_pagar", 0)))
        with d2:
            venc_raw = darf.get("vencimento") or ""
            if venc_raw:
                parts = venc_raw.split("-")
                venc = f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else venc_raw
            else:
                venc = "—"
            st.metric("Vencimento", venc)
        with d3:
            st.metric("Código DARF", darf.get("codigo_darf", "6015"))

        if darf.get("deve_pagar"):
            st.error(
                f"⚠️ DARF a recolher até **{venc}**. "
                f"Valor: **{fmt_brl(darf.get('valor_a_pagar', 0))}**"
            )
        else:
            ir = darf.get("ir_devido", 0)
            if ir == 0:
                st.success("✅ Sem IR a recolher este mês.")
            else:
                st.success(
                    f"✅ IR ({fmt_brl(ir)}) abaixo de R$10,00 — não há DARF a recolher."
                )

    # Trade history table
    st.divider()
    st.subheader("Operações de Venda do Mês")
    try:
        trades = get_trade_history(month=int(mes), year=int(ano))
        if not trades:
            st.info("Nenhuma operação de venda registrada neste mês.")
        else:
            rows = []
            for t in trades:
                data_raw = t.get("data_operacao", "")
                if data_raw:
                    parts = data_raw.split("-")
                    data_fmt = f"{parts[2]}/{parts[1]}/{parts[0]}" if len(parts) == 3 else data_raw
                else:
                    data_fmt = "—"
                rows.append({
                    "Data": data_fmt,
                    "Ativo": t.get("ativo", ""),
                    "Qtd": int(t.get("quantidade", 0)),
                    "Preço": fmt_brl(t.get("preco_unitario", 0)),
                    "Valor Fin.": fmt_brl(t.get("valor_financeiro", 0)),
                    "G/P Bruto": fmt_brl(t.get("ganho_prejuizo_bruto", 0)),
                    "IR Devido": fmt_brl(t.get("ir_devido", 0)),
                    "Valor Líq.": fmt_brl(t.get("valor_liquido", 0)),
                })
            st.dataframe(rows, use_container_width=True)
            st.caption(f"{len(trades)} operação(ões) encontrada(s).")
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
