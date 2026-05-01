from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAIProvider(ABC):
    """Abstract interface that every AI provider adapter must implement."""

    @abstractmethod
    def predict_effort(self, prompt: str, system_prompt: str) -> str:
        """
        Send a prediction request to the AI provider.

        Parameters
        ----------
        prompt:
            The user-facing prompt containing project context.
        system_prompt:
            The system instruction that shapes model behaviour.

        Returns
        -------
        str
            Raw text response from the provider. Callers are responsible
            for JSON extraction and validation.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (never exposed publicly)."""
        raise NotImplementedError

    def build_context_dict(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return provider metadata for internal diagnostics only."""
        base: dict[str, Any] = {"provider": self.provider_name}
        if extra:
            base.update(extra)
        return base
