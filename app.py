import streamlit as st
from openai import OpenAI
import time
import docx
import os

# Configuración de la API
client = OpenAI(
    base_url="https://api.kluster.ai/v1",
    api_key=st.secrets["KLUSTERAI_API_KEY"]
)

# Función para generar un capítulo
def generar_capitulo(genero, titulo, capitulo_num, trama_principal, personajes_principales):
    prompt = f"""
    Escribe el capítulo {capitulo_num} de una novela titulada "{titulo}" del género {genero}.
    La trama principal es: {trama_principal}.
    Los personajes principales son: {personajes_principales}.
    El capítulo debe tener alrededor de 2000 palabras y debe incluir:
    - Desarrollo de personajes: Profundiza en los pensamientos, emociones y trasfondos de los personajes.
    - Descripciones detalladas: Incluye descripciones elaboradas de los escenarios, ambientes y situaciones.
    - Subplots o tramas secundarias: Introduce subtramas que complementen la historia principal.
    - Diálogos extensos: Usa rayas para los diálogos, ejemplo: —Así es—.
    - Reflexiones internas: Permite que los personajes reflexionen sobre lo que está sucediendo.
    - Eventos detallados: Describe acciones o eventos clave con más detalle.
    - Flashbacks o recuerdos: Usa flashbacks para explorar el pasado de los personajes.
    - Expansión del mundo: Si es fantasía o ciencia ficción, desarrolla el mundo, sus reglas, culturas y sistemas.
    - Pacing controlado: Asegúrate de que el ritmo de la historia no sea demasiado rápido.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",  # O el modelo que prefieras
        messages=[
            {"role": "system", "content": "Eres un escritor de novelas experto."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000  # Ajusta según sea necesario
    )
    
    return response.choices[0].message.content

# Función para generar la tabla de contenidos
def generar_tabla_contenidos(titulo, trama_principal, personajes_principales):
    prompt = f"""
    Genera una tabla de contenidos para una novela titulada "{titulo}" del género {genero}.
    La trama principal es: {trama_principal}.
    Los personajes principales son: {personajes_principales}.
    La novela debe tener 24 capítulos. Proporciona un título breve para cada capítulo.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",  # O el modelo que prefieras
        messages=[
            {"role": "system", "content": "Eres un escritor de novelas experto."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000  # Ajusta según sea necesario
    )
    
    return response.choices[0].message.content

# Función para guardar la novela en un archivo .docx
def guardar_novela_docx(titulo, capitulos):
    doc = docx.Document()
    doc.add_heading(titulo, 0)
    
    for capitulo_num, contenido in capitulos.items():
        doc.add_heading(f"Capítulo {capitulo_num}", level=1)
        doc.add_paragraph(contenido)
    
    doc.save(f"{titulo}.docx")

# Interfaz de Streamlit
st.title("Generador de Novelas")

# Entradas del usuario
genero = st.selectbox("Selecciona el género de la novela:", ["Fantasía", "Ciencia Ficción", "Romance", "Misterio", "Terror"])
titulo = st.text_input("Título de la novela:")
personajes_principales = st.text_area("Describe los personajes principales:")
trama_principal = st.text_area("Describe la trama principal:")

if st.button("Generar Novela"):
    if not titulo or not personajes_principales or not trama_principal:
        st.error("Por favor, completa todos los campos.")
    else:
        with st.spinner("Generando la tabla de contenidos..."):
            tabla_contenidos = generar_tabla_contenidos(titulo, trama_principal, personajes_principales)
        
        st.subheader("Tabla de Contenidos")
        st.write(tabla_contenidos)
        
        capitulos = {}
        for i in range(1, 25):
            with st.spinner(f"Generando Capítulo {i}..."):
                capitulo = generar_capitulo(genero, titulo, i, trama_principal, personajes_principales)
                capitulos[i] = capitulo
                st.subheader(f"Capítulo {i}")
                st.write(capitulo)
        
        # Guardar la novela en un archivo .docx
        guardar_novela_docx(titulo, capitulos)
        
        # Ofrecer descarga del archivo .docx
        with open(f"{titulo}.docx", "rb") as file:
            btn = st.download_button(
                label="Descargar Novela Completa",
                data=file,
                file_name=f"{titulo}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        st.success("¡Novela generada y lista para descargar!")
