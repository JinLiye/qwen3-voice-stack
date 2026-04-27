#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/qwen3tts.env"
APP_MODULE="qwen3tts.tts_api:app"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing env file: ${ENV_FILE}" >&2
  echo "Copy qwen3tts.env.example to qwen3tts.env and update it first." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

PYTHON_BIN="${PYTHON_BIN:-${SCRIPT_DIR}/.venv-qwen3tts/bin/python}"
UVICORN_BIN="${UVICORN_BIN:-${SCRIPT_DIR}/.venv-qwen3tts/bin/uvicorn}"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python binary not found or not executable: ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ ! -x "${UVICORN_BIN}" ]]; then
  echo "uvicorn binary not found or not executable: ${UVICORN_BIN}" >&2
  exit 1
fi

export QWEN3_TTS_MODEL_PATH="${QWEN3_TTS_MODEL_PATH}"
export QWEN3_TTS_DEVICE="${QWEN3_TTS_DEVICE:-cuda:0}"
export QWEN3_TTS_DTYPE="${QWEN3_TTS_DTYPE:-bfloat16}"
export QWEN3_TTS_DEFAULT_SPEAKER="${QWEN3_TTS_DEFAULT_SPEAKER:-Vivian}"
export QWEN3_TTS_DEFAULT_LANGUAGE="${QWEN3_TTS_DEFAULT_LANGUAGE:-zh}"
export QWEN3_TTS_ATTN_IMPL="${QWEN3_TTS_ATTN_IMPL:-}"
export QWEN3_TTS_API_KEYS="${QWEN3_TTS_API_KEYS:-tts-key-1}"
export TTS_API_HOST="${TTS_API_HOST:-0.0.0.0}"
export TTS_API_PORT="${TTS_API_PORT:-8010}"

exec "${UVICORN_BIN}" \
  "${APP_MODULE}" \
  --app-dir "${SCRIPT_DIR}" \
  --host "${TTS_API_HOST}" \
  --port "${TTS_API_PORT}"
