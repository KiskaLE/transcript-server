import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
import whisperx
from whisperx.diarize import DiarizationPipeline
import torch

app = FastAPI()

# Nastavení pro CPU
HF_TOKEN = os.getenv("HF_TOKEN")
DEVICE = "cpu"
# "int8" je pro CPU nejrychlejší volba
COMPUTE_TYPE = "int8" 

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transkripce audio souboru.
    
    Args:
        file: Audio soubor (wav, mp3, m4a, ...)
        language: Volitelný kód jazyka (cs, en, de, sk, ...). 
                  Pokud není zadán, jazyk bude automaticky detekován.
    """
    # Uložení nahraného souboru
    audio_path = "temp_audio.wav"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # 1. Transkripce (Whisper) - medium je dobrý kompromis
    model = whisperx.load_model("medium", DEVICE, compute_type=COMPUTE_TYPE, language=language)
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=4, language=language)

    # 2. Diarizace (Pyannote)
    diarize_model = DiarizationPipeline(use_auth_token=HF_TOKEN, device=DEVICE)
    diarize_segments = diarize_model(audio)
    
    # 3. Přiřazení mluvčích k textu
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return {
        "language": result.get("language", language),
        "segments": result["segments"]
    }