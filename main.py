import os
import pandas as pd
from dotenv import load_dotenv
from pypdf import PdfReader
from google import genai

# 1. CARGA DE CONFIGURACIÓN
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("ERROR: No se encontró la GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)


# 2. PROCESAMIENTO Y LIMPIEZA DEL CSV
def cargar_inventario(ruta_csv):
    if not os.path.exists(ruta_csv):
        print(f"[-] Archivo no encontrado: {ruta_csv}")
        return None
    
    df = pd.read_csv(ruta_csv)
    # Eliminar columnas sin nombre
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    print(f"[+] Inventario cargado exitosamente ({len(df)} registros procesados).")
    return df


# 3. EXTRAER TEXTO COMPLETO DE PDFs
def extraer_texto_pdfs(lista_pdfs):
    texto_consolidado = ""
    for ruta_pdf in lista_pdfs:
        if os.path.exists(ruta_pdf):
            reader = PdfReader(ruta_pdf)
            texto_pdf = ""
            for page in reader.pages:
                texto_pdf += page.extract_text() or ""
            texto_consolidado += f"\n=== DOCUMENTO: {ruta_pdf} ===\n{texto_pdf}\n"
            print(f"[+] PDF cargado: {ruta_pdf}")
        else:
            print(f"[-] PDF no encontrado: {ruta_pdf}")
            
    return texto_consolidado


# 4. CONSULTAR A GEMINI
def consultar_gemini(prompt_usuario, df_inventario, texto_pdfs):
    # Resumen estructurado del CSV para dar contexto completo
    resumen_csv = df_inventario.to_string(index=False)
    
    prompt_completo = f"""
    Eres un asistente virtual experto en gestión de inventarios y cumplimiento normativo para un supermercado.
    
    REGLAS Y POLÍTICAS DEL SUPERMERCADO:
    {texto_pdfs}
    
    DATOS DEL INVENTARIO:
    {resumen_csv}
    
    INSTRUCCIONES:
    Responde a la siguiente consulta del usuario de forma precisa, profesional y estructurada. 
    Usa la información del inventario y contrástala con las políticas cuando corresponda.
    
    PREGUNTA DEL USUARIO:
    {prompt_usuario}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_completo
    )
    return response.text


# 5. FLUJO PRINCIPAL INTERACTIVO
if __name__ == "__main__":
    archivo_csv = "inventario_de_supermercado_latam.csv"
    archivos_pdf = [
        "Manual de Proveedores y Política de Compras — Mercado Central 24h (México).pdf",
        "Política de Atención al Cliente y Devoluciones — Mercado Central 24h (México).pdf",
        "Preguntas Frecuentes (FAQ) — Mercado Central 24h (México).pdf",
        "Reglamento Interno y Procedimientos Operativos — Mercado Central 24h (México).pdf"
    ]
    
    print("\n--- CARGANDO BASE DE DATOS Y DOCUMENTACIÓN ---")
    df_inventario = cargar_inventario(archivo_csv)
    texto_politicas = extraer_texto_pdfs(archivos_pdf)
    
    if df_inventario is not None:
        print("\n==================================================")
        print(" Sistema listo. Escribe tu pregunta (o 'salir').")
        print("==================================================\n")
        
        while True:
            pregunta = input("TÚ > ")
            if pregunta.lower() in ["salir", "exit", "quit"]:
                print("Cerrando el sistema...")
                break
            
            if not pregunta.strip():
                continue
                
            print("\n[...] Gemini analizando datos...")
            try:
                respuesta = consultar_gemini(pregunta, df_inventario, texto_politicas)
                print(f"\nASISTENTE IA:\n{respuesta}\n")
                print("-" * 50)
            except Exception as e:
                print(f"[-] Error al consultar Gemini: {e}\n")
        pregunta = "¿Qué productos del inventario requieren atención o revisión según las políticas?"
        print("\n--- CONSULTANDO A GEMINI ---")
        respuesta = consultar_gemini(pregunta, df_inventario, texto_politicas)
        print("\nRESPUESTA DE LA IA:\n")
        print(respuesta)




        # el siguiente comando ejecuta el script principal y asegura que todas las dependencias estén instaladas:
        # python -m pip install pandas google-genai python-dotenv pypdf

        # python.terminal.useEnvFile