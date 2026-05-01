"""
Admin routes (Phase 9).

All endpoints require a valid bearer token (ADMIN_API_KEY env var).

Endpoints:
  GET  /admin/state        – return current runtime state
  PATCH /admin/state       – partial-update runtime state
  GET  /admin/diagnostics  – lightweight liveness + mode diagnostics
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from services.admin_auth import require_admin_key
from services.state_manager import get_state, update_state

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class AdminStateResponse(BaseModel):
    prediction_mode: str
    ai_provider: str
    ai_profile: str
    monthly_rate_inr: float
    default_currency: str


class AdminStateUpdate(BaseModel):
    """All fields are optional; only provided fields are mutated."""

    prediction_mode: str | None = Field(
        default=None,
        description='Prediction runtime: "ai" or "model".',
    )
    ai_provider: str | None = Field(
        default=None,
        description='AI provider: "openai", "gemini", "groq", etc.',
    )
    ai_profile: str | None = Field(
        default=None,
        description='Prompt profile: "conservative", "balanced", or "optimistic".',
    )
    monthly_rate_inr: float | None = Field(
        default=None,
        gt=0,
        description="Blended monthly rate per person in INR (must be > 0).",
    )
    default_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="ISO-4217 display currency code (e.g. INR, USD).",
    )

    @field_validator("prediction_mode")
    @classmethod
    def _validate_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in ("ai", "model"):
            raise ValueError('prediction_mode must be "ai" or "model"')
        return v

    @field_validator("ai_profile")
    @classmethod
    def _validate_profile(cls, v: str | None) -> str | None:
        if v is not None and v not in ("conservative", "balanced", "optimistic"):
            raise ValueError('ai_profile must be "conservative", "balanced", or "optimistic"')
        return v


class AdminDiagnosticsResponse(BaseModel):
    status: str
    prediction_mode: str
    ai_provider: str
    ai_profile: str
    monthly_rate_inr: float
    default_currency: str
    model_service_loaded: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/state",
    response_model=AdminStateResponse,
    summary="Get current runtime configuration",
)
def get_runtime_state(_: None = Depends(require_admin_key)) -> AdminStateResponse:
    """Return the current in-memory runtime state."""
    s = get_state()
    return AdminStateResponse(
        prediction_mode=s.prediction_mode,
        ai_provider=s.ai_provider,
        ai_profile=s.ai_profile,
        monthly_rate_inr=s.monthly_rate_inr,
        default_currency=s.default_currency,
    )


@router.patch(
    "/state",
    response_model=AdminStateResponse,
    summary="Update runtime configuration (partial)",
)
def patch_runtime_state(
    body: AdminStateUpdate,
    _: None = Depends(require_admin_key),
) -> AdminStateResponse:
    """
    Partially update runtime state.  Only fields present in the request body
    are changed; all others keep their current values.
    """
    updates = body.model_dump(exclude_none=True)
    try:
        s = update_state(**updates)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return AdminStateResponse(
        prediction_mode=s.prediction_mode,
        ai_provider=s.ai_provider,
        ai_profile=s.ai_profile,
        monthly_rate_inr=s.monthly_rate_inr,
        default_currency=s.default_currency,
    )


@router.get(
    "/diagnostics",
    response_model=AdminDiagnosticsResponse,
    summary="Runtime diagnostics (liveness + mode info)",
)
def get_diagnostics(_: None = Depends(require_admin_key)) -> AdminDiagnosticsResponse:
    """Return live status alongside current runtime configuration."""
    from src.predictor import _PREDICTION_SERVICE  # noqa: PLC0415  (local import to avoid circular dep)
    s = get_state()
    return AdminDiagnosticsResponse(
        status="ok",
        prediction_mode=s.prediction_mode,
        ai_provider=s.ai_provider,
        ai_profile=s.ai_profile,
        monthly_rate_inr=s.monthly_rate_inr,
        default_currency=s.default_currency,
        model_service_loaded=_PREDICTION_SERVICE is not None,
    )
