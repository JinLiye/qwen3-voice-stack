#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/vllm-qwen3-8b.env"
CHAT_TEMPLATE_FILE="${SCRIPT_DIR}/qwen3-chat-template-default-system.jinja"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing env file: ${ENV_FILE}" >&2
  echo "Copy vllm-qwen3-8b.env.example to vllm-qwen3-8b.env and update it first." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

if [[ ! -f "${CHAT_TEMPLATE_FILE}" ]]; then
  echo "Missing chat template file: ${CHAT_TEMPLATE_FILE}" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-${SCRIPT_DIR}/.venv-vllm/bin/python}"
VLLM_BIN="${VLLM_BIN:-${SCRIPT_DIR}/.venv-vllm/bin/vllm}"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python binary not found or not executable: ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ ! -x "${VLLM_BIN}" ]]; then
  echo "vLLM binary not found or not executable: ${VLLM_BIN}" >&2
  exit 1
fi

if [[ -z "${MODEL_PATH:-}" ]]; then
  echo "Missing MODEL_PATH in ${ENV_FILE}" >&2
  exit 1
fi

DEFAULT_CHAT_TEMPLATE_KWARGS="$(${PYTHON_BIN} -c '
import json, os
print(json.dumps({
    "enable_thinking": False,
    "default_system_prompt": os.environ.get("DEFAULT_SYSTEM_PROMPT", "")
}, ensure_ascii=False))
')"

ARGS=(
  serve "${MODEL_PATH}"
  --served-model-name "${SERVED_MODEL_NAME}"
  --host "${HOST}"
  --port "${PORT}"
  --dtype "${DTYPE}"
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}"
  --max-model-len "${MAX_MODEL_LEN}"
  --trust-remote-code
  --chat-template "${CHAT_TEMPLATE_FILE}"
  --default-chat-template-kwargs "${DEFAULT_CHAT_TEMPLATE_KWARGS}"
  --enable-auto-tool-choice
  --tool-call-parser qwen3_xml
)

for key_name in API_KEY_1 API_KEY_2 API_KEY_3 API_KEY_4 API_KEY_5; do
  key_value="${!key_name:-}"
  if [[ -n "${key_value}" ]]; then
    ARGS+=(--api-key "${key_value}")
  fi
done

exec "${VLLM_BIN}" "${ARGS[@]}"
