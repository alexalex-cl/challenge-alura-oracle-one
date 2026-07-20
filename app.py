import os
import pandas as pd
from pypdf import PdfReader
import streamlit as st
from google import genai
from dotenv import load_dotenv

# Cargar variables locales
load_dotenv()

st.set_page_config(page_title="Asistente IA - Oracle ONE", page_icon="🤖")
st.title("🤖 Asistente Virtual de Inventario y Políticas - Mercado Central 24h")
st.caption("Oracle ONE / Alura LATAM - Tech AI Builder / Challenge")

# Obtener clave API (local desde .env o desde Secrets en Streamlit Cloud)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ No se encontró la API Key. Configúrala en las variables del sistema.")
    st.stop()

# Configurar cliente de Gemini
client = genai.Client(api_key=api_key)

# Cargar datos (CSV + PDFs) con almacenamiento en caché para agilizar la app
@st.cache_resource
def cargar_contexto():
    contexto = ""
    # Lectura de CSV
    if os.path.exists("inventario_de_supermercado_latam.csv"):
        df = pd.read_csv("inventario_de_supermercado_latam.csv")
        contexto += f"\n--- DATOS DE INVENTARIO (CSV) ---\n{df.to_string(index=False)}\n"
    
    # Lectura de PDFs
    for archivo in os.listdir("."):
        if archivo.endswith(".pdf"):
            reader = PdfReader(archivo)
            texto_pdf = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            contexto += f"\n--- DOCUMENTO POLITICA ({archivo}) ---\n{texto_pdf}\n"
            
    return contexto

contexto_base = cargar_contexto()

# Historial de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Consulta sobre el inventario o las políticas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        prompt_completo = f"Con base en la siguiente información de la empresa:\n{contexto_base}\n\nResponde a la consulta del usuario de forma precisa, esquemática y resumida:\n{prompt}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_completo,
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})