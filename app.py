import streamlit as st
from openai import OpenAI
from docx import Document
import io

# Configura la API key desde los secrets de Streamlit
api_key = st.secrets["my_klusterai_api_key"]

# Inicializa el cliente de OpenAI
client = OpenAI(base_url="https://api.kluster.ai/v1", api_key=api_key)

# Función para generar la trama de la novela
def generar_trama(genero, titulo):
    prompt = f"Genera una trama para una novela de género {genero} titulada '{titulo}'. La trama debe ser lo suficientemente detallada para desarrollar 24 capítulos."
    response = client.chat.completions.create(
        model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Función para generar la tabla de contenidos
def generar_tabla_contenidos(trama):
    prompt = f"Genera una tabla de contenidos con 24 capítulos basada en la siguiente trama:\n\n{trama}"
    response = client.chat.completions.create(
        model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Función para generar un capítulo con diálogos formateados
def generar_capitulo(trama, tabla_contenidos, capitulo):
    prompt = f"""Escribe el capítulo {capitulo} de una novela basada en la siguiente trama y tabla de contenidos:
    
    Trama:
    {trama}

    Tabla de contenidos:
    {tabla_contenidos}

    El capítulo debe tener alrededor de 2000 palabras. Usa rayas (—) para los diálogos. Por ejemplo:
    — Hola, ¿cómo estás? —preguntó Juan.
    — Bien, gracias —respondió María.
    """
    response = client.chat.completions.create(
        model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Función para generar un archivo .docx con la novela completa
def generar_docx(novela):
    doc = Document()
    for capitulo_num, capitulo_texto in novela.items():
        doc.add_heading(f"Capítulo {capitulo_num}", level=1)
        doc.add_paragraph(capitulo_texto)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Interfaz de Streamlit
st.title("Generador de Novelas")

# Entradas del usuario
genero = st.text_input("Especifica el género de la novela:")
titulo = st.text_input("Especifica el título de la novela:")

if genero and titulo:
    if 'trama' not in st.session_state:
        st.session_state.trama = generar_trama(genero, titulo)
        st.session_state.tabla_contenidos = generar_tabla_contenidos(st.session_state.trama)
        st.session_state.capitulo_actual = 1
        st.session_state.novela = {}  # Diccionario para almacenar la novela completa

    st.write("### Trama de la Novela")
    st.write(st.session_state.trama)

    st.write("### Tabla de Contenidos")
    st.write(st.session_state.tabla_contenidos)

    st.write(f"### Capítulo {st.session_state.capitulo_actual}")
    capitulo = generar_capitulo(st.session_state.trama, st.session_state.tabla_contenidos, st.session_state.capitulo_actual)
    st.write(capitulo)

    # Guardar el capítulo en la novela completa
    st.session_state.novela[st.session_state.capitulo_actual] = capitulo

    if st.button("Generar Siguiente Capítulo"):
        if st.session_state.capitulo_actual < 24:
            st.session_state.capitulo_actual += 1
            st.rerun()
        else:
            st.write("¡Has completado la novela de 24 capítulos!")

            # Generar y ofrecer la descarga del archivo .docx
            st.write("### Descargar Novela Completa")
            docx_file = generar_docx(st.session_state.novela)
            st.download_button(
                label="Descargar Novela en .docx",
                data=docx_file,
                file_name=f"{titulo}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
