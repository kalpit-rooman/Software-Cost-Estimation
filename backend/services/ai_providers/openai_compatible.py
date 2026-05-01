from __future__ import annotations

import httpx

from services.ai_providers.base import BaseAIProvider

_DEFAULT_TIMEOUT_S: float = 60.0
_DEFAULT_MAX_TOKENS: int = 512


class OpenAICompatibleProvider(BaseAIProvider):
    """
    Provider adapter for OpenAI Chat Completions API and any compatible endpoint
    (e.g. Groq, Mistral, Together AI, local Ollama with OpenAI shim).

    The base_url defaults to the official OpenAI endpoint; override it via
    OPENAI_BASE_URL env var for alternative hosts.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_s: float = _DEFAULT_TIMEOUT_S,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI-compatible provider requires a non-empty api_key.")
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._max_tokens = max_tokens

    @property
    def provider_name(self) -> str:
        return "openai_compatible"

    def predict_effort(self, prompt: str, system_prompt: str) -> str:
        """Call the chat completions endpoint and return the assistant message text."""
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self._max_tokens,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=self._timeout_s) as client:
                response = client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                f"AI provider request timed out after {self._timeout_s}s."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"AI provider network error: {exc}") from exc

        if response.status_code != 200:
            raise RuntimeError(
                f"AI provider returned HTTP {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected response shape from AI provider: {data}"
            ) from exc
