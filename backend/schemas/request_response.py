from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    dataset: str = Field(..., examples=["china"])
    features: dict[str, Any] = Field(
        ...,
        description="Feature payload for the selected dataset.",
    )


class PredictionResponse(BaseModel):
    rf_prediction: float
    xgb_prediction: float
    lr_prediction: float
    ensemble_prediction: float
    best_model: str
    insight: str


class HealthResponse(BaseModel):
    status: str


class DatasetsResponse(BaseModel):
    datasets: list[str]
