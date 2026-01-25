import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import Optional
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
import torch
import tempfile
import shutil
import subprocess
import numpy as np

app = FastAPI()

# Global variables
asr_model = None
diarization_pipeline = None

# Config
# Use standard large-v3-turbo. Automatically filtered by faster-whisper.
ASR_MODEL_SIZE = "deepdml/faster-whisper-large-v3-turbo-ct2" 
ASR_MODEL_NAME = "medium"

HF_TOKEN = os.getenv("HF_TOKEN")
# Fallback to Docker Secret
if not HF_TOKEN and os.path.exists("/run/secrets/HF_TOKEN"):
    with open("/run/secrets/HF_TOKEN", "r") as f:
        HF_TOKEN = f.read().strip()

print("Loading models...")

try:
    # 1. Load Faster Whisper (CPU int8)
    # compute_type="int8" is crucial for CPU speed
    asr_model = WhisperModel(ASR_MODEL_NAME, device="cpu", compute_type="int8")
    print(f"Faster-Whisper ({ASR_MODEL_NAME}) loaded.")

    # 2. Load Pyannote Diarization
    if HF_TOKEN:
        print(f"Loading Pyannote with token: {HF_TOKEN[:4]}... (redacted)")
        diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=HF_TOKEN
        )
        if diarization_pipeline:
            diarization_pipeline.to(torch.device("cpu"))
            print("Pyannote 3.1 loaded.")
        else:
            print("Failed to load Pyannote pipeline (check token permissions).")
    else:
        print("HF_TOKEN not found. Diarization will be disabled.")

except Exception as e:
    print(f"CRITICAL ERROR loading models: {e}")

def align_transcription(segments, diarization):
    """
    Align whisper segments with pyannote diarization segments.
    Simple 'dominant speaker' approach.
    """
    aligned_segments = []
    
    # Convert pyannote annotation to list of (start, end, label)
    # diarization is an Annotation object
    diar_segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        diar_segments.append((turn.start, turn.end, speaker))
        
    for seg in segments:
        # Segment: start, end, text
        seg_start = seg.start
        seg_end = seg.end
        
        # Find overlapping diarization segments
        speakers_overlap = {}
        for (d_start, d_end, speaker) in diar_segments:
            # Calculate overlap
            overlap_start = max(seg_start, d_start)
            overlap_end = min(seg_end, d_end)
            overlap_duration = max(0, overlap_end - overlap_start)
            
            if overlap_duration > 0:
                speakers_overlap[speaker] = speakers_overlap.get(speaker, 0) + overlap_duration
        
        # Choose dominance
        if speakers_overlap:
            best_speaker = max(speakers_overlap, key=speakers_overlap.get)
        else:
            best_speaker = "UNKNOWN"
            
        aligned_segments.append({
            "start": seg_start,
            "end": seg_end,
            "text": seg.text.strip(),
            "speaker": best_speaker
        })
        
    return aligned_segments

@app.post("/diarize")
async def diarize_audio(
    file: UploadFile = File(...),
    min_speakers: Optional[int] = Form(None),
    max_speakers: Optional[int] = Form(None)
):
    if asr_model is None:
         raise HTTPException(status_code=500, detail="ASR Model not initialized")

    # 1. Save and Clean Audio (FFmpeg)
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    wav_path = tmp_path + ".converted.wav"
    
    try:
        # Conversion
        subprocess.run([
            "ffmpeg", "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", wav_path
        ], check=True, stderr=subprocess.PIPE)
        
        if not os.path.exists(wav_path):
             raise Exception("Conversion failed")

        print(f"Processing {wav_path}...")

        # 2. Transcribe (Whisper)
        # segments is a generator
        segments_gen, info = asr_model.transcribe(wav_path, beam_size=5, vad_filter=True)
        # consume generator
        segments = list(segments_gen)
        print(f"Transcribed {len(segments)} segments.")

        # 3. Diarize (Pyannote)
        if diarization_pipeline:
            # Prepare kwargs, filter out None
            diar_kwargs = {}
            if min_speakers is not None: diar_kwargs["min_speakers"] = min_speakers
            if max_speakers is not None: diar_kwargs["max_speakers"] = max_speakers
            
            print(f"Running diarization with options: {diar_kwargs}")
            diarization = diarization_pipeline(wav_path, **diar_kwargs)
            
            # 4. Align
            final_result = align_transcription(segments, diarization)
        else:
            # Fallback (no speakers)
            final_result = [{"start": s.start, "end": s.end, "text": s.text, "speaker": "N/A"} for s in segments]
            
        return final_result

    except Exception as e:
        print(f"Error processing: {e}")
        # Capture ffmpeg stderr if possible, but e is usually just Exception
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        if os.path.exists(wav_path): os.remove(wav_path)

@app.get("/health")
def health():
    return {"status": "ok", "asr": asr_model is not None, "diar": diarization_pipeline is not None}
