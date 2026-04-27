# Qwen3-TTS Deployment Guide

This document defines the TTS milestone of the project: deploy a local `Qwen3-TTS` service, expose HTTP APIs for synthesis, and verify both preset-speaker generation and voice-clone experimentation on a GPU server.

## Goal
By the end of this guide you should be able to:
- create a clean Miniconda environment for Qwen3-TTS
- install the `qwen-tts` runtime dependencies
- download the `1.7B-CustomVoice` model for the API service
- start the FastAPI service and call its endpoints
- experiment with voice cloning separately using the `1.7B-Base` model

## Recommended Model Split
Use two model checkpoints for two different purposes:

- API service: `Qwen3-TTS-12Hz-1.7B-CustomVoice`
- voice clone experiments: `Qwen3-TTS-12Hz-1.7B-Base`

This is important:
- `CustomVoice` gives you a stable preset-speaker service with 9 supported speakers and optional instruction control.
- actual reference-audio voice cloning belongs to the `Base` model path, not the `CustomVoice` API currently in this repo.

## Step 1: Create the Conda Environment

```bash
conda create -n qwen3-tts python=3.12 -y
source /root/.bashrc
# If this is the first time `conda init` has been used in the shell:
# conda init bash
# source /root/.bashrc
conda activate qwen3-tts
```

## Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -U qwen-tts fastapi uvicorn requests soundfile
```

Optional but recommended if the environment supports it:

```bash
pip install -U flash-attn --no-build-isolation
```

If the machine has limited RAM during build:

```bash
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

## Step 3: Download the Models

### 3.1 Download the API Service Model

```bash
mkdir -p /root/autodl-tmp/models
pip install -U "huggingface_hub[cli]"
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice \
  --local-dir /root/autodl-tmp/models/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

If you prefer a mirror:

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice \
  --local-dir /root/autodl-tmp/models/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

### 3.2 Download the Voice Clone Test Model

```bash
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --local-dir /root/autodl-tmp/models/Qwen3-TTS-12Hz-1.7B-Base
```

## Step 4: Create the Runtime Config

```bash
cp qwen3tts.env.example qwen3tts.env
```

Update at least these fields:
- `QWEN3_TTS_MODEL_PATH`
- `PYTHON_BIN`
- `UVICORN_BIN`
- `QWEN3_TTS_API_KEYS`

Default recommended service model path:

```bash
QWEN3_TTS_MODEL_PATH=/root/autodl-tmp/models/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

## Step 5: Start the Service

```bash
chmod +x scripts/run-qwen3tts-api.sh
./scripts/run-qwen3tts-api.sh
```

Default endpoint:
- `http://0.0.0.0:8010`

## Step 6: Verify the Service

### Health Check

```bash
curl -sS http://127.0.0.1:8010/health
```

### List Supported Voices

```bash
curl -sS http://127.0.0.1:8010/v1/voices
```

### Generate WAV Audio

```bash
curl -X POST http://127.0.0.1:8010/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你好，这是 Qwen3-TTS 的本地部署测试。",
    "voice": "Vivian",
    "language": "zh",
    "instruction": "Use a calm and natural tone.",
    "format": "wav",
    "api_key": "tts-key-1"
  }' \
  --output out.wav
```

### Generate Streaming PCM Audio

```bash
curl -N -X POST http://127.0.0.1:8010/v1/audio/speech/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": "第一句。第二句。第三句。",
    "voice": "Vivian",
    "language": "zh",
    "format": "pcm16",
    "api_key": "tts-key-1"
  }' > out.pcm
```

### Local Streaming Playback Test

```bash
python qwen3tts/stream_play_test.py \
  --text "你好，这是一个流式播放测试。" \
  --voice Vivian \
  --api-key tts-key-1
```

## Preset Speakers
The current API in this repository is designed around the `CustomVoice` models and preset speakers returned by `/v1/voices`.
Typical speakers include:
- `Vivian`
- `Serena`
- `Uncle_Fu`
- `Dylan`
- `Eric`
- `Ryan`
- `Aiden`
- `Ono_Anna`
- `Sohee`

Use each speaker's native language first if you want the most stable quality.

## Voice Clone Note
The current FastAPI service in this repository does not yet expose an HTTP endpoint for uploading reference audio and cloning a new speaker on demand.

What you can do right now:
- run the API service with `1.7B-CustomVoice` for stable preset speakers
- separately test voice cloning with the `1.7B-Base` model using a local Python script

That means your TTS video can cover two tracks:
1. `CustomVoice` API deployment for practical application serving
2. `Base` model voice cloning experiment for advanced usage

## Voice Clone Test Example
See [examples/qwen3tts_voice_clone_test.py](../examples/qwen3tts_voice_clone_test.py).

It uses:
- `Qwen3-TTS-12Hz-1.7B-Base`
- a local reference audio file
- the transcript of that reference audio

## Known Pitfalls
- If `conda activate` does not work after `conda init`, run `source /root/.bashrc` in the current shell.
- If `uvicorn` is not found, verify `UVICORN_BIN` points to the active conda environment.
- If `qwen-tts` fails to load the model, confirm the model path and dependency versions first.
- If `flash-attn` is unavailable, leave `QWEN3_TTS_ATTN_IMPL` empty and test without it first.
- If the service returns 401, confirm the request `api_key` is included in `QWEN3_TTS_API_KEYS`.
- If you want real voice cloning from reference audio, do not expect the current `CustomVoice` API to do it; use the `Base` model path instead.

## What This Milestone Covers
- local HTTP service for TTS
- preset-speaker synthesis with the `1.7B-CustomVoice` model
- instruction-controlled synthesis
- WAV and PCM16 output
- voice clone experimentation path with the `1.7B-Base` model
