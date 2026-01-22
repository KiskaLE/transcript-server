# WhisperX Offline Server

Tento projekt poskytuje FastAPI server pro transkripci audia pomocí **WhisperX** s podporou diarizace (rozpoznání mluvčích). Je optimalizován pro běh na **CPU** a navržen pro běh v Dockeru.

## Vlastnosti
- **Transkripce:** Používá model OpenAI Whisper (výchozí `base`).
- **Diarizace:** Rozpoznání mluvčích pomocí Pyannote.
- **CPU Optimalizace:** Využívá `int8` kvantizaci pro rychlejší běh bez GPU.
- **Offline Ready:** Modely se stáhnou během sestavování Docker obrazu.

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

### 2. Sestavení Docker obrazu
Pro stažení a "zapečení" modelů do obrazu použijte následující příkaz:
```bash
docker build --secret id=HF_TOKEN,src=hf_token.txt -t whisper-server .
```

### 3. Spuštění kontejneru
```bash
docker run -p 8000:8000 whisper-server
```

## Použití API

Server běží na portu `8000`. Hlavní endpoint je `/transcribe`.

### Transkripce souboru (cURL)
```bash
curl -X POST http://localhost:8000/transcribe \
  -H "Content-Type: multipart/form-data" \
  -F "file=@cesta/k/vasemu/audiu.wav"
```

### Formát odpovědi
Server vrátí JSON se segmenty textu a identifikací mluvčích:
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Dobrý den, jak se máte?",
      "speaker": "SPEAKER_00"
    },
    ...
  ]
}
```

## Konfigurace
- **Model:** V `main.py` a `download_models.py` můžete změnit model `base` na `tiny` (rychlejší) nebo `small` (přesnější).
- **Zařízení:** Nastaveno na `cpu`. Pro GPU verzi by bylo nutné upravit Dockerfile a základní obraz.
