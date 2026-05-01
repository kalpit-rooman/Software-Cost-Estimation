from __future__ import annotations

from typing import Any

from services.ai_response_parser import AIResponseParseError

# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------
# Validates parsed AI responses before they are surfaced in public API output.
# Catches out-of-range values, suspicious estimates, and schema violations.
# ---------------------------------------------------------------------------

_MIN_EFFORT_MONTHS: float = 0.5
_MAX_EFFORT_MONTHS: float = 600.0
_MIN_CONFIDENCE: float = 0.0
_MAX_CONFIDENCE: float = 1.0
_MAX_LIST_ITEMS: int = 20
_MAX_STRING_LENGTH: int = 500


class GuardrailViolation(ValueError):
    """Raised when a parsed AI response fails guardrail validation."""


def validate_effort_response(data: dict[str, Any]) -> dict[str, Any]:
    """
    Apply guardrail checks to a parsed AI effort estimation response.

    Parameters
    ----------
    data:
        Dict produced by ``parse_ai_effort_response``.

    Returns
    -------
    dict[str, Any]
        The same dict if all guardrails pass. Assumptions/warnings lists are
        clamped to ``_MAX_LIST_ITEMS`` items.

    Raises
    ------
    GuardrailViolation
        On any out-of-range or structurally invalid value.
    """
    effort: float = data.get("effort_months", 0.0)  # type: ignore[assignment]
    if not (_MIN_EFFORT_MONTHS <= effort <= _MAX_EFFORT_MONTHS):
        raise GuardrailViolation(
            f"effort_months {effort} is outside the allowed range "
            f"[{_MIN_EFFORT_MONTHS}, {_MAX_EFFORT_MONTHS}]."
        )

    confidence: float = data.get("confidence", -1.0)  # type: ignore[assignment]
    if not (_MIN_CONFIDENCE <= confidence <= _MAX_CONFIDENCE):
        raise GuardrailViolation(
            f"confidence {confidence} is outside the allowed range "
            f"[{_MIN_CONFIDENCE}, {_MAX_CONFIDENCE}]."
        )

    for list_key in ("assumptions", "warnings"):
        items: list[str] = data.get(list_key, [])  # type: ignore[assignment]
        # Clamp list length silently.
        data[list_key] = items[:_MAX_LIST_ITEMS]
        # Validate individual item length.
        for i, item in enumerate(data[list_key]):
            if len(item) > _MAX_STRING_LENGTH:
                data[list_key][i] = item[:_MAX_STRING_LENGTH]

    return data
