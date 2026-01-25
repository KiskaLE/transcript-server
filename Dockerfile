# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install lightweight API dependencies using uv
# httpx: For calling the FunASR microservice
# fastapi/uvicorn: For the main API
RUN uv pip install --system --no-cache \
    fastapi \
    uvicorn \
    python-multipart \
    httpx \
    requests

COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
