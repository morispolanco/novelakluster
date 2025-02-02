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
        "max_tokens": 6000,
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
if st.button("Generar novela automáticamente"):
    prompt_trama = f"Genera una trama completa para una novela de género {genero} con el título '{titulo}'. Divide la trama en 24 capítulos y proporciona una breve descripción para cada uno."
    trama = generar_contenido(prompt_trama)
    st.session_state["trama"] = trama

    # Generar cada capítulo automáticamente con barra de progreso
    progreso = st.progress(0)
    for capitulo_num in range(1, 25):
        capitulo_completo = ""
        for escena_num in range(1, 4):
            descripcion_escena = (
                f"Escribe la escena {escena_num} del capítulo {capitulo_num} basado en la descripción de la trama. La escena debe incluir: "
                "desarrollo de personajes con pensamientos, emociones y trasfondos; descripciones detalladas de escenarios y situaciones; "
                "tramas secundarias que complementen la historia principal; diálogos extensos; reflexiones internas de los personajes; "
                "eventos detallados; flashbacks o recuerdos; expansión del mundo (si aplica); y un ritmo controlado. "
                f"Trama: {trama}"
            )
            escena = generar_contenido(descripcion_escena)
            capitulo_completo += f"\nEscena {escena_num}\n" + escena + "\n"
        st.session_state[f"capitulo_{capitulo_num}"] = capitulo_completo
        st.write(f"Capítulo {capitulo_num} generado.")
        progreso.progress(capitulo_num / 24)

# Descargar novela completa
documento = Document()
documento.add_heading(titulo, level=1)

for i in range(1, 25):
    if f"capitulo_{i}" in st.session_state:
        documento.add_heading(f"Capítulo {i}", level=2)
        documento.add_paragraph(st.session_state[f"capitulo_{i}"])

if st.button("Descargar novela completa"):
    nombre_archivo = f"{titulo.replace(' ', '_')}.docx"
    documento.save(nombre_archivo)
    with open(nombre_archivo, "rb") as file:
        st.download_button("Descargar novela", file, file_name=nombre_archivo)
