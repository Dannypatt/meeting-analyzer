import ollama
import json
import os # Importar el módulo os

# Define la ruta al archivo del prompt
# Esto asegura que el archivo se encuentre sin importar desde dónde se ejecute el script principal
PROMPT_FILE = os.path.join(os.path.dirname(__file__), 'ollama_prompt_template.txt')

# Cargar el prompt desde el archivo
try:
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        OLLAMA_PROMPT = f.read()
except FileNotFoundError:
    raise RuntimeError(f"Error: El archivo de plantilla del prompt no se encontró en: {PROMPT_FILE}")
except Exception as e:
    raise RuntimeError(f"Error al cargar el archivo de prompt: {e}")

def generate_minutes_with_ollama(transcription_text: str, model_name: str, params: dict) -> dict:
    """
    Envía la transcripción a Ollama y procesa la respuesta para obtener el acta.
    """
    client = ollama.Client()

    # Formatear el prompt con la transcripción
    prompt_formatted = OLLAMA_PROMPT.format(transcription_text=transcription_text)

    # --- AÑADE ESTAS LÍNEAS PARA DEBUGGING ---
    print(f"DEBUG: Prompt enviado a Ollama (primeros 500 chars):\n{prompt_formatted[:500]}...")
    print(f"DEBUG: Longitud total del prompt: {len(prompt_formatted)} caracteres.")
    # ----------------------------------------

    options = {
        "temperature": params.get("temperature", 0.7),
        "num_predict": params.get("num_predict", 4096),
        "num_ctx": params.get("num_ctx", 4096)
        # Añadir top_k, top_p si están en params y el modelo los soporta
    }

    try:
        response = client.generate(
            model=model_name,
            prompt=prompt_formatted,
            options=options,
            format='json' # Pide a Ollama que la salida sea JSON
        )
        
        raw_json_str = response['response']

        # --- AÑADE ESTAS LÍNEAS PARA DEBUGGING ---
                # --- AÑADE ESTAS LÍNEAS PARA DEBUGGING ---
        print(f"DEBUG: ----- INICIO RESPUESTA CRUDA DE OLLAMA -----")
        print(raw_json_str)
        print(f"DEBUG: ----- FIN RESPUESTA CRUDA DE OLLAMA -----")
        # ----------------------------------------
        # ----------------------------------------

        meeting_data = json.loads(raw_json_str)

        # --- AÑADE ESTA LÍNEA PARA DEBUGGING ---
        print(f"DEBUG: JSON parseado de Ollama:\n{json.dumps(meeting_data, indent=2)}")
        # ----------------------------------------
        
        return meeting_data

    except ollama.ResponseError as e:
        raise RuntimeError(f"Error de Ollama: {e.error}")
    except json.JSONDecodeError as e:
        # Esto ocurre si Ollama no devuelve un JSON válido a pesar de la instrucción
        # Podrías querer loguear response['response'] aquí para depuración
        raise ValueError(f"Ollama no devolvió un JSON válido. Error de parseo: {e}\n"
                         f"Respuesta cruda (primeros 500 chars): {raw_json_str[:500] if raw_json_str else 'N/A'}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado al comunicarse con Ollama: {e}")

if __name__ == '__main__':
    # Ejemplo de uso (esto no se ejecutará en la app principal)
    # Asegúrate de tener un modelo como 'mistral' o 'llama2' instalado en Ollama
    # Ollama debe estar corriendo en http://localhost:11434
    
    # transcription_ejemplo = """
    # Juan: Hola a todos, gracias por unirse. El objetivo de hoy es revisar el progreso del proyecto Alfa y planificar los próximos pasos.
    # María: Por mi parte, el módulo de autenticación está al 80%, pero tengo un pequeño bloqueo con la integración de la API externa.
    # Pedro: Entendido, María. ¿Necesitas ayuda de mi parte con eso? Podríamos revisar juntos la documentación.
    # María: Sí, Pedro, sería genial si pudieras mirar los logs conmigo mañana.
    # Juan: Perfecto. Entonces, tarea para María y Pedro: revisar la integración de la API para mañana, 10 AM.
    # Ana: En cuanto al diseño de la interfaz, hemos terminado los mockups y los hemos compartido en Confluence. Necesitamos la aprobación final de Juan.
    # Juan: Excelente, Ana. Revisaré los mockups hoy mismo y daré feedback antes del final del día. Decisión: Aprobación del diseño de UI por Juan antes de fin de día.
    # María: También quería preguntar sobre la fecha de entrega del proyecto. ¿Sigue siendo el 15 de marzo?
    # Juan: Sí, la fecha de entrega sigue siendo el 15 de marzo. Eso es una decisión clave.
    # Pedro: Tengo una duda sobre el ambiente de producción. ¿Podemos tener acceso para pruebas de rendimiento la próxima semana?
    # Juan: Sí, Pedro. Tarea: Solicitar acceso al ambiente de producción para pruebas de rendimiento a Juan, fecha límite: 2 de marzo.
    # """
    
    # print("Generando acta con Ollama...")
    # try:
    #     test_params = {"temperature": 0.5, "num_predict": 2048, "num_ctx": 4096}
    #     acta_data = generate_minutes_with_ollama(transcription_ejemplo, "mistral", test_params)
    #     print("\n--- Acta Generada (JSON) ---")
    #     print(json.dumps(acta_data, indent=2))
    # except Exception as e:
    #     print(f"Error al generar acta: {e}")
    pass