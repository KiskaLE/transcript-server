# WhisperX Offline Server

Tento projekt poskytuje FastAPI server pro transkripci audia pomocí **WhisperX** s podporou diarizace (rozpoznání mluvčích). Je optimalizován pro běh na **CPU** a navržen pro běh v Dockeru.

## Vlastnosti
- **Transkripce:** Používá model OpenAI Whisper (`medium`).
- **Diarizace:** Rozpoznání mluvčích pomocí Pyannote.
- **CPU Optimalizace:** Využívá `int8` kvantizaci pro rychlejší běh bez GPU.
- **Offline Ready:** Modely se stáhnou během sestavování Docker obrazu.
- **Volba jazyka:** Možnost specifikovat jazyk nebo nechat automatickou detekci.

## Požadavky
1. **Hugging Face Token:** Budete potřebovat token z [huggingface.co](https://huggingface.co/settings/tokens).
2. **Přístup k modelům:** Na Hugging Face musíte odsouhlasit podmínky pro následující modely:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

## Instalace a spuštění

### 1. Příprava tokenu
Vložte svůj Hugging Face token do souboru `hf_token.txt`:
```bash
echo "vas_hf_token_zde" > hf_token.txt
```

### 2. Spuštění pomocí Docker Compose (doporučeno)
```bash
docker compose up --build
```

### 3. Alternativně: Ruční sestavení a spuštění
```bash
# Sestavení obrazu
docker build --secret id=HF_TOKEN,src=hf_token.txt -t whisper-offline .

# Spuštění kontejneru
docker run -p 8000:8000 -e HF_TOKEN=$(cat hf_token.txt) whisper-offline
```

## Použití API

Server běží na portu `8000`. Hlavní endpoint je `/transcribe`.

### Transkripce souboru (automatická detekce jazyka)
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@cesta/k/vasemu/audiu.wav"
```

### Transkripce se specifikovaným jazykem
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@audio.wav" \
  -F "language=cs"
```

Podporované jazyky: `cs` (čeština), `en` (angličtina), `de` (němčina), `sk` (slovenština), `pl` (polština), `fr`, `es`, `it`, `pt`, `ru`, `uk`, `ja`, `zh`, ...

### Formát odpovědi
```json
{
  "language": "cs",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Dobrý den, jak se máte?",
      "speaker": "SPEAKER_00"
    }
  ]
}
```

## Konfigurace
- **Model:** V `main.py` a `download_models.py` můžete změnit model na `tiny`, `base`, `small`, `medium`, `large-v2` nebo `large-v3`.
- **Zařízení:** Nastaveno na `cpu`. Pro GPU verzi by bylo nutné upravit Dockerfile a základní obraz.
