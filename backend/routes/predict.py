from fastapi import APIRouter

from core.config import INSIGHT_TEMPLATE
from schemas.request_response import PredictionRequest, PredictionResponse
from src.predictor import predict_cost

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    prediction = predict_cost(
        payload.dataset,
        payload.features,
        ensemble_method="simple",
        weights=None,
    )
    best_model = str(prediction["best_model"])
    return PredictionResponse(
        rf_prediction=float(prediction["rf_prediction"]),
        xgb_prediction=float(prediction["xgb_prediction"]),
        lr_prediction=float(prediction["lr_prediction"]),
        ensemble_prediction=float(prediction["ensemble_prediction"]),
        best_model=best_model,
        insight=INSIGHT_TEMPLATE.format(best_model=best_model),
    )
