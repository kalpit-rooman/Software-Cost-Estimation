from __future__ import annotations

import json
import re
from typing import Any

# ---------------------------------------------------------------------------
# AI Response Parser
# ---------------------------------------------------------------------------
# Extracts and validates a JSON object from raw AI provider text output.
# Handles markdown code fences, leading/trailing whitespace, and common
# response wrapping patterns.
# ---------------------------------------------------------------------------

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]+?)\s*```", re.IGNORECASE)
_REQUIRED_KEYS: frozenset[str] = frozenset({"effort_months", "confidence", "assumptions", "warnings"})


class AIResponseParseError(ValueError):
    """Raised when the AI response cannot be parsed into the expected structure."""


def extract_json_from_text(raw_text: str) -> dict[str, Any]:
    """
    Extract a JSON object from raw AI provider response text.

    Tries, in order:
    1. Direct JSON parse.
    2. Extract from a markdown code fence (```json ... ``` or ``` ... ```).
    3. Find the first {...} block in the text.

    Raises
    ------
    AIResponseParseError
        If no valid JSON object can be extracted.
    """
    text = raw_text.strip()

    # Attempt 1 – direct parse.
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Attempt 2 – markdown code fence extraction.
    match = _JSON_FENCE_RE.search(text)
    if match:
        try:
            result = json.loads(match.group(1))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Attempt 3 – first {...} block.
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        candidate = text[brace_start : brace_end + 1]
        try:
            result = json.loads(candidate)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    raise AIResponseParseError(
        f"Could not extract a JSON object from AI response. "
        f"Raw preview: {text[:300]!r}"
    )


def parse_ai_effort_response(raw_text: str) -> dict[str, Any]:
    """
    Parse and do basic type coercion on the AI effort estimation response.

    Expected keys: effort_months (float), confidence (float),
    assumptions (list[str]), warnings (list[str]).

    Raises
    ------
    AIResponseParseError
        If required keys are missing or types are irrecoverably wrong.
    """
    data = extract_json_from_text(raw_text)

    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        raise AIResponseParseError(
            f"AI response is missing required keys: {sorted(missing)}. Got: {sorted(data.keys())}"
        )

    # Coerce effort_months.
    try:
        data["effort_months"] = float(data["effort_months"])
    except (TypeError, ValueError) as exc:
        raise AIResponseParseError(
            f"effort_months must be numeric, got: {data['effort_months']!r}"
        ) from exc

    # Coerce confidence.
    try:
        data["confidence"] = float(data["confidence"])
    except (TypeError, ValueError) as exc:
        raise AIResponseParseError(
            f"confidence must be numeric, got: {data['confidence']!r}"
        ) from exc

    # Coerce assumptions/warnings to lists of strings.
    for list_key in ("assumptions", "warnings"):
        if not isinstance(data[list_key], list):
            # Tolerate a single string wrapped in a list.
            data[list_key] = [str(data[list_key])]
        else:
            data[list_key] = [str(item) for item in data[list_key]]

    return data
