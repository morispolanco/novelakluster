import streamlit as st
from openai import OpenAI
import time
from docx import Document

# Leer la API key desde los secretos de Streamlit
import openai_secret_manager

assert "klusterai" in openai_secret_manager.get_services()
secrets = openai_secret_manager.get_secrets("klusterai")

# Configurar el cliente de la API
client = OpenAI(
    base_url="https://api.kluster.ai/v1", api_key=secrets["api_key"]
)

# Función para generar texto usando la API
def generar_capitulo(titulo, genero, capitulo_num):
    prompt = f"Escribe el capítulo {capitulo_num} de una novela de género {genero} titulada {titulo}. Cada capítulo debe tener alrededor de 2000 palabras, con un enfoque en los eventos más relevantes de la trama. Los diálogos deben ser representados con la raya: '—'."
    response = client.chat.completions.create(
        model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Función para guardar la novela en un archivo .docx
def guardar_como_docx(titulo, contenido):
    doc = Document()
    doc.add_heading(titulo, 0)
    for capitulo in contenido:
        doc.add_heading(f"Capítulo {capitulo['numero']}: {capitulo['titulo']}", level=1)
        doc.add_paragraph(capitulo['texto'])
    doc.save(f"{titulo}.docx")

# Interfaz de Streamlit
st.title("Generador de Novelas")
st.write("Especifica el título y el género de la novela para generar una novela de 24 capítulos.")

# Entradas del usuario
titulo = st.text_input("Título de la novela")
genero = st.selectbox("Género", ["Ciencia Ficción", "Fantasía", "Romántico", "Misterio", "Aventura"])

# Crear una tabla de contenidos inicial
contenido = []

# Función principal para generar la novela
if st.button("Generar novela"):
    if not titulo:
        st.warning("Por favor ingresa un título para la novela.")
    else:
        st.write(f"Generando la novela '{titulo}' del género {genero}...")
        for capitulo_num in range(1, 25):
            # Mostrar al usuario que se está generando el capítulo
            st.write(f"Generando capítulo {capitulo_num}...")
            capitulo = generar_capitulo(titulo, genero, capitulo_num)
            contenido.append({
                "numero": capitulo_num,
                "titulo": f"Capítulo {capitulo_num}",
                "texto": capitulo
            })
            st.write(capitulo)
            time.sleep(2)  # Pausa entre capítulos para evitar sobrecargar la API
        
        # Después de generar todos los capítulos, ofrecer la descarga
        st.success(f"¡La novela '{titulo}' ha sido generada con éxito! Puedes descargarla ahora.")
        guardar_como_docx(titulo, contenido)
        st.download_button(
            label="Descargar novela completa",
            data=f"{titulo}.docx",
            file_name=f"{titulo}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
