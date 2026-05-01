from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# ---------------------------------------------------------------------------
# Prompt profile definitions
# ---------------------------------------------------------------------------
# Each profile shapes how the system prompt instructs the AI estimator.
# Profiles affect tone, risk posture, and effort assumptions — they do NOT
# change the required JSON output contract.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptProfile:
    profile_id: str
    title: str
    system_prompt: str
    user_prompt_suffix: str


_SYSTEM_BASE: Final[str] = (
    "You are an expert software project estimator. "
    "Your task is to estimate the effort required to deliver a software project "
    "based on the project characteristics provided. "
    "You MUST respond with a single valid JSON object and nothing else. "
    "Do NOT include markdown formatting, code fences, or explanatory text outside the JSON. "
    "Required JSON schema:\n"
    "{\n"
    '  "effort_months": <float, person-months, must be > 0>,\n'
    '  "confidence": <float between 0.0 and 1.0>,\n'
    '  "assumptions": [<string>, ...],\n'
    '  "warnings": [<string>, ...]\n'
    "}"
)

_CONSERVATIVE_ADDITION: Final[str] = (
    "\n\nAdopt a risk-aware posture. Assume scope creep, integration delays, "
    "and moderate team ramp-up time. Provide a conservatively high effort estimate "
    "that a project manager can defend when things go wrong. "
    "Reflect any high-risk factors clearly in the warnings list."
)

_OPTIMISTIC_ADDITION: Final[str] = (
    "\n\nAdopt an optimistic posture. Assume the team is experienced, requirements "
    "are stable, and delivery is streamlined. Reflect this in a lean estimate. "
    "Document your optimistic assumptions clearly in the assumptions list."
)

_BALANCED_ADDITION: Final[str] = (
    "\n\nAdopt a balanced posture. Weigh both favourable and unfavourable factors "
    "and produce a realistic mid-range estimate. Document significant assumptions "
    "and any notable risk factors."
)


CONSERVATIVE = PromptProfile(
    profile_id="conservative",
    title="Conservative (risk-aware)",
    system_prompt=_SYSTEM_BASE + _CONSERVATIVE_ADDITION,
    user_prompt_suffix=(
        "\n\nRemember: apply conservative risk buffers. "
        "Do not underestimate complexity or integration effort."
    ),
)

BALANCED = PromptProfile(
    profile_id="balanced",
    title="Balanced (realistic)",
    system_prompt=_SYSTEM_BASE + _BALANCED_ADDITION,
    user_prompt_suffix=(
        "\n\nProduce a balanced, realistic estimate. "
        "Justify your confidence level based on information completeness."
    ),
)

OPTIMISTIC = PromptProfile(
    profile_id="optimistic",
    title="Optimistic (best-case)",
    system_prompt=_SYSTEM_BASE + _OPTIMISTIC_ADDITION,
    user_prompt_suffix=(
        "\n\nApply optimistic assumptions. "
        "Only flag warnings for genuinely critical risks."
    ),
)

_REGISTRY: dict[str, PromptProfile] = {
    "conservative": CONSERVATIVE,
    "balanced": BALANCED,
    "optimistic": OPTIMISTIC,
}


def get_profile(profile_id: str) -> PromptProfile:
    """Return the PromptProfile for the given id. Defaults to balanced."""
    return _REGISTRY.get(profile_id.lower(), BALANCED)


def list_profile_ids() -> list[str]:
    return list(_REGISTRY.keys())
