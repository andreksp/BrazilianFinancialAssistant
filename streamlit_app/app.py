import streamlit as st

st.set_page_config(
    page_title="Assistente Financeiro Brasileiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Assistente Financeiro Brasileiro")
st.markdown("""
**TCC — Sistema Inteligente para o Mercado Financeiro Brasileiro**

Bem-vindo! Use o menu lateral para navegar:

| Página | Descrição |
|--------|-----------|
| 📈 Calcular Trade | Informe uma operação e veja IR, taxas e valor líquido |
| 💬 Chat | Converse em linguagem natural *(Fase 3 — em breve)* |
| 📋 Histórico | Resumo mensal de operações e DARF |

---

### Como funciona

1. Registre suas **compras** na página *Calcular Trade* para o sistema calcular seu preço médio
2. Registre as **vendas** para obter o IR devido, IRRF retido e valor líquido
3. Veja o **resumo mensal** e as informações do DARF na página *Histórico*
""")

with st.sidebar:
    st.markdown("---")
    st.caption("Backend: `http://localhost:8000`")
    st.caption("API Docs: [localhost:8000/docs](http://localhost:8000/docs)")
