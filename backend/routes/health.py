import logging

from fastapi import APIRouter

from schemas.request_response import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Shallow liveness check — always returns ok."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
def health_ready() -> HealthResponse:
    """
    Deep readiness check — verifies that the ML prediction service is loaded.

    Returns status 'ok' if models are ready, 'degraded' if only AI/adaptive
    endpoints will work.
    """
    try:
        from src.predictor import _PREDICTION_SERVICE  # noqa: PLC0415
        if _PREDICTION_SERVICE is not None:
            return HealthResponse(status="ok")
    except Exception:
        pass
    return HealthResponse(status="degraded")
