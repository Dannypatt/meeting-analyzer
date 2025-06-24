import ollama
import os
from datetime import datetime
from llm_clients import generate_with_openai, generate_with_anthropic, generate_with_google

OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
PROMPT_FILE = os.path.join(os.path.dirname(__file__), 'ollama_prompt_template.txt')
try:
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        OLLAMA_PROMPT_TEMPLATE = f.read()
except FileNotFoundError:
    raise RuntimeError(f"Error: El archivo de plantilla del prompt no se encontró en: {PROMPT_FILE}")

def generate_minutes(provider: str, model_name: str, transcription_text: str, user_context: str, params: dict) -> str:
    """
    Función principal que despacha la solicitud al proveedor de LLM correcto para generar MARKDOWN.
    """
    today_date = datetime.now().strftime("%Y-%m-%d")
    prompt_formatted = OLLAMA_PROMPT_TEMPLATE.format(
        user_context=user_context if user_context else "Ninguno.",
        current_date=today_date, 
        transcription_text=transcription_text
    )
    
    acta_markdown = ""

    print(f"DEBUG: Enviando solicitud a {provider} con el modelo {model_name}...")

    try:
        if provider == "Ollama":
            client = ollama.Client(host=OLLAMA_HOST)
            response = client.generate(
                model=model_name,
                prompt=prompt_formatted,
                options={
                    "temperature": params.get("temperature"),
                    "num_predict": params.get("num_predict"),
                    "num_ctx": params.get("num_ctx")
                }
                # ¡Ya no forzamos el formato JSON!
            )
            acta_markdown = response.get('response', '')
        
        # La lógica para otros proveedores se puede adaptar para que también devuelvan Markdown
        elif provider == "OpenAI":
            # Nota: generate_with_openai necesita ser adaptado para no forzar JSON
            acta_markdown = generate_with_openai(prompt_formatted, model_name) 
        elif provider == "Anthropic":
            # Nota: generate_with_anthropic necesita ser adaptado para no forzar JSON
            acta_markdown = generate_with_anthropic(prompt_formatted, model_name)
        elif provider == "Google":
             # Nota: generate_with_google necesita ser adaptado para no forzar JSON
            acta_markdown = generate_with_google(prompt_formatted, model_name)
        else:
            raise ValueError(f"Proveedor de LLM no reconocido: {provider}")

        print(f"DEBUG: Respuesta Markdown de {provider}:\n{acta_markdown[:1000]}...")
        
        if not acta_markdown.strip():
            print(f"ADVERTENCIA: {provider} devolvió una respuesta vacía.")
            return "El modelo no generó un acta. Por favor, inténtelo de nuevo."
            
        return acta_markdown

    except Exception as e:
        import traceback
        print(f"ERROR al procesar con {provider}:")
        traceback.print_exc()
        raise e