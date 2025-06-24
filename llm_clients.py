import os
from dotenv import load_dotenv
import openai
import anthropic
import google.generativeai as genai

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# --- Cliente de OpenAI (ChatGPT) ---
def generate_with_openai(prompt: str, model: str) -> str:
    """Genera una respuesta usando la API de OpenAI."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("La clave OPENAI_API_KEY no se encontró en el archivo .env")
        
        client = openai.OpenAI(api_key=api_key)
        
        # Para generar Markdown, no forzamos la respuesta JSON
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en la creación de actas de reunión en formato Markdown."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        raise RuntimeError(f"Error con la API de OpenAI: {e}")

# --- Cliente de Anthropic (Claude) ---
def generate_with_anthropic(prompt: str, model: str) -> str:
    """Genera una respuesta usando la API de Anthropic."""
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("La clave ANTHROPIC_API_KEY no se encontró en el archivo .env")

        client = anthropic.Anthropic(api_key=api_key)
        
        # Extraer el inicio del prompt para usarlo como 'system' prompt
        system_prompt = "Eres un asistente experto en la creación de actas de reunión. Tu tarea es analizar la transcripción y generar un acta formal y detallada en formato Markdown."
        
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": prompt 
                }
            ]
        )
        return response.content[0].text or ""
    except Exception as e:
        raise RuntimeError(f"Error con la API de Anthropic: {e}")


# --- Cliente de Google (Gemini) ---
def generate_with_google(prompt: str, model: str) -> str:
    """Genera una respuesta usando la API de Google."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("La clave GOOGLE_API_KEY no se encontró en el archivo .env")

        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model)
        
        # Para generar Markdown, no forzamos la respuesta JSON
        response = gemini_model.generate_content(prompt)
        return response.text or ""
    except Exception as e:
        raise RuntimeError(f"Error con la API de Google: {e}")