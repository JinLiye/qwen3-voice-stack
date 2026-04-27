#!/usr/bin/env python3
from __future__ import annotations

import base64
import io
import os
import re
import time
from typing import Generator, List, Literal, Optional

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from qwen_tts import Qwen3TTSModel


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    if not value:
        return default
    return value


MODEL_PATH = _env(
    "QWEN3_TTS_MODEL_PATH",
    "/root/autodl-tmp/models/Qwen3-TTS-12Hz-1.7B-CustomVoice",
)
DEVICE = _env("QWEN3_TTS_DEVICE", "cuda:0")
DTYPE_STR = _env("QWEN3_TTS_DTYPE", "bfloat16").lower()
DEFAULT_SPEAKER = _env("QWEN3_TTS_DEFAULT_SPEAKER", "Vivian")
DEFAULT_LANGUAGE = _env("QWEN3_TTS_DEFAULT_LANGUAGE", "zh")
ATTN_IMPL = _env("QWEN3_TTS_ATTN_IMPL", "")
API_KEYS = {
    k.strip()
    for k in _env(
        "QWEN3_TTS_API_KEYS",
        "tts-key-1,tts-key-2,tts-key-3,tts-key-4,tts-key-5",
    ).split(",")
    if k.strip()
}

_DTYPE_MAP = {
    "float16": torch.float16,
    "fp16": torch.float16,
    "bfloat16": torch.bfloat16,
    "bf16": torch.bfloat16,
    "float32": torch.float32,
    "fp32": torch.float32,
}
TORCH_DTYPE = _DTYPE_MAP.get(DTYPE_STR, torch.bfloat16)

app = FastAPI(title="Qwen3-TTS API", version="1.0.0")
model: Optional[Qwen3TTSModel] = None
supported_speakers: List[str] = []


class TTSRequest(BaseModel):
    model: str = Field(default="qwen3-tts")
    input: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field(default=None, description="Speaker name")
    language: str = Field(default=DEFAULT_LANGUAGE)
    instruction: Optional[str] = Field(default=None)
    format: Literal["wav", "pcm16"] = Field(default="wav")
    stream: bool = Field(default=False)
    api_key: Optional[str] = Field(default=None)
    max_new_tokens: Optional[int] = Field(default=None)


def _split_sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[銆傦紒锛?!?锛?,锛宂)\s*", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def _to_pcm16(audio: np.ndarray) -> bytes:
    if audio.ndim != 1:
        audio = np.squeeze(audio)
    audio = np.clip(audio, -1.0, 1.0)
    audio_i16 = (audio * 32767.0).astype(np.int16)
    return audio_i16.tobytes()


def _to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    import wave

    pcm = _to_pcm16(audio)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()


def _check_key(req: TTSRequest) -> None:
    if not API_KEYS:
        return
    if not req.api_key or req.api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid api_key")


def _normalize_language(language: Optional[str]) -> Optional[str]:
    if language is None:
        return None
    lang = language.strip()
    if not lang:
        return None
    if lang.lower() == "auto":
        return "Auto"
    return lang


@app.on_event("startup")
def _startup() -> None:
    global model, supported_speakers
    kwargs = {
        "device_map": DEVICE,
        "dtype": TORCH_DTYPE,
    }
    if ATTN_IMPL:
        kwargs["attn_implementation"] = ATTN_IMPL
    model = Qwen3TTSModel.from_pretrained(MODEL_PATH, **kwargs)
    speakers = model.get_supported_speakers() or []
    supported_speakers = sorted(speakers)


@app.get("/health")
def health() -> dict:
    return {
        "ok": model is not None,
        "model_path": MODEL_PATH,
        "device": DEVICE,
        "dtype": str(TORCH_DTYPE),
    }


@app.get("/v1/voices")
def voices() -> dict:
    return {"voices": supported_speakers}


