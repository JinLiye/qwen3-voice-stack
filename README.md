# qwen3-voice-stack

An end-to-end local voice AI stack built with Qwen3-8B, Whisper, Qwen3-TTS, vLLM, and a web demo.

## Status
This repository is being organized as a tutorial series project.
The first public milestone focuses on deploying `Qwen3-8B` with `vLLM` and verifying OpenAI-compatible API calls.

## Episode Milestones
- `ep01-demo-overview`: project overview and final demo
- `ep02-vllm-qwen3`: deploy Qwen3-8B with vLLM
- `ep03-whisper-stt`: add Whisper speech-to-text service
- `ep04-qwen3tts`: add Qwen3-TTS service
- `ep05-voice-web-demo`: integrate the full voice web demo
- `ep06-autodl-packaging`: AutoDL reproduction and open-source packaging

## Current Scope
The current milestone covers:
- Miniconda-based Python environment setup
- vLLM installation strategy
- Qwen3-8B model serving with an OpenAI-compatible API
- Basic API verification with `curl` and the OpenAI Python SDK

## Quick Start
See [docs/qwen3-8b-deployment.md](docs/qwen3-8b-deployment.md) for the step-by-step deployment guide.

## Repository Notes
This project is under active cleanup for public release.
Large local assets, model weights, virtual environments, and secrets are excluded from version control.
