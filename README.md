# Whisper Turbo Server (Microservice)

Modernizovaný, CPU-optimalizovaný server pro transkripci a diarizaci audia. Využívá architekturu mikro-služeb pro maximální stabilitu a rychlost.

## Architektura

Systém se skládá ze dvou Docker kontejnerů:
1.  **Gateway (`whisper-server`, port 8000):** Lehký HTTP server (FastAPI), který přijímá požadavky, čistí vstupy a posílá je do AI enginu.
2.  **AI Engine (`funasr-server`, interní port 8001):** Výkonný backend běžící na **Faster-Whisper** (transkripce) a **Pyannote 3.1** (diarizace).

## Klíčové Vlastnosti
- **Faster-Whisper Turbo:** Využívá C++ optimalizovaný model `large-v3-turbo` (nebo `medium`), který je až 4x rychlejší než běžný Whisper na CPU.
- **Pyannote 3.1:** State-of-the-art model pro rozlišení mluvčích.
- **Auto-Sanitization:** Automaticky opravuje a konvertuje jakýkoliv vstupní formát (M4A, MP3, OGG...) do čistého 16kHz WAV pomocí FFmpeg.
- **CPU Ready:** Optimalizováno pro běh bez GPU (int8 kvantizace).

## Požadavky
1.  **Hugging Face Token:** Nutný pro stahování modelu Pyannote 3.1 (akceptujte licenci na [huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)).
    *   Token musí být uložen v souboru `hf_token.txt` v kořenovém adresáři.

## Instalace a Spuštění

1.  **Vytvořte token soubor**
    ```bash
    echo "hf_vase_tajne_tokeny" > hf_token.txt
    ```

2.  **Spusťte pomocí Docker Compose**
    ```bash
    docker compose up --build -d
    ```
    *První spuštění může trvat několik minut (stahování ~3GB modelů).*

## Dokumentace API (Swagger UI)

Interaktivní dokumentace je dostupná přímo v prohlížeči:
*   [http://localhost:8000/docs](http://localhost:8000/docs)

Zde můžete API testovat klikáním ("Try it out"), nahrávat soubory a nastavovat parametry `min_speakers` / `max_speakers`.

## Použití API (cURL)

Endpoint: `POST http://localhost:8000/transcribe`

### Příklad (cURL) - Základní
```bash
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@nahravka.m4a"
```

### Příklad (cURL) - S počtem mluvčích (Doporučeno pro lepší přesnost)
Pokud víte, kolik lidí v nahrávce mluví, zadejte to. Zlepší to přesnost diarizace.
```bash
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@nahravka.m4a" \
     -F "min_speakers=2" \
     -F "max_speakers=2"
```

### Formát Odpovědi
```json
[
  {
    "start": 0.5,
    "end": 2.1,
    "text": "Dobrý den, vítám vás u našeho podcastu.",
    "speaker": "SPEAKER_00"
  },
  {
    "start": 2.5,
    "end": 5.0,
    "text": "Děkuji za pozvání.",
    "speaker": "SPEAKER_01"
  }
]
```

## Řešení Problémů / Troubleshooting

*   **Chyba `CRITICAL ERROR loading models`:** Zkontrolujte, zda máte platný token v `hf_token.txt` a zda jste odsouhlasili podmínky na HuggingFace.
*   **Chyba `<|nospeech|>`:** Server to nyní řeší automaticky konverzí. Pokud problém přetrvává, zkuste nahrát hlasitější soubor.

## Změna Modelu
Pro změnu modelu (např. na `large-v3`) upravte `ASR_MODEL_NAME` v souboru `funasr-server/main.py`.
