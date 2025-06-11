      
# 📝 Acta de Reunión Inteligente

Una aplicación de escritorio que transcribe grabaciones de reuniones (Teams, Zoom, etc.) y utiliza un modelo de lenguaje grande (LLM) a través de Ollama para generar automáticamente un acta de reunión formal, incluyendo resumen ejecutivo, decisiones, y tareas pendientes. El resultado se puede exportar a un PDF profesional.

---

## ✨ Características

- **Interfaz Gráfica Amigable:** Creada con Tkinter para una fácil interacción.
- **Transcripción Automática:** Utiliza `openai-whisper` para convertir audio/video (MP4, MP3, WAV) a texto.
- **Procesamiento con LLM Local:** Se integra con **Ollama**, permitiendo usar modelos locales (como Mistral, Llama, Gemma) para garantizar la privacidad de los datos.
- **Generación Estructurada de Actas:** Extrae automáticamente:
  - Resumen ejecutivo.
  - Temas discutidos y puntos clave.
  - Decisiones tomadas.
  - Tareas pendientes con responsables.
- **Exportación a PDF:** Genera un documento PDF formateado y profesional del acta.
- **Dockerizado:** Incluye un `Dockerfile` para una fácil implementación y ejecución en cualquier entorno compatible con Docker.

---

## 🚀 Cómo Empezar

Tienes dos maneras de ejecutar esta aplicación: **usando Docker (recomendado)** o **localmente con un entorno virtual**.

### Requisitos Previos

1. **Ollama Instalado y Corriendo:** Asegúrate de que [Ollama](https://ollama.com/) esté instalado y que tengas al menos un modelo descargado.
   ```bash
   ollama run mistral

    

IGNORE_WHEN_COPYING_START
Use code with caution. Markdown
IGNORE_WHEN_COPYING_END

    Git: Necesitas Git para clonar el repositorio.

    Docker (Opcional, para el método recomendado): Necesitas Docker instalado.

    FFmpeg (Para el método local): whisper lo requiere.

          
    # En Debian/Ubuntu
    sudo apt update && sudo apt install ffmpeg
    # En macOS (con Homebrew)
    brew install ffmpeg

        

    IGNORE_WHEN_COPYING_START

    Use code with caution. Bash
    IGNORE_WHEN_COPYING_END

🐳 Método 1: Ejecutar con Docker (Recomendado)

Este método simplifica todas las dependencias de Python y FFmpeg.
    bash
    docker pull dannypat88/meeting-analyzer:latest  
    git clone https://github.com/Dannypatt/meeting-analyzer.git
    cd meeting-analyzer/root_dir

        

    IGNORE_WHEN_COPYING_START

Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Configura Ollama para aceptar conexiones externas:
Por defecto, Ollama solo escucha en localhost. Para que Docker pueda conectarse, necesitas que escuche en 0.0.0.0.

      
# Detén el servicio de Ollama (si está corriendo en segundo plano)
sudo systemctl stop ollama
# Inicia Ollama manualmente para que acepte conexiones externas
OLLAMA_HOST=0.0.0.0 ollama serve

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Deja esta terminal abierta mientras usas la aplicación.

Construye la imagen de Docker:

      
docker build -t meeting-analyzer-app .

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Crea las carpetas locales para los archivos:
En la misma carpeta root_dir, crea directorios para tus audios y para guardar los PDFs.

      
mkdir audios pdfs

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Ejecuta el contenedor:
Este comando comparte tu pantalla y las carpetas recién creadas para que la GUI funcione y puedas acceder a tus archivos.

      
# Para Linux
xhost +SI:localuser:$(whoami)
docker run -it --rm \
  --name meeting-app \
  -e DISPLAY=$DISPLAY \
  -e OLLAMA_HOST=http://172.17.0.1:11434 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ${PWD}/audios:/home/appuser/app/audios \
  -v ${PWD}/pdfs:/home/appuser/app/pdfs \
  dannypat88/meeting-analyzer:latest
    

IGNORE_WHEN_COPYING_START

    Use code with caution. Bash
    IGNORE_WHEN_COPYING_END

        Nota: 172.17.0.1 es la IP por defecto del host de Docker en Linux. Si no funciona, obtén la tuya con ip addr show docker0.

        Ahora, cuando la aplicación se abra, puedes seleccionar archivos de tu carpeta audios y guardar los PDFs en tu carpeta pdfs.

# 📝 Acta de Reunión Inteligente

[![Docker Hub](https://img.shields.io/docker/pulls/dannypat88/meeting-analyzer?style=for-the-badge&logo=docker)](https://hub.docker.com/r/dannypat88/meeting-analyzer)

🐍 Método 2: Ejecutar Localmente (con Entorno Virtual)

    Clona el repositorio:

          
    git clone https://github.com/Dannypatt/meeting-analyzer.git
    cd meeting-analyzer

        

    IGNORE_WHEN_COPYING_START

Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Crea y activa un entorno virtual:

      
python3 -m venv venv
source venv/bin/activate

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Instala las dependencias:

      
cd root_dir
pip install -r requirements.txt

    

IGNORE_WHEN_COPYING_START
Use code with caution. Bash
IGNORE_WHEN_COPYING_END

Ejecuta la aplicación:

      
python3 main.py

    

IGNORE_WHEN_COPYING_START

    Use code with caution. Bash
    IGNORE_WHEN_COPYING_END

🛠️ Stack Tecnológico

    Lenguaje: Python 3.12

    GUI: Tkinter

    Transcripción: OpenAI Whisper

    Procesamiento de Lenguaje: Ollama

    Generación de PDF: PyFPDF

    Contenerización: Docker

🤝 Contribuciones

Las contribuciones son bienvenidas. Si tienes ideas para mejorar la aplicación o encuentras un error, por favor abre un issue para discutirlo. También puedes crear un pull request con tus mejoras.
📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
