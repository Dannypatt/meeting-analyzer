# 📝 Acta de Reunión Inteligente v2.0

Una aplicación de escritorio que utiliza un flujo de trabajo en dos etapas para una máxima precisión:
1.  **Transcripción:** Convierte grabaciones de reuniones (MP4, MP3, etc.) a texto usando la API de alta precisión de **Deepgram (Nova-3)**.
2.  **Generación de Acta:** Utiliza un modelo de lenguaje grande (LLM) a través de **Ollama, OpenAI, Claude o Gemini** para generar un acta de reunión formal en formato **Markdown** a partir del texto transcrito.

El usuario tiene control total, pudiendo editar la transcripción antes de generar el acta, y editar el acta final antes de exportarla a un PDF profesional.

![Screenshot de la Aplicación](https://github.com/Dannypatt/meeting-analyzer/blob/main/screenshot.png?raw=true) <!-- ¡Toma un screenshot de tu app final y súbelo a GitHub! -->

---

## ✨ Características Principales

- **Flujo de Trabajo en Dos Etapas:** Transcribe primero, luego genera el acta. Esto permite al usuario corregir errores de transcripción (nombres, jerga técnica) para un resultado final perfecto.
- **Transcripción de Alta Precisión:** Utiliza **Deepgram Nova-3**, uno de los modelos más avanzados, con diarización para identificar hablantes.
- **Soporte Multi-LLM:** Se integra con:
  - **Ollama:** Para usar modelos locales y garantizar la privacidad.
  - **OpenAI (ChatGPT):** `gpt-4o` y otros.
  - **Anthropic:** Familia de modelos `Claude 3.5`.
  - **Google:** Familia de modelos `Gemini`.
- **Generación Basada en Markdown:** El LLM genera un acta en formato Markdown, un método mucho más robusto y natural que forzar una estructura JSON.
- **Exportación a PDF:** Convierte el acta final en Markdown a un documento PDF formateado, preservando encabezados, listas y negritas.
- **Contenerización con Docker:** Incluye un `Dockerfile` optimizado para una fácil implementación en cualquier sistema compatible.

---

## 🚀 Cómo Empezar

### Requisitos Previos

1.  **Cuentas de API (Obligatorio):**
    -   **Deepgram:** Necesitas una API Key para la transcripción. Ofrecen un crédito inicial gratuito.
    -   **Opcional:** API Keys para OpenAI, Anthropic o Google si deseas usar sus modelos.
2.  **Ollama Instalado (Si usas modelos locales):** [Ollama](https://ollama.com/) debe estar instalado y con al menos un modelo descargado (`ollama run mistral`).
3.  **Git:** Para clonar el repositorio.
4.  **Docker:** [Docker](https://www.docker.com/products/docker-desktop/) es el método de ejecución recomendado.

---

### 🐳 Ejecutar con Docker (Recomendado)

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/Dannypatt/meeting-analyzer.git
    cd meeting-analyzer/root_dir
    ```

2.  **Crea el archivo de secretos (`.env`):**
    En la carpeta `root_dir`, crea un archivo llamado `.env` y añade tus claves API.
    ```env
    # Clave para Deepgram (Obligatoria)
    DEEPGRAM_API_KEY="tu_api_key_de_deepgram"

    # Claves para los LLMs de nube (Opcionales)
    OPENAI_API_KEY="sk-..."
    ANTHROPIC_API_KEY="sk-ant-..."
    GOOGLE_API_KEY="AIzaSy..."
    ```

3.  **Configura Ollama para aceptar conexiones externas (si lo usas):**
    ```bash
    # Detén el servicio de Ollama (si está corriendo en segundo plano)
    sudo systemctl stop ollama
    # Inicia Ollama manualmente para que acepte conexiones externas
    OLLAMA_HOST=0.0.0.0 ollama serve
    ```
    **Deja esta terminal abierta mientras usas la aplicación.**

4.  **Construye la imagen de Docker:**
    ```bash
    docker build -t dannypat88/meeting-analyzer:latest .
    ```

5.  **Ejecuta el contenedor:**
    Este comando comparte tu pantalla y directorios para que la GUI funcione.

    ```bash
    # Para Linux (asegúrate de haber ejecutado 'xhost +SI:localuser:$(whoami)' una vez)
    docker run -it --rm \
      --name meeting-app \
      --net=host \
      -e DISPLAY=$DISPLAY \
      --env-file ./.env \
      -v ${PWD}/audios:/home/appuser/app/audios \
      -v ${PWD}/pdfs:/home/appuser/app/pdfs \
      dannypat88/meeting-analyzer:latest
    ```
    *   **Nota:** Crea las carpetas `audios` y `pdfs` dentro de `root_dir` para tus archivos.

---

## 🛠️ Stack Tecnológico

-   **Lenguaje:** Python 3.12
-   **GUI:** Tkinter
-   **Transcripción:** **Deepgram (Nova-3)**
-   **Procesamiento de Lenguaje:** Ollama, OpenAI API, Anthropic API, Google AI API
-   **Generación de PDF:** PyFPDF con soporte Markdown
-   **Contenerización:** Docker

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.