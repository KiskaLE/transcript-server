# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Instalace systémových nástrojů
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Instalace PyTorch pro CPU
RUN pip3 install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# 2. Instalace pyannote.audio (bez závislostí, aby nepřepsala torch)
RUN pip3 install --no-cache-dir --no-deps pyannote.audio

# 3. Instalace WhisperX a zbylých závislostí
RUN pip3 install --no-cache-dir \
    git+https://github.com/m-bain/whisperX.git \
    fastapi uvicorn python-multipart \
    pyannote.core pyannote.database pyannote.pipeline \
    asteroid-filterbanks speechbrain

# 4. Reinstalace CPU torch (kdyby něco přepsalo)
RUN pip3 install --no-cache-dir --force-reinstall \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# 5. Oprava závislostí (typing_extensions pro pydantic)
RUN pip3 install --no-cache-dir --upgrade typing_extensions pydantic

# Příprava skriptu a stažení modelů
COPY download_models.py .

# Bezpečné použití tokenu během buildu
RUN --mount=type=secret,id=HF_TOKEN \
    HF_TOKEN=$(cat /run/secrets/HF_TOKEN) python3 download_models.py

COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
