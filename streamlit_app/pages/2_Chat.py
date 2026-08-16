import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.api_client import send_chat

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
st.title("💬 Chat com o Assistente")

st.info(
    "**Fase 3 — em breve.** A IA para linguagem natural será integrada na próxima fase. "
    "O chat já conecta ao backend; as respostas são placeholders até a integração do LLM.",
    icon="🤖",
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Olá! Sou o Assistente Financeiro Brasileiro. "
                "Em breve poderei interpretar suas operações em linguagem natural. "
                "Por enquanto, use a página *Calcular Trade* para registrar operações diretamente."
            ),
        }
    ]

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("calculation"):
            from components.result_card import render_result
            render_result(msg["calculation"])

if prompt := st.chat_input("Ex: Vendi 100 ações da PETR4 por R$25,50 cada em 15/03/2025"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                resp = send_chat(prompt)
                reply = resp.get("response", "Sem resposta do servidor.")
                calc = resp.get("calculation_result")
            except Exception as e:
                reply = f"Erro ao conectar ao backend: {e}"
                calc = None

        st.write(reply)
        if calc:
            from components.result_card import render_result
            render_result(calc)

    entry: dict = {"role": "assistant", "content": reply}
    if calc:
        entry["calculation"] = calc
    st.session_state.chat_messages.append(entry)
