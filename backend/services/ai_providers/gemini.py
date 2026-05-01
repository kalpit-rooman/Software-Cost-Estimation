from __future__ import annotations

import json

import httpx

from services.ai_providers.base import BaseAIProvider

_DEFAULT_TIMEOUT_S: float = 60.0
_GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(BaseAIProvider):
    """
    Provider adapter for Google Gemini generateContent REST API.

    Uses the v1beta REST endpoint directly via httpx — no google-generativeai
    SDK dependency required.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        timeout_s: float = _DEFAULT_TIMEOUT_S,
        max_output_tokens: int = 512,
    ) -> None:
        if not api_key:
            raise ValueError("GeminiProvider requires a non-empty api_key.")
        self._api_key = api_key
        self._model = model
        self._timeout_s = timeout_s
        self._max_output_tokens = max_output_tokens

    @property
    def provider_name(self) -> str:
        return "gemini"

    def predict_effort(self, prompt: str, system_prompt: str) -> str:
        """Call the Gemini generateContent endpoint and return the text response."""
        url = f"{_GEMINI_API_BASE}/{self._model}:generateContent?key={self._api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "maxOutputTokens": self._max_output_tokens,
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        try:
            with httpx.Client(timeout=self._timeout_s) as client:
                response = client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                f"Gemini request timed out after {self._timeout_s}s."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Gemini network error: {exc}") from exc

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini returned HTTP {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected Gemini response shape: {json.dumps(data)[:500]}"
            ) from exc
