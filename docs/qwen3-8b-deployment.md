# Qwen3-8B Deployment Guide

This document defines the first reproducible milestone of the project: deploy `Qwen3-8B` with `vLLM`, expose an OpenAI-compatible API, and verify that requests succeed on a GPU server.

## Goal
By the end of this guide you should be able to:
- create a clean Miniconda environment
- install `vLLM` and required Python packages
- download or prepare the `Qwen3-8B` model weights
- start the service with a stable shell script
- verify `/v1/models` and `/v1/chat/completions`

## Recommended Environment
- OS: Ubuntu 22.04 or a compatible Linux distribution
- GPU: RTX 5090 or another CUDA-capable GPU with enough VRAM
- Python: 3.12 via Miniconda
- CUDA: match the installed PyTorch and `vLLM` build

## Directory Layout
Recommended layout on the target server:

```text
~/qwen3-voice-stack/
  scripts/
    run-vllm-qwen3-8b.sh
  examples/
    qwen3_openai_client.py
  docs/
  qwen3-chat-template-default-system.jinja
  vllm-qwen3-8b.env.example
```

Model weights can live outside the repository if preferred, for example:

```text
/root/autodl-tmp/models/Qwen3-8B/
```

## Step 1: Create the Conda Environment

```bash
conda create -n qwen3-vllm python=3.12 -y
source /root/.bashrc
# If this is the first time `conda init` has been used in the shell:
# conda init bash
# source /root/.bashrc
conda activate qwen3-vllm
```

Note:
- After running `conda init`, the current shell usually needs `source /root/.bashrc` before `conda activate` works.
- If `conda activate` reports that your shell is not initialized, reload the shell config first and then retry.

## Step 2: Install Dependencies
Install packages in the active environment.
The exact wheel strategy may vary depending on your CUDA stack.

```bash
pip install --upgrade pip
pip install vllm openai
```

If the server image already provides CUDA-compatible PyTorch and `vLLM`, use that known-good combination instead of changing versions blindly.

## Step 3: Prepare the Model Weights
Set `MODEL_PATH` to the local path of the `Qwen3-8B` model directory.
Example:

```bash
mkdir -p /root/autodl-tmp/models
pip install -U "huggingface_hub[cli]"
huggingface-cli download Qwen/Qwen3-8B \
  --local-dir /root/autodl-tmp/models/Qwen3-8B
```

If the environment uses a Hugging Face mirror, configure it first and then run the same download command:

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download Qwen/Qwen3-8B \
  --local-dir /root/autodl-tmp/models/Qwen3-8B
```

Do not commit model weights into this repository.

## Step 4: Create the Runtime Config
Copy the environment template:

```bash
cp vllm-qwen3-8b.env.example vllm-qwen3-8b.env
```

Update at least these fields:
- `MODEL_PATH`
- `VLLM_BIN`
- `PYTHON_BIN`
- `API_KEY_1`

If you do not want a built-in default system prompt, leave `DEFAULT_SYSTEM_PROMPT` empty.

## Step 5: Start the Service

```bash
chmod +x scripts/run-vllm-qwen3-8b.sh
./scripts/run-vllm-qwen3-8b.sh
```

Default endpoint:
- `http://0.0.0.0:8000/v1`

## Step 6: Verify the Service

### List Models

```bash
curl http://127.0.0.1:8000/v1/models \
  -H "Authorization: Bearer replace-with-your-key"
```

### Basic Chat Completion

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer replace-with-your-key" \
  -d '{
    "model": "qwen3-8b",
    "messages": [
      {"role": "user", "content": "Give me a short introduction to Qwen3-8B."}
    ],
    "stream": false
  }'
```

### Python SDK Example

```bash
python examples/qwen3_openai_client.py
```

## Key Parameters
- `GPU_MEMORY_UTILIZATION`: controls how aggressively vLLM uses GPU memory
- `MAX_MODEL_LEN`: sets the maximum context window exposed by the service
- `DTYPE`: common values are `bfloat16` or `half`, depending on hardware and compatibility
- `SERVED_MODEL_NAME`: the model id used by clients

## Known Pitfalls
- If `conda activate` does not work after `conda init`, run `source /root/.bashrc` in the current shell.
- If `vllm` is not found, verify `VLLM_BIN` points to the active conda environment.
- If startup fails on CUDA or PyTorch issues, re-check the server image, driver, and package compatibility.
- If requests fail with 401, confirm the request key matches one of the configured API keys.
- If the model path is wrong, vLLM will fail early; check `MODEL_PATH` before debugging anything else.

## What This Milestone Does Not Cover Yet
- Whisper speech-to-text
- Qwen3-TTS
- web integration
- AutoDL-specific adaptation

Those will be added in later milestones.
