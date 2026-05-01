from __future__ import annotations

from typing import Any

import core.config as cfg
from services.ai_providers.base import BaseAIProvider
from services.ai_providers.openai_compatible import OpenAICompatibleProvider
from services.ai_providers.gemini import GeminiProvider
from services.ai_response_parser import parse_ai_effort_response, AIResponseParseError
from services.guardrails import validate_effort_response, GuardrailViolation
from services.prompts.profiles import get_profile, PromptProfile

# ---------------------------------------------------------------------------
# Prompt construction helpers
# ---------------------------------------------------------------------------

_COMPLEXITY_MAP = {"low": "Low", "medium": "Medium", "high": "High"}
_RELIABILITY_MAP = {"low": "Low (best-effort)", "medium": "Medium (standard)", "high": "High (mission-critical)"}


def _build_user_prompt(
    brief: dict[str, Any],
    follow_up_answers: dict[str, Any],
    profile: PromptProfile,
) -> str:
    """Build the user-facing prompt from Stage 1 + Stage 2 inputs."""
    complexity = _COMPLEXITY_MAP.get(str(brief.get("complexity", "medium")), "Medium")
    reliability = _RELIABILITY_MAP.get(str(brief.get("reliability", "medium")), "Medium (standard)")

    lines = [
        "## Project Characteristics",
        "",
        f"- Screens / pages: {brief.get('num_screens', 'N/A')}",
        f"- Data entities: {brief.get('num_entities', 'N/A')}",
        f"- Target delivery duration: {brief.get('duration_months', 'N/A')} months",
        f"- Team size: {brief.get('team_size', 'N/A')} people",
        f"- Average team experience: {brief.get('team_experience_years', 'N/A')} years",
        f"- Project manager experience: {brief.get('pm_experience_years', 'N/A')} years",
        f"- Complexity: {complexity}",
        f"- Reliability requirement: {reliability}",
    ]

    notes = brief.get("project_notes")
    if notes:
        lines.append(f"- Additional context: {notes}")

    if follow_up_answers:
        lines.append("")
        lines.append("## Additional Project Details")
        lines.append("")
        for key, value in follow_up_answers.items():
            readable_key = key.replace("_", " ").title()
            lines.append(f"- {readable_key}: {value}")

    lines.append("")
    lines.append(
        "Based on the above, estimate the total effort in person-months needed "
        "to complete this software project from inception to delivery."
    )
    lines.append(profile.user_prompt_suffix)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

def _build_provider() -> BaseAIProvider:
    """Instantiate the correct AI provider based on runtime config."""
    provider_id = cfg.AI_PROVIDER.lower()

    if provider_id == "gemini":
        api_key = cfg.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError(
                "AI_PROVIDER is set to 'gemini' but GEMINI_API_KEY is not configured."
            )
        return GeminiProvider(api_key=api_key, model=cfg.AI_MODEL or "gemini-1.5-flash")

    # Default: OpenAI-compatible (also covers Groq, Mistral, Together, etc.)
    api_key = cfg.OPENAI_API_KEY or cfg.GROQ_API_KEY
    if not api_key:
        raise RuntimeError(
            f"AI_PROVIDER is '{provider_id}' but neither OPENAI_API_KEY "
            "nor GROQ_API_KEY is set."
        )
    base_url = cfg.OPENAI_BASE_URL or "https://api.openai.com/v1"
    model = cfg.AI_MODEL or "gpt-4o-mini"
    return OpenAICompatibleProvider(api_key=api_key, model=model, base_url=base_url)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class AIOrchestrator:
    """
    Coordinates AI provider selection, prompt construction, response parsing,
    and guardrail validation.

    Instances are created once at startup. Provider initialisation is lazy
    (on first call to ``estimate_effort``) to avoid hard failures during
    import time when keys are absent.
    """

    def __init__(self) -> None:
        self._provider: BaseAIProvider | None = None

    def _get_provider(self) -> BaseAIProvider:
        if self._provider is None:
            self._provider = _build_provider()
        return self._provider

    def estimate_effort(
        self,
        brief: dict[str, Any],
        follow_up_answers: dict[str, Any],
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run the full AI estimation pipeline.

        Parameters
        ----------
        brief:
            Stage 1 project brief as a plain dict (field values, not enum wrappers).
        follow_up_answers:
            Stage 2 normalised answers as a plain dict.
        profile_id:
            Override the default prompt profile. Falls back to ``cfg.AI_PROFILE``.

        Returns
        -------
        dict with keys: effort_months, confidence, assumptions, warnings

        Raises
        ------
        RuntimeError
            If the provider call fails.
        AIResponseParseError | GuardrailViolation
            If parsing or guardrail checks fail.
        """
        resolved_profile_id = profile_id or cfg.AI_PROFILE or "balanced"
        profile = get_profile(resolved_profile_id)

        user_prompt = _build_user_prompt(
            brief=brief,
            follow_up_answers=follow_up_answers,
            profile=profile,
        )

        provider = self._get_provider()
        raw_text = provider.predict_effort(
            prompt=user_prompt,
            system_prompt=profile.system_prompt,
        )

        parsed = parse_ai_effort_response(raw_text)
        validated = validate_effort_response(parsed)
        return validated
