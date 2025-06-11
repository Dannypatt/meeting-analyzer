import whisper
import os

def transcribe_audio(file_path):
    """
    Transcribe un archivo de audio/video a texto usando Whisper.
    Requiere que FFmpeg esté instalado y en el PATH del sistema.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no existe: {file_path}")

    try:
        # Cargar el modelo Whisper. Puedes elegir 'tiny', 'base', 'small', 'medium', 'large'
        # 'base' es un buen equilibrio entre velocidad y precisión para empezar.
        # Puedes especificar 'model = whisper.load_model("base", device="cuda")' si tienes GPU NVIDIA
        model = whisper.load_model("large", device="cpu") 
        
        # Realizar la transcripción
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        # Aquí se podrían añadir más detalles de error, como si FFmpeg no está
        # Se puede añadir una comprobación de ffmpeg antes de cargar el modelo.
        raise RuntimeError(f"Error durante la transcripción con Whisper: {e}\n"
                           "Asegúrese de que FFmpeg esté instalado y en su PATH.")

if __name__ == '__main__':
    # Ejemplo de uso (esto no se ejecutará en la app principal)
    # Crea un archivo de audio de prueba o usa uno existente para testear
    # from moviepy.editor import VideoFileClip
    # video = VideoFileClip("mi_reunion.mp4")
    # video.audio.write_audiofile("mi_reunion.wav")
    
    # print("Transcribiendo archivo de prueba.wav...")
    # try:
    #     transcribed_text = transcribe_audio("mi_reunion.wav")
    #     print("\n--- Transcripción ---")
    #     print(transcribed_text[:500] + "...") # Mostrar los primeros 500 caracteres
    # except Exception as e:
    #     print(f"Error al transcribir: {e}")
    pass