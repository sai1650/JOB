import os
import json
import time
from typing import Any, Dict, Optional

from app.core.config import settings

try:
    import openai
except Exception:
    openai = None


class LLMClient:
    """Simple LLM client wrapper supporting OpenAI (if available) and a
    local callable fallback. Methods return raw model text (string).
    """

    def __init__(self, provider: str = "openai",
                 api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if provider == "openai" and openai is not None and self.api_key:
            openai.api_key = self.api_key

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if self.provider == "openai":
            if openai is None or not self.api_key:
                raise RuntimeError(
                    "OpenAI client not configured or api key missing"
                )

            retries = max(1, settings.LLM_RETRY_COUNT)
            backoff = 1.0
            last_exc = None
            for attempt in range(retries):
                try:
                    # Use ChatCompletion if available
                    if hasattr(openai, "ChatCompletion"):
                        resp = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=max_tokens,
                        )
                        return resp.choices[0].message.content
                    else:
                        resp = openai.Completion.create(
                            model="text-davinci-003",
                            prompt=prompt,
                            max_tokens=max_tokens,
                        )
                        return resp.choices[0].text
                except Exception as exc:
                    last_exc = exc
                    # simple backoff
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 10.0)

            # if we get here, retries exhausted
            raise RuntimeError("LLM generation failed") from last_exc
        else:
            # provider not supported; user may pass a callable instead
            raise RuntimeError("Unsupported LLM provider")


def build_question_prompt(payload: Dict[str, Any]) -> str:
    """Safe prompt template that instructs the model to output JSON
    array of question objects with the required schema.
    """
    template = (
        "You are an interview question generator. Given the input, generate "
        "a JSON array of interview question objects. Each object must have: "
        "'question', 'topic', and 'difficulty' (easy|medium|hard). "
        "Provide a 'question_type' and include a 'reason'. "
        "Also include 'source_context' as an array of {source,page}. "
        "Do not invent sources; only use provided retrieved_context.chunks. "
        "Output must be valid JSON."
        "\n\nInput:\n"
    )
    return template + json.dumps(payload)
