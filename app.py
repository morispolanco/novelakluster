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

    Instrucciones adicionales para el capítulo:
    1. **Desarrollo de personajes**: Profundiza en los pensamientos, emociones y trasfondos de los personajes principales. Explora sus motivaciones y conflictos internos.
    2. **Descripciones detalladas**: Incluye descripciones elaboradas de los escenarios, ambientes y situaciones. Ayuda al lector a visualizar el mundo de la historia.
    3. **Subtramas**: Introduce una subtrama que complemente la historia principal. Puede ser un conflicto secundario, una relación entre personajes o un misterio que se desarrolla en paralelo.
    4. **Diálogos extensos**: Usa diálogos bien construidos para revelar información importante sobre los personajes o la trama. Asegúrate de que los diálogos sean naturales y contribuyan al desarrollo de la historia.
    5. **Reflexiones internas**: Permite que los personajes reflexionen sobre lo que está sucediendo. Esto añade profundidad psicológica y ayuda al lector a conectarse con los personajes.
    6. **Eventos detallados**: Si hay acciones o eventos clave, descríbelos con detalle. Por ejemplo, en lugar de resumir una batalla, describe cada movimiento, estrategia y emoción.
    7. **Flashbacks o recuerdos**: Usa flashbacks para explorar el pasado de los personajes o eventos importantes que influyen en la trama actual.
    8. **Expansión del mundo**: Si la novela es de fantasía o ciencia ficción, dedica tiempo a desarrollar el mundo, sus reglas, culturas y sistemas.
    9. **Ritmo controlado**: Asegúrate de que el ritmo de la historia no sea demasiado rápido. Tómate tu tiempo para desarrollar cada escena de manera natural.

    El capítulo debe tener alrededor de 3000 a 4000 palabras. Usa rayas (—) para los diálogos. Por ejemplo:
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
