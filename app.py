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

# [El resto del código permanece igual...]
