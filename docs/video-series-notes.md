# QwenDeploye v2 Video Series Notes

## Purpose
This document is the long-term working memory for the video series around this project.
It records positioning, episode planning, speaking notes, Git milestones, publishing ideas, and follow-up tasks.
Update this file continuously as the project evolves.

## Current Project Positioning
Working title:
- Local voice LLM application stack on real hardware
- Whisper + Qwen3-8B + Qwen3-TTS + Web Demo

Current judgment:
- Suitable for a tutorial series
- Best framed as a real-machine engineering walkthrough, not a beginner-proof one-click tutorial yet
- Strong value points: full pipeline, real GPU validation, practical deployment experience

Known strengths:
- End-to-end pipeline exists: STT -> LLM -> TTS -> Web
- Tested on RTX 5090 real hardware
- Multiple services already split by responsibility
- Has room for later AutoDL migration and open-source packaging

Known weaknesses before public release:
- Project root is still a working directory, not a clean public repo
- Sensitive defaults and local-only config need cleanup
- No public-facing top-level README yet
- Docs and structure need normalization
- Large local assets, models, envs, logs, and generated data should not enter the public repository

## Channel Direction
Recommended channel focus:
- Local or cloud deployment of LLM applications
- Small but complete LLM demos
- Practical engineering around open-source model serving

Channel value should come from:
- Real deployment
- Architecture judgment
- Pitfall explanations
- Reproducible engineering steps

Avoid positioning the channel as:
- Pure news commentary
- Generic prompt tips
- High-level AI discussion without runnable artifacts

## Series Structure
Recommended structure: 5 main episodes + 1 extension episode

### Episode 1
Name:
- Project overview and final demo

Goal:
- Show the finished effect first
- Explain the architecture and why the stack matters
- Establish the series direction

Core content:
- What the project does
- Hardware context: tested on RTX 5090
- Service topology
- One complete voice interaction demo
- What later episodes will implement or refine

Suggested Git milestone:
- tag: ep01-demo-overview

### Episode 2
Name:
- Deploy Qwen3-8B with vLLM

Goal:
- Build the LLM serving foundation

Core content:
- Model path and serving strategy
- vLLM startup script and env config
- OpenAI-compatible API usage
- Health check and basic request verification
- Important parameters: model length, memory utilization, API key handling

Suggested Git milestone:
- tag: ep02-vllm-qwen3

### Episode 3
Name:
- Build the Whisper STT service

Goal:
- Add speech-to-text as an independent service

Core content:
- Whisper model choices
- CPU vs GPU tradeoffs
- API design for transcription
- Example audio verification
- Latency and accuracy tradeoffs

Suggested Git milestone:
- tag: ep03-whisper-stt

### Episode 4
Name:
- Build the Qwen3-TTS service

Goal:
- Add text-to-speech as an independent service

Core content:
- TTS model choices
- Voice and language configuration
- Whole-response vs streaming response
- Audio formats and playback implications
- Latency and output quality considerations

Suggested Git milestone:
- tag: ep04-qwen3tts

### Episode 5
Name:
- Integrate the full voice web demo

Goal:
- Connect STT, LLM, and TTS into one web application

Core content:
- Frontend recording flow
- Backend orchestration
- History handling
- Error handling and service dependency order
- End-to-end demo

Suggested Git milestone:
- tag: ep05-voice-web-demo

### Episode 6
Name:
- Reproduce on AutoDL and prepare open-source release

Goal:
- Validate that the project works beyond the local 5090 machine
- Convert the project into a public GitHub repo

Core content:
- AutoDL environment differences
- Dependency migration issues
- Path and model configuration cleanup
- .env.example and repo cleanup
- Final public README and release packaging

Suggested Git milestone:
- tag: ep06-autodl-packaging

## Git Strategy
Principle:
- Day-to-day development can use normal commits
- Each episode should correspond to one stable milestone tag
- Every milestone should be runnable or at least demonstrably coherent

Recommended tag names:
- ep01-demo-overview
- ep02-vllm-qwen3
- ep03-whisper-stt
- ep04-qwen3tts
- ep05-voice-web-demo
- ep06-autodl-packaging

Recommended commit message style:
- feat(ep01): add project overview and public-facing docs
- feat(ep02): serve Qwen3-8B with vLLM and OpenAI-compatible API
- feat(ep03): add Whisper transcription service
- feat(ep04): add Qwen3-TTS synthesis service
- feat(ep05): integrate voice web demo end-to-end
- chore(ep06): prepare AutoDL deployment and open-source packaging

## Open Source Release Direction
Public repository should contain:
- README.md
- docs/
- service code that is actually part of the project
- launch scripts
- environment variable templates
- architecture diagram assets
- reproducible setup instructions

Public repository should exclude:
- .venv directories
- model weights
- logs
- generated databases
- local cert private keys
- real API keys or secrets
- local audio artifacts unless explicitly needed as small examples

## Publishing Strategy
Recommended order:
1. Validate on local RTX 5090
2. Reproduce on AutoDL
3. Clean and publish GitHub repo
4. Publish overview video
5. Publish deeper implementation episodes

Reasoning:
- Video should point to a usable repository
- Repository should be validated outside the author machine
- AutoDL broadens audience beyond high-end local GPU owners

## Audience Promise
The series should promise:
- Real engineering, not slideware
- Clear tradeoffs, not fake simplicity
- Repeatable deployment paths where feasible
- Honest discussion of hardware and environment limits

Avoid promising:
- One-click deployment for everyone
- Perfect portability before AutoDL validation is done
- Performance claims without measured data

## Speaking Style Notes
Preferred tone for the videos:
- Direct
- Practical
- Evidence-based
- No inflated claims

Useful recurring speaking patterns:
- What this solves
- Why this component exists
- What can break here
- What is good enough for now
- What should be improved later

## Future Content Ideas
Possible follow-up topics:
- Lower VRAM adaptation
- Service startup orchestration
- Docker-based packaging
- OpenWebUI integration
- Streaming latency optimization
- Better frontend UX for voice chat
- Monitoring and logging
- Multi-user access control

## Working Memory
This section is for persistent notes from ongoing discussion.
Append dated bullets here over time.

### 2026-04-27
- User wants to build a YouTube series around this project.
- Project has been tested on RTX 5090 real hardware.
- User is considering reproducing the project on AutoDL later.
- Public GitHub repository is intended to be linked under the videos.
- Series direction agreed: 5 main episodes plus 1 AutoDL/open-source packaging episode.
- Git milestones should map to tutorial episodes for easier audience navigation.
- This file is intended to preserve long-term planning context across future work sessions.
- Deployment note: after `conda init`, the shell must run `source /root/.bashrc` before `conda activate` takes effect.

## Next Recommended Actions
- Create a top-level public README draft
- Define public repo cleanup rules via .gitignore and env templates
- Document exact startup order for all services
- Validate one clean end-to-end run path
- Prepare AutoDL reproduction checklist
