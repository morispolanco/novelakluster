import streamlit as st
import time
import json
import docx
from docx.shared import Inches
import os
from openai import OpenAI

# Configuración de la página
st.set_page_config(page_title="Generador de Novelas", layout="wide")

# Configuración de Kluster.ai
client = OpenAI(
    base_url="https://api.kluster.ai/v1",
    api_key=st.secrets["kluster_api_key"]
)

def generar_personajes(genero):
    try:
        response = client.chat.completions.create(
            model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "Eres un escritor experto en crear personajes complejos y memorables."},
                {"role": "user", "content": f"""Crea 5 personajes principales para una novela de {genero}.
                Incluye para cada uno:
                - Nombre
                - Edad
                - Descripción física
                - Personalidad
                - Rol en la historia
                Devuelve la respuesta en formato JSON."""}
            ],
            metadata={
                "@kluster.ai": {
                    "async": False,
                    "completion_window": "1h"
                }
            }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error al generar personajes: {str(e)}")
        return None

def generar_trama(genero, titulo, personajes):
    try:
        response = client.chat.completions.create(
            model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "Eres un escritor experto en crear tramas complejas y cautivadoras."},
                {"role": "user", "content": f"""Crea una trama completa para una novela de {genero} titulada '{titulo}'.
                Personajes: {json.dumps(personajes, ensure_ascii=False)}

                La respuesta debe ser un JSON con:
                - título
                - tema_principal
                - sinopsis
                - capitulos: (diccionario con 24 capítulos numerados)

                Cada capítulo debe tener:
                - título
                - resumen
                - eventos_principales
                - desarrollo_personajes"""}
            ],
            metadata={
                "@kluster.ai": {
                    "async": False,
                    "completion_window": "1h"
                }
            }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error al generar trama: {str(e)}")
        return None

def escribir_capitulo(numero, titulo, trama, personajes):
    try:
        response = client.chat.completions.create(
            model="klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "Eres un novelista experto que escribe capítulos detallados y envolventes."},
                {"role": "user", "content": f"""Escribe el capítulo {numero} de la novela '{titulo}'.
                Información del capítulo: {json.dumps(trama['capitulos'][str(numero)], ensure_ascii=False)}
                Personajes: {json.dumps(personajes, ensure_ascii=False)}

                Requisitos:
                - Aproximadamente 2000 palabras
                - Usar raya (—) para diálogos
                - Desarrollo profundo de personajes
                - Descripciones detalladas
                - Diálogos elaborados
                - Reflexiones internas
                - Ritmo narrativo controlado"""}
            ],
            metadata={
                "@kluster.ai": {
                    "async": False,
                    "completion_window": "1h"
                }
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al escribir capítulo: {str(e)}")
        return None

def crear_documento_word(titulo, capitulos):
    doc = docx.Document()
    doc.add_heading(titulo, 0)

    for num, contenido in capitulos.items():
        doc.add_heading(f'Capítulo {num}', 1)
        doc.add_paragraph(contenido)
        doc.add_page_break()

    filename = f"{titulo.lower().replace(' ', '_')}.docx"
    doc.save(filename)
    return filename

# Interfaz de Streamlit
st.title("Generador de Novelas")

# Inicialización del estado de la sesión
if 'estado' not in st.session_state:
    st.session_state.estado = 'inicio'
    st.session_state.capitulos = {}
    st.session_state.personajes = None
    st.session_state.trama = None
    st.session_state.genero = ""
    st.session_state.titulo = ""

# Sidebar para mostrar progreso
with st.sidebar:
    st.write("### Progreso de la Novela")
    if st.session_state.personajes:
        st.success("✅ Personajes generados")
    if st.session_state.trama:
        st.success("✅ Trama generada")
    if st.session_state.capitulos:
        progress = len(st.session_state.capitulos) / 24
        st.progress(progress)
        st.write(f"Capítulos completados: {len(st.session_state.capitulos)}/24")

# Página principal
if st.session_state.estado == 'inicio':
    st.write("### Bienvenido al Generador de Novelas")
    st.write("Por favor, introduce los detalles iniciales de tu novela.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.genero = st.text_input("Género de la novela:",
                                               help="Por ejemplo: Fantasía, Romance, Ciencia Ficción, etc.")
    with col2:
        st.session_state.titulo = st.text_input("Título de la novela:")

    if st.button("Comenzar Novela", disabled=not (st.session_state.genero and st.session_state.titulo)):
        with st.spinner("Generando personajes y trama..."):
            st.session_state.personajes = generar_personajes(st.session_state.genero)
            if st.session_state.personajes:
                st.session_state.trama = generar_trama(
                    st.session_state.genero,
                    st.session_state.titulo,
                    st.session_state.personajes
                )
                if st.session_state.trama:
                    st.session_state.estado = 'escribiendo'
                    st.rerun()

elif st.session_state.estado == 'escribiendo':
    # Tabs para organizar la información
    tab1, tab2, tab3 = st.tabs(["📝 Escritura", "👥 Personajes", "📋 Trama"])

    with tab1:
        capitulo_actual = len(st.session_state.capitulos) + 1

        if capitulo_actual <= 24:
            st.write(f"### Escribiendo Capítulo {capitulo_actual}")
            if st.button("Generar Capítulo"):
                with st.spinner(f"Escribiendo capítulo {capitulo_actual}..."):
                    contenido = escribir_capitulo(
                        capitulo_actual,
                        st.session_state.trama['titulo'],
                        st.session_state.trama,
                        st.session_state.personajes
                    )
                    if contenido:
                        st.session_state.capitulos[str(capitulo_actual)] = contenido
                        st.rerun()

        # Mostrar capítulos escritos
        st.write("### Capítulos Completados")
        for num, contenido in st.session_state.capitulos.items():
            with st.expander(f"Capítulo {num}"):
                st.write(contenido)

        # Opción para descargar cuando la novela está completa
        if len(st.session_state.capitulos) == 24:
            st.write("### ¡Novela Completa! 🎉")
            if st.button("Descargar Novela en Word"):
                filename = crear_documento_word(
                    st.session_state.trama['titulo'],
                    st.session_state.capitulos
                )
                with open(filename, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Novela",
                        data=file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

    with tab2:
        st.write("### Personajes de la Novela")
        st.json(st.session_state.personajes)

    with tab3:
        st.write("### Trama General")
        st.json(st.session_state.trama)

# Botón para reiniciar en cualquier momento
if st.sidebar.button("🔄 Reiniciar Novela"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
