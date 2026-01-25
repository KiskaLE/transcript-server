import os
import httpx
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form

app = FastAPI()

FUNASR_URL = os.getenv("FUNASR_URL", "http://funasr:8000")

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    min_speakers: Optional[int] = Form(None),
    max_speakers: Optional[int] = Form(None)
):
    """
    Proxy endpoint: Forwards audio to the FunASR microservice for ASR + Diarization.
    Supports optional min/max speakers to guide diarization.
    """
    
    # Read file content safely
    file_content = await file.read()
    filename = file.filename
    
    # 1 hour timeout for long files
    timeout = httpx.Timeout(3600.0, connect=60.0) 
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # We simply stream the file to the microservice
            # Ensure we send a content type that hints it is audio
            content_type = file.content_type
            if not content_type or content_type == 'application/octet-stream':
                content_type = 'audio/wav' # Default fallback
            
            files = {'file': (filename, file_content, content_type)}
            
            # Prepare optional data
            data = {}
            if min_speakers is not None: data['min_speakers'] = min_speakers
            if max_speakers is not None: data['max_speakers'] = max_speakers

            response = await client.post(f"{FUNASR_URL}/diarize", files=files, data=data)
            
            if response.status_code != 200:
                 raise HTTPException(status_code=response.status_code, detail=f"FunASR Error: {response.text}")
            
            return response.json()
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Failed to connect to FunASR service: {exc}")