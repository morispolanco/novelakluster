import streamlit as st
import json
import requests

# Configuración de la página
st.set_page_config(page_title="Generador de Novelas", layout="wide")

# Configuración de OpenRouter
OPENROUTER_API_KEY = "tu_openrouter_api_key"  # Reemplaza con tu API key real
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generar_contenido(messages):
    try:
        response = requests.post(
            url=OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://tusitio.com",  # Opcional
                "X-Title": "Generador de Novelas",  # Opcional
            },
            json={
                "model": "sophosympatheia/rogue-rose-103b-v0.2:free",  # Puedes cambiar el modelo
                "messages": messages,
                "max_tokens": 5000,
                "temperature": 0.7,
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error al generar contenido: {str(e)}")
        return None

def generar_personajes(genero):
    messages = [
        {"role": "system", "content": "Eres un escritor experto en crear personajes complejos y memorables."},
        {"role": "user", "content": f"""Crea 5 personajes principales para una novela de {genero}.
        Incluye para cada uno:
        - Nombre
        - Edad
        - Descripción física
        - Personalidad
        - Rol en la historia
        Devuelve la respuesta en formato JSON."""}
    ]
    contenido = generar_contenido(messages)
    if contenido:
        return json.loads(contenido)
    return None

def generar_trama(genero, titulo, personajes):
    messages = [
        {"role": "system", "content": "Eres un escritor experto en crear tramas complejas y cautivadoras."},
        {"role": "user", "content": f"""Crea una trama completa para una novela de {genero} titulada '{titulo}'.
        Personajes: {json.dumps(personajes, ensure_ascii=False)}

        La respuesta debe ser un JSON con:
        - título
        - tema_principal
        - sinopsis
        - capitulos: (diccionario con 10 capítulos numerados)

        Cada capítulo debe tener:
        - título
        - resumen
        - eventos_principales
        - desarrollo_personajes"""}
    ]
    contenido = generar_contenido(messages)
    if contenido:
        return json.loads(contenido)
    return None

def escribir_capitulo(numero, titulo, trama, personajes):
    messages = [
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
    ]
    return generar_contenido(messages)

def crear_documento_texto(titulo, capitulos):
    filename = f"{titulo.lower().replace(' ', '_')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{titulo}\n\n")
        for num, contenido in capitulos.items():
            f.write(f"\nCapítulo {num}\n")
            f.write(f"{contenido}\n")
            f.write("\n" + "="*50 + "\n")
    return filename

# Inicialización del estado de la sesión
if 'estado' not in st.session_state:
    st.session_state.estado = 'inicio'
    st.session_state.capitulos = {}
    st.session_state.personajes = None
    st.session_state.trama = None
    st.session_state.genero = ""
    st.session_state.titulo = ""

# Título principal
st.title("Generador de Novelas con IA")

# Sidebar para mostrar progreso
with st.sidebar:
    st.write("### Progreso de la Novela")
    if st.session_state.personajes:
        st.success("✅ Personajes generados")
    if st.session_state.trama:
        st.success("✅ Trama generada")
    if st.session_state.capitulos:
        progress = len(st.session_state.capitulos) / 10
        st.progress(progress)
        st.write(f"Capítulos completados: {len(st.session_state.capitulos)}/10")

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

        if capitulo_actual <= 10:
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
        if len(st.session_state.capitulos) == 10:
            st.write("### ¡Novela Completa! 🎉")
            if st.button("Descargar Novela"):
                filename = crear_documento_texto(
                    st.session_state.trama['titulo'],
                    st.session_state.capitulos
                )
                with open(filename, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Novela",
                        data=file,
                        file_name=filename,
                        mime="text/plain"
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

# Guardar progreso automáticamente
if st.session_state.personajes or st.session_state.trama or st.session_state.capitulos:
    try:
        progress_data = {
            'personajes': st.session_state.personajes,
            'trama': st.session_state.trama,
            'capitulos': st.session_state.capitulos,
            'genero': st.session_state.genero,
            'titulo': st.session_state.titulo
        }
        with open('novel_progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.sidebar.warning("No se pudo guardar el progreso")
