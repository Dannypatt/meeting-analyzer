# ---- Etapa 1: Builder ----
# Usa una imagen base de Python para instalar las dependencias
FROM python:3.12-slim-bookworm as builder

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias del sistema necesarias para compilar algunas librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requerimientos
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt


# ---- Etapa 2: Final ----
# Usa una imagen base limpia y ligera para la aplicación final
FROM python:3.12-slim-bookworm

# Instala las dependencias de TIEMPO DE EJECUCIÓN (no las de construcción)
# FFmpeg es crucial para Whisper, Tkinter para la GUI
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tk \
    && rm -rf /var/lib/apt/lists/*

# Crea un usuario no-root para la aplicación (mejor práctica de seguridad)
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Establece el directorio de trabajo para el usuario 'appuser'
WORKDIR /home/appuser/app

# Copia las librerías de Python instaladas desde la etapa 'builder'
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia el código de la aplicación y dale ownership al usuario 'appuser'
COPY --chown=appuser:appuser . .

# Comando por defecto para ejecutar la aplicación
CMD ["python3", "main.py"]