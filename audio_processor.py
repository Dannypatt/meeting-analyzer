import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

# Cargar las variables de entorno para obtener la API Key
load_dotenv()

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe un archivo de audio/video a texto usando la API de Deepgram.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no existe: {file_path}")

    try:
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la DEEPGRAM_API_KEY en el archivo .env")

        deepgram = DeepgramClient(api_key)

        with open(file_path, 'rb') as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # --- ¡CONFIGURACIÓN CORREGIDA! ---
        # Usamos el modelo que Deepgram recomienda para español.
        options = PrerecordedOptions(
            model="nova-2-general", # Usando nova-2 que tiene un excelente soporte para español
            language="es",
            smart_format=True,
            punctuate=True,
            diarize=True,
            detect_topics=True,
            paragraphs=True
        )

        print("DEBUG: Enviando archivo a Deepgram para transcripción...")
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        print("DEBUG: Transcripción con Deepgram finalizada.")

        transcript = response.results.channels[0].alternatives[0].transcript
        
        if len(transcript) < 50:
             print(f"ADVERTENCIA: La transcripción generada es muy corta. Contenido: '{transcript}'")

        return transcript

    except Exception as e:
        raise RuntimeError(f"Error durante la transcripción con Deepgram: {e}")