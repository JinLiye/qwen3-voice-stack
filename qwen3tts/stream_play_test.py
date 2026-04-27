#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

import pyaudio
import requests


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play chunked pcm16 stream from Qwen3-TTS API.")
    parser.add_argument("--url", default="http://127.0.0.1:8010/v1/audio/speech/stream")
    parser.add_argument("--api-key", default="tts-key-1")
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", default="aiden")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--chunk-size", type=int, default=4096)
    parser.add_argument("--connect-timeout", type=float, default=10.0)
    parser.add_argument("--read-timeout", type=float, default=300.0)
    parser.add_argument("--save-pcm", default=None, help="Optional path to save raw pcm_s16le stream.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    payload = {
        "input": args.text,
        "voice": args.voice,
        "language": args.language,
        "format": "pcm16",
        "api_key": args.api_key,
    }

    timeout = (args.connect_timeout, args.read_timeout)
    response = requests.post(args.url, json=payload, stream=True, timeout=timeout)
    if response.status_code != 200:
        print(f"HTTP {response.status_code}: {response.text}", file=sys.stderr)
        return 1

    sample_rate = int(response.headers.get("X-Audio-Sample-Rate", "24000"))
    channels = int(response.headers.get("X-Audio-Channels", "1"))
    fmt = response.headers.get("X-Audio-Format", "pcm_s16le")
    if fmt != "pcm_s16le":
        print(f"Unexpected audio format: {fmt}", file=sys.stderr)
        return 1

    print(
        f"Streaming audio: sample_rate={sample_rate}, channels={channels}, format={fmt}",
        file=sys.stderr,
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        output=True,
    )

    pcm_file: Optional[object] = open(args.save_pcm, "wb") if args.save_pcm else None
    pending = b""

    try:
        for chunk in response.iter_content(chunk_size=args.chunk_size):
            if not chunk:
                continue

            data = pending + chunk
            even_len = len(data) - (len(data) % 2)
            playable = data[:even_len]
            pending = data[even_len:]

            if playable:
                stream.write(playable)
                if pcm_file:
                    pcm_file.write(playable)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
    finally:
        if pending:
            print(f"Dropping 1 trailing byte (incomplete sample): {pending!r}", file=sys.stderr)
        if pcm_file:
            pcm_file.close()
        stream.stop_stream()
        stream.close()
        pa.terminate()
        response.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
