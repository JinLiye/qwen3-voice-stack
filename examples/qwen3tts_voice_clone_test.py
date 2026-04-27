import os

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

model_path = os.getenv(
    "QWEN3_TTS_CLONE_MODEL_PATH",
    "/root/autodl-tmp/models/Qwen3-TTS-12Hz-1.7B-Base",
)
ref_audio = os.getenv("QWEN3_TTS_REF_AUDIO", "./ref.wav")
ref_text = os.getenv("QWEN3_TTS_REF_TEXT", "你好，这是用于音色克隆的参考音频文本。")
output_text = os.getenv("QWEN3_TTS_OUTPUT_TEXT", "你好，这是克隆后的音色测试。")
output_path = os.getenv("QWEN3_TTS_OUTPUT_PATH", "voice_clone_out.wav")
attn_impl = os.getenv("QWEN3_TTS_ATTN_IMPL", "") or None

kwargs = {
    "device_map": os.getenv("QWEN3_TTS_DEVICE", "cuda:0"),
    "dtype": torch.bfloat16,
}
if attn_impl:
    kwargs["attn_implementation"] = attn_impl

model = Qwen3TTSModel.from_pretrained(model_path, **kwargs)

wavs, sr = model.generate_voice_clone(
    text=output_text,
    ref_audio=ref_audio,
    ref_text=ref_text,
)

sf.write(output_path, wavs[0], sr)
print(f"saved cloned voice output to {output_path}")
