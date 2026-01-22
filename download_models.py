import whisperx
import torch
import os

# Nastavení tokenu z prostředí (předá Docker)
hf_token = os.getenv("HF_TOKEN")
device = "cpu"

print("Stahuji modely Whisper a Pyannote...")

# 1. Stažení Whisper modelu (medium - dobrý kompromis mezi přesností a rychlostí)
model = whisperx.load_model("medium", device, compute_type="int8")

# 2. Stažení modelů pro diarizaci (vyžaduje token)
from whisperx.diarize import DiarizationPipeline
diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=device)

print("Hotovo. Modely jsou uloženy v cache.")
