import streamlit as st
import pandas as pd
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Asistente Virtual IA - Tech AI Builder", page_icon="🤖")
st.title("🤖 Asistente Virtual Inteligente")
st.subheader("Oracle ONE / Alura LATAM - Tech AI Builder")

# Carga de API Key desde secretos de Streamlit o .env local
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("No se encontró la GEMINI_API_KEY. Configúrala en las variables de entorno.")
    st.stop()

client = genai.Client(api_key=api_key)

# Historial de chat en interfaz
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Realiza tu consulta sobre inventario o políticas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})