@app.post("/v1/audio/speech")
def speech(req: TTSRequest) -> Response:
    if req.stream:
        raise HTTPException(status_code=400, detail="Use /v1/audio/speech/stream when stream=true")
    _check_key(req)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")

    t0 = time.perf_counter()
    speaker = req.voice or DEFAULT_SPEAKER
    language = _normalize_language(req.language)
    max_new_tokens = req.max_new_tokens
    gen_kwargs = {}
    if max_new_tokens is not None:
        gen_kwargs["max_new_tokens"] = max_new_tokens
    audios, sample_rate = model.generate_custom_voice(
        text=req.input,
        speaker=speaker,
        language=language,
        instruct=req.instruction,
        non_streaming_mode=True,
        **gen_kwargs,
    )
    audio = audios[0]
    latency_ms = int((time.perf_counter() - t0) * 1000)
    header_max_new_tokens = "model_default" if max_new_tokens is None else str(max_new_tokens)
    headers = {"X-TTS-Latency-Ms": str(latency_ms), "X-TTS-Max-New-Tokens": header_max_new_tokens}
    if req.format == "pcm16":
        return Response(
            content=_to_pcm16(audio),
            media_type=f"audio/L16;rate={sample_rate};channels=1",
            headers=headers,
        )
    wav = _to_wav_bytes(audio, sample_rate)
    return Response(content=wav, media_type="audio/wav", headers=headers)


def _stream_pcm_by_sentence(req: TTSRequest) -> Generator[bytes, None, None]:
    assert model is not None
    speaker = req.voice or DEFAULT_SPEAKER
    language = _normalize_language(req.language)
    max_new_tokens = req.max_new_tokens
    gen_kwargs = {}
    if max_new_tokens is not None:
        gen_kwargs["max_new_tokens"] = max_new_tokens
    chunks = _split_sentences(req.input)
    if not chunks:
        return
    for sentence in chunks:
        audios, _sample_rate = model.generate_custom_voice(
            text=sentence,
            speaker=speaker,
            language=language,
            instruct=req.instruction,
            non_streaming_mode=True,
            **gen_kwargs,
        )
        yield _to_pcm16(audios[0])


@app.post("/v1/audio/speech/stream")
def speech_stream(req: TTSRequest) -> StreamingResponse:
    _check_key(req)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    if req.format != "pcm16":
        raise HTTPException(status_code=400, detail="stream endpoint currently only supports format=pcm16")

    # Chunked raw PCM stream (16-bit LE, mono). Client should play as PCM with known sample rate.
    # To reduce client complexity, sample rate is exposed in header.
    language = _normalize_language(req.language)
    max_new_tokens = req.max_new_tokens
    gen_kwargs = {}
    if max_new_tokens is not None:
        gen_kwargs["max_new_tokens"] = max_new_tokens
    _, sample_rate = model.generate_custom_voice(
        text="娴嬭瘯",
        speaker=req.voice or DEFAULT_SPEAKER,
        language=language,
        instruct=req.instruction,
        non_streaming_mode=True,
        **gen_kwargs,
    )
    headers = {
        "X-Audio-Format": "pcm_s16le",
        "X-Audio-Sample-Rate": str(sample_rate),
        "X-Audio-Channels": "1",
    }
    return StreamingResponse(
        _stream_pcm_by_sentence(req),
        media_type="application/octet-stream",
        headers=headers,
    )


@app.post("/v1/audio/speech/sse")
def speech_sse(req: TTSRequest) -> StreamingResponse:
    _check_key(req)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")

    speaker = req.voice or DEFAULT_SPEAKER
    language = _normalize_language(req.language)
    max_new_tokens = req.max_new_tokens
    gen_kwargs = {}
    if max_new_tokens is not None:
        gen_kwargs["max_new_tokens"] = max_new_tokens
    chunks = _split_sentences(req.input)
    if not chunks:
        return JSONResponse({"error": "input is empty"}, status_code=400)

    def _event_gen() -> Generator[str, None, None]:
        for sentence in chunks:
            audios, sample_rate = model.generate_custom_voice(
                text=sentence,
                speaker=speaker,
                language=language,
                instruct=req.instruction,
                non_streaming_mode=True,
                **gen_kwargs,
            )
            wav_b64 = base64.b64encode(_to_wav_bytes(audios[0], sample_rate)).decode("ascii")
            yield f"data: {wav_b64}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_event_gen(), media_type="text/event-stream")
