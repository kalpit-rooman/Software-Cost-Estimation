"""
Runtime state manager (Phase 9 / Phase 10).

Holds in-memory configuration that can be updated by the admin API without
a redeploy.  Values are seeded from environment variables / core.config on
first access so that .env-based defaults still work.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

import core.config as cfg

_VALID_MODES = frozenset({"ai", "model"})
_VALID_PROFILES = frozenset({"conservative", "balanced", "optimistic"})

_lock = Lock()


@dataclass
class RuntimeState:
    prediction_mode: str        # "ai" | "model"
    ai_provider: str            # e.g. "openai", "gemini", "groq"
    ai_profile: str             # "conservative" | "balanced" | "optimistic"
    monthly_rate_inr: float     # blended monthly rate per person in INR
    default_currency: str       # display currency default (ISO-4217)


_state: RuntimeState | None = None


def get_state() -> RuntimeState:
    """Return the singleton runtime state, initialising from env/config on first call."""
    global _state
    with _lock:
        if _state is None:
            _state = RuntimeState(
                prediction_mode=cfg.PREDICTION_MODE,
                ai_provider=cfg.AI_PROVIDER,
                ai_profile=cfg.AI_PROFILE,
                monthly_rate_inr=cfg.DEFAULT_MONTHLY_RATE_INR,
                default_currency="INR",
            )
        return _state


def update_state(
    *,
    prediction_mode: str | None = None,
    ai_provider: str | None = None,
    ai_profile: str | None = None,
    monthly_rate_inr: float | None = None,
    default_currency: str | None = None,
) -> RuntimeState:
    """
    Apply a partial update to runtime state.

    Raises ValueError for invalid field values so the caller (admin route)
    can return a 422 before mutating state.
    """
    with _lock:
        state = get_state()

        if prediction_mode is not None:
            if prediction_mode not in _VALID_MODES:
                raise ValueError(f"prediction_mode must be one of {sorted(_VALID_MODES)!r}")
            state.prediction_mode = prediction_mode

        if ai_provider is not None:
            state.ai_provider = ai_provider

        if ai_profile is not None:
            if ai_profile not in _VALID_PROFILES:
                raise ValueError(f"ai_profile must be one of {sorted(_VALID_PROFILES)!r}")
            state.ai_profile = ai_profile

        if monthly_rate_inr is not None:
            if monthly_rate_inr <= 0:
                raise ValueError("monthly_rate_inr must be a positive number")
            state.monthly_rate_inr = monthly_rate_inr

        if default_currency is not None:
            state.default_currency = default_currency.upper()

        return state
