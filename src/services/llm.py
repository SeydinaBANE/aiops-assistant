from __future__ import annotations

from openai import OpenAI

from src.config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client  # noqa: PLW0603
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            max_retries=2,
        )
    return _client


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature,
    )
    return response.choices[0].message.content or ""
