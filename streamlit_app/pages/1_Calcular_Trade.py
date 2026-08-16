import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from datetime import date

from utils.api_client import process_trade
from components.result_card import render_result, fmt_brl

st.set_page_config(page_title="Calcular Trade", page_icon="📈", layout="wide")
st.title("📈 Calcular Trade")
st.markdown("Informe os dados da operação para calcular IR, taxas e valor líquido.")

with st.form("trade_form"):
    col1, col2 = st.columns(2)

    with col1:
        ativo = st.text_input("Ticker *", placeholder="PETR4", max_chars=20)
        tipo_ativo = st.selectbox(
            "Tipo de Ativo *",
            options=["acao", "bdr", "fii", "opcao"],
            format_func=lambda x: {
                "acao": "Ação",
                "bdr": "BDR",
                "fii": "Fundo Imobiliário (FII)",
                "opcao": "Opção",
            }[x],
        )
        tipo_operacao = st.radio(
            "Operação *",
            options=["compra", "venda"],
            format_func=lambda x: "🟢 Compra" if x == "compra" else "🔴 Venda",
            horizontal=True,
        )

    with col2:
        quantidade = st.number_input("Quantidade *", min_value=1, step=1, value=100)
        preco = st.number_input(
            "Preço Unitário (R$) *", min_value=0.01, step=0.01, value=25.00, format="%.2f"
        )
        data_op = st.date_input("Data da Operação *", value=date.today())

    with st.expander("Custos de Corretagem (opcional)"):
        corretora = st.text_input("Corretora", placeholder="XP, C6, Clear, BTG...")
        c1, c2 = st.columns(2)
        with c1:
            corretagem_pct = st.number_input(
                "Corretagem % (ex: 0.001 = 0,1%)",
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                value=0.0,
                format="%.4f",
            )
        with c2:
            corretagem_fixa = st.number_input(
                "Corretagem Fixa (R$)", min_value=0.0, step=0.01, value=0.0, format="%.2f"
            )

    submitted = st.form_submit_button("Calcular", use_container_width=True, type="primary")

if submitted:
    if not ativo.strip():
        st.error("Informe o ticker do ativo.")
    else:
        payload = {
            "ativo": ativo.strip().upper(),
            "tipo_ativo": tipo_ativo,
            "tipo_operacao": tipo_operacao,
            "quantidade": float(quantidade),
            "preco_unitario": float(preco),
            "data_operacao": str(data_op),
            "corretora": corretora.strip() or None,
            "corretagem_percentual": float(corretagem_pct),
            "corretagem_fixa": float(corretagem_fixa),
        }
        try:
            with st.spinner("Processando..."):
                result = process_trade(payload)

            if result.get("tipo_operacao") == "compra":
                st.success(result.get("mensagem", "Compra registrada com sucesso."))
                st.info(
                    f"Preço médio de **{result['ativo']}** atualizado. "
                    "Registre a venda quando quiser calcular o IR."
                )
            else:
                render_result(result)

        except Exception as e:
            st.error(f"Erro ao processar: {e}")
            st.caption("Verifique se o backend FastAPI está rodando em http://localhost:8000")
