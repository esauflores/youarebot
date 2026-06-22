from openai import OpenAI
from typing import Dict, List

from app.api.config import LLM_URL
from app.core.logging import app_logger

SYSTEM_PROMPT = (
    "You are participating in a Turing test. Your task is to respond "
    "to the person in the most human-like and convincing way. "
    "Use the same language as the person. Be casual, make typos sometimes, "
    "use informal language. Keep responses short (1-3 sentences). "
    "Never reveal you are an AI."
)

client = OpenAI(base_url=f"{LLM_URL}/v1", api_key="not-needed")


def get_llm_reply(history: List[Dict[str, str]]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        role = "user" if msg["participant_index"] == 0 else "assistant"
        messages.append({"role": role, "content": msg["text"]})

    app_logger.info(f"Sending {len(messages) - 1} history messages to LLM")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=256,
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()
