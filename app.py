import streamlit as st
from openai import OpenAI
import time
from docx import Document
from io import BytesIO

# Configuración de Streamlit
st.set_page_config(page_title="Generador de Novelas", page_icon="📚")

# Esconder API Key en los secrets de Streamlit
API_KEY = st.secrets["KLUSTERAI_API_KEY"]

# Cliente OpenAI compatible
client = OpenAI(
    base_url="https://api.kluster.ai/v1",
    api_key=API_KEY
)

# Función para generar texto con la API
def generate_text(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",  # Ajusta según el modelo disponible
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.7
    )
    return response.choices[0].message.content

# Función para guardar la novela en un archivo .docx
def save_to_docx(chapters, title):
    doc = Document()
    doc.add_heading(title, level=1)
    for i, chapter in enumerate(chapters, start=1):
        doc.add_heading(f"Capítulo {i}", level=2)
        doc.add_paragraph(chapter)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# Título de la aplicación
st.title("Generador de Novelas 📚")
st.write("Crea tu propia novela de 24 capítulos con detalles ricos y emocionantes.")

# Inputs del usuario
genre = st.text_input("Género de la novela (ej. Fantasía, Ciencia Ficción, Romance):")
title = st.text_input("Título de la novela:")
if st.button("Generar Novela"):
    if genre and title:
        st.session_state['genre'] = genre
        st.session_state['title'] = title
        st.session_state['chapters'] = []
        st.session_state['current_chapter'] = 1
        st.success("¡Comenzando la generación de la novela!")
    else:
        st.error("Por favor, ingresa el género y el título.")

# Generación de capítulos
if 'chapters' in st.session_state and st.session_state['current_chapter'] <= 24:
    with st.spinner(f"Generando Capítulo {st.session_state['current_chapter']}..."):
        # Generar trama y tabla de contenidos si es el primer capítulo
        if st.session_state['current_chapter'] == 1:
            st.subheader("Trama y Tabla de Contenidos")
            plot_prompt = f"Escribe una trama completa para una novela de {st.session_state['genre']} titulada '{st.session_state['title']}' con 24 capítulos. Incluye una tabla de contenidos con títulos de cada capítulo."
            plot_and_toc = generate_text(plot_prompt)
            st.session_state['plot_and_toc'] = plot_and_toc
            st.write(plot_and_toc)

        # Generar el capítulo actual
        chapter_prompt = f"Escribe el Capítulo {st.session_state['current_chapter']} de una novela de {st.session_state['genre']} titulada '{st.session_state['title']}'. Usa los siguientes elementos: Desarrollo de personajes profundo, descripciones detalladas, subtramas, diálogos extensos con rayas (—), reflexiones internas, eventos detallados, flashbacks y expansión del mundo. Asegúrate de que tenga alrededor de 2000 palabras."
        chapter_text = generate_text(chapter_prompt)
        st.session_state['chapters'].append(chapter_text)

        # Mostrar el capítulo generado
        st.subheader(f"Capítulo {st.session_state['current_chapter']}")
        st.write(chapter_text)

        # Avanzar al siguiente capítulo
        st.session_state['current_chapter'] += 1

# Descargar novela completa
if 'chapters' in st.session_state and st.session_state['current_chapter'] > 24:
    st.success("¡Novela completa generada!")
    docx_file = save_to_docx(st.session_state['chapters'], st.session_state['title'])
    st.download_button(
        label="Descargar Novela Completa (.docx)",
        data=docx_file,
        file_name=f"{st.session_state['title']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
