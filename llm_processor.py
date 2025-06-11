import ollama
import json
import os

# Configurar el host de Ollama desde una variable de entorno,
# con 'http://localhost:11434' como valor predeterminado si no se especifica.
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

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
    client = ollama.Client(host=OLLAMA_HOST)

    # Formatear el prompt con la transcripción
    prompt_formatted = OLLAMA_PROMPT.format(transcription_text=transcription_text)

    # --- DEBUGGING ---
    print(f"DEBUG: Prompt enviado a Ollama (primeros 500 chars):\n{prompt_formatted[:500]}...")
    print(f"DEBUG: Longitud total del prompt: {len(prompt_formatted)} caracteres.")
    # -----------------

    options = {
        "temperature": params.get("temperature", 0.7),
        "num_predict": params.get("num_predict", 8192), # Aumentado por defecto
        "num_ctx": params.get("num_ctx", 16384)       # Aumentado por defecto
    }

    try:
        response = client.generate(
            model=model_name,
            prompt=prompt_formatted,
            options=options,
            format='json' # Pide a Ollama que la salida sea JSON
        )
        
        raw_json_str = response['response']

        # --- DEBUGGING COMPLETO ---
        print(f"DEBUG: ----- INICIO RESPUESTA CRUDA DE OLLAMA -----")
        print(raw_json_str)
        print(f"DEBUG: ----- FIN RESPUESTA CRUDA DE OLLAMA -----")
        # --------------------------

        # Si la respuesta está vacía, devuelve un diccionario vacío para evitar el error 'NoneType'
        if not raw_json_str.strip():
            print("ADVERTENCIA: Ollama devolvió una respuesta vacía.")
            return {}

        meeting_data = json.loads(raw_json_str)

        # --- DEBUGGING FINAL ---
        print(f"DEBUG: JSON parseado de Ollama:\n{json.dumps(meeting_data, indent=2)}")
        # -----------------------
        
        return meeting_data

    except ollama.ResponseError as e:
        raise RuntimeError(f"Error de Ollama: {e.error}")
    except json.JSONDecodeError as e:
        # Esto ocurre si Ollama no devuelve un JSON válido a pesar de la instrucción
        raise ValueError(f"Ollama no devolvió un JSON válido. Error de parseo: {e}\n"
                         f"Respuesta cruda: {raw_json_str if 'raw_json_str' in locals() else 'No se recibió respuesta'}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado al comunicarse con Ollama: {e}")