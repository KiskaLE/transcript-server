# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install system dependencies (ffmpeg is needed for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies using uv
# Downgrade to rock-solid stable suite for CPU
RUN uv pip install --system --no-cache \
    torch==2.1.2 \
    torchvision==0.16.2 \
    torchaudio==2.1.2 \
    --index-url https://download.pytorch.org/whl/cpu

# Install AI stack
RUN uv pip install --system --no-cache \
    faster-whisper \
    pyannote.audio==3.1.1 \
    "huggingface_hub<0.23" \
    "numpy<2" \
    fastapi \
    uvicorn \
    python-multipart

# Copy application code
COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "3600"]
