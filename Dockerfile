# ---- Etapa 1: Builder ----
FROM python:3.12-slim-bookworm as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Esta línea es la que instala todo lo de requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# ---- Etapa 2: Final ----
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tk \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

WORKDIR /home/appuser/app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . .

CMD ["python3", "main.py"]