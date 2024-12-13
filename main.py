
import sys
import google.generativeai as genai
from googlesearch import search
import requests
from bs4 import BeautifulSou

def buscar_y_extraer(sentencia, num_paginas=5):
    # Buscar URLs usando Google
    urls = []
    for i, url in enumerate(search(sentencia, stop=num_paginas), start=1):
        urls.append(url)

    # Extraer información de las páginas
    resultados = []
    for url in urls:
        try:
            print(f"Extrayendo contenido de: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraer título y contenido del cuerpo
            titulo = soup.title.string if soup.title else "Sin título"
            contenido = soup.get_text()[:1000]  # Extraer los primeros 1000 caracteres de texto

            print(f"Contenido extraído: {contenido}\n")  # Imprimir el contenido extraído

            resultados.append({
                "url": url,
                "titulo": titulo,
                "contenido": contenido
            })
        except Exception as e:
            print(f"Error al procesar {url}: {e}")

    return resultados

def procesar_con_gemini(sentencia, resultados):
    # Preparar texto para procesar con Gemini
    contenido_agregado = "\n".join([f"{r['titulo']}: {r['contenido']}" for r in resultados])
    consulta_extendida = f"{sentencia}\nBasado en las siguientes fuentes:\n{contenido_agregado}"

    # Configurar Gemini
    genai.configure(api_key="TU_API_KEY")
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generar respuesta con Gemini
    response = model.generate_content(consulta_extendida)
    print(f"Respuesta de Gemini: {response.text}\n")  # Imprimir la respuesta de Gemini
    return response.text

def determinar_veracidad(sentencia):
    # Configurar Gemini
    genai.configure(api_key="TU_API_KEY")
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generar respuesta inicial con Gemini
    response = model.generate_content(f"Determina si la siguiente afirmación es verdadera o falsa: {sentencia}")
    normalized_response = response.text.strip().lower()

    if "true" in normalized_response or "verdadero" in normalized_response:
        return "True"
    elif "false" in normalized_response or "falso" in normalized_response:
        return "False"
    else:
        print("No se pudo determinar una respuesta clara. Realizando búsqueda y procesamiento adicional...")
        resultados = buscar_y_extraer(sentencia)

        if not resultados:
            return "No se encontraron resultados relevantes."

        # Procesar nuevamente con Gemini usando resultados del scraping
        nueva_respuesta = procesar_con_gemini(sentencia, resultados)
        if "true" in nueva_respuesta.lower() or "verdadero" in nueva_respuesta.lower():
            return "True"
        elif "false" in nueva_respuesta.lower() or "falso" in nueva_respuesta.lower():
            return "False"
        else:
            # Análisis adicional basado en coincidencias
            if "confirma" in nueva_respuesta.lower() or "apoya" in nueva_respuesta.lower():
                return "True"
            elif "desmiente" in nueva_respuesta.lower() or "contradice" in nueva_respuesta.lower():
                return "False"
            else:
                return "Consulta procesada pero sin respuesta clara."
            


# Solicitar consulta al usuario
user_input = input("Escriba su consulta: ")
respuesta_final = determinar_veracidad(user_input)
