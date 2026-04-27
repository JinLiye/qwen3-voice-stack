from openai import OpenAI
import os

base_url = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1")
api_key = os.getenv("OPENAI_API_KEY", "replace-with-your-key")
model = os.getenv("OPENAI_MODEL", "qwen3-8b")

client = OpenAI(base_url=base_url, api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Give me a short introduction to Qwen3-8B."},
    ],
    temperature=0.4,
)

print(response.choices[0].message.content)
