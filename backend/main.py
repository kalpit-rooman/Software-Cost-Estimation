from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.config import PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from routes.admin import router as admin_router
from routes.chat import router as chat_router
from routes.health import router as health_router
from routes.meta import router as meta_router
from routes.predict import router as predict_router
from src.predictor import InvalidDatasetError, InvalidInputError, load_prediction_service

# ---------------------------------------------------------------------------
# OpenAPI metadata
# ---------------------------------------------------------------------------
_DESCRIPTION = """
## Software Cost Estimator API

Two-step adaptive cost estimation.  No dataset names are exposed.

### Public flow

1. **POST /predict/intake** – Submit project brief. Receive adaptive follow-up questions.
2. **POST /predict/final** – Submit follow-up answers. Receive effort estimate and cost breakdown.

### Authentication
No authentication is required for the public estimation endpoints.
"""

_TAGS_METADATA = [
    {
        "name": "Estimation",
        "description": "Public two-step adaptive estimation endpoints.",
    },
    {
        "name": "Legacy",
        "description": "Deprecated dataset-based endpoint kept for backward compatibility.",
    },
    {
        "name": "Internal",
        "description": "Internal/admin debugging endpoints (hidden from public docs).",
    },
    {
        "name": "Admin",
        "description": "Protected runtime configuration endpoints. Require Bearer token (ADMIN_API_KEY).",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        load_prediction_service()
    except Exception as exc:  # noqa: BLE001
        import logging
        logging.getLogger("uvicorn.error").warning(
            "Prediction service failed to load at startup: %s. "
            "The new adaptive endpoints (POST /predict/intake, POST /predict/final) "
            "will still work. The legacy /predict endpoint requires models.", exc
        )
    yield


app = FastAPI(
    title="Software Cost Estimator",
    description=_DESCRIPTION,
    version="1.0.0",
    openapi_tags=_TAGS_METADATA,
    lifespan=lifespan,
)

_ALLOWED_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


# ---------------------------------------------------------------------------
# Standardised error helpers
# ---------------------------------------------------------------------------

def _error_body(error_code: str, message: str, field: str | None = None) -> dict:
    body: dict = {"error_code": error_code, "message": message}
    if field is not None:
        body["field"] = field
    return body


@app.exception_handler(InvalidDatasetError)
async def invalid_dataset_handler(_: Request, exc: InvalidDatasetError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=_error_body("INVALID_DATASET", str(exc), field="dataset"),
    )


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(_: Request, exc: InvalidInputError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_body("INVALID_INPUT", str(exc)),
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
    first = exc.errors()[0]
    field = ".".join(str(loc) for loc in first.get("loc", []))
    return JSONResponse(
        status_code=422,
        content=_error_body("VALIDATION_ERROR", first["msg"], field=field or None),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_error_body("INTERNAL_ERROR", "An unexpected error occurred."),
    )


app.include_router(predict_router)
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(meta_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    _reload = os.getenv("UVICORN_RELOAD", "false").lower() == "true"
    _port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=_port, reload=_reload)
