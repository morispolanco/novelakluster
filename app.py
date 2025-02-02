import streamlit as st
import requests
import time
from docx import Document

# Funciones auxiliares
def generar_contenido(prompt, model="deepseek-ai/DeepSeek-R1"):
    api_key = st.secrets["TOGETHER_API_KEY"]
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "max_tokens": 2000,
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error("Error al generar contenido. Intenta de nuevo.")
        return ""

# Configuración de la aplicación
st.title("Generador de Novelas por Capítulos")
st.write("Escribe tu novela con desarrollo de personajes, tramas y descripciones detalladas.")

# Entrada del usuario
titulo = st.text_input("Título de la novela")
genero = st.selectbox("Selecciona el género", ["Fantasía", "Ciencia ficción", "Romance", "Misterio", "Thriller", "Aventura"])

# Botón para comenzar
if st.button("Generar trama y tabla de contenidos"):
    prompt_trama = f"Genera una trama completa para una novela de género {genero} con el título '{titulo}'. Divide la trama en 24 capítulos y proporciona una breve descripción para cada uno."
    trama = generar_contenido(prompt_trama)
    st.session_state["trama"] = trama
    st.write(trama)

# Generar capítulos
if "trama" in st.session_state:
    st.subheader("Tabla de contenidos")
    st.write(st.session_state["trama"])

    capitulo_actual = st.number_input("Selecciona el capítulo a escribir", min_value=1, max_value=24, step=1)
    if st.button("Escribir capítulo"):
        descripcion_capitulo = f"Escribe el capítulo {capitulo_actual} basado en la siguiente descripción de la trama: {st.session_state['trama']}"
        capitulo = generar_contenido(descripcion_capitulo)
        st.session_state[f"capitulo_{capitulo_actual}"] = capitulo
        st.write(capitulo)

# Descargar novela completa
documento = Document()
documento.add_heading(titulo, level=1)

tabla_contenidos = st.session_state.get("trama", "")
documento.add_heading("Tabla de contenidos", level=2)
documento.add_paragraph(tabla_contenidos)

for i in range(1, 25):
    if f"capitulo_{i}" in st.session_state:
        documento.add_heading(f"Capítulo {i}", level=2)
        documento.add_paragraph(st.session_state[f"capitulo_{i}"])

if st.button("Descargar novela completa"):
    nombre_archivo = f"{titulo.replace(' ', '_')}.docx"
    documento.save(nombre_archivo)
    with open(nombre_archivo, "rb") as file:
        st.download_button("Descargar novela", file, file_name=nombre_archivo)
