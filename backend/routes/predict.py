from uuid import uuid4

from fastapi import APIRouter, HTTPException

import core.config as cfg
from core.config import INSIGHT_TEMPLATE
from services.followup_questions import get_followup_pack_by_id, normalize_followup_answers
from services.mapper import UniversalMapper
from services.router import UniversalRouter
from services.ai_orchestrator import AIOrchestrator
from services.cost_converter import effort_to_inr
from services.currency_converter import convert_from_inr
from schemas.request_response import (
    CostBreakdown,
    EstimatedEffort,
    FinalAssemblyRequest,
    FinalAssemblyResponse,
    FinalPredictionRequest,
    FinalPredictionResponse,
    IntakeFollowUpResponse,
    PublicIntakeResponse,
    RouteInferenceMetadata,
    NormalizedUniversalPredictionRequest,
    PredictionRequest,
    PredictionResponse,
    UniversalPredictionRequest,
    normalize_universal_request,
)
from src.predictor import predict_cost

router = APIRouter()
universal_router = UniversalRouter()
universal_mapper = UniversalMapper()
ai_orchestrator = AIOrchestrator()
intake_metadata_cache: dict[str, RouteInferenceMetadata] = {}
intake_payload_cache: dict[str, NormalizedUniversalPredictionRequest] = {}
MAX_CACHED_INTAKES = 1000


def cache_intake_context(metadata: RouteInferenceMetadata, normalized_payload: NormalizedUniversalPredictionRequest) -> None:
    if len(intake_metadata_cache) >= MAX_CACHED_INTAKES:
        oldest_key = next(iter(intake_metadata_cache))
        intake_metadata_cache.pop(oldest_key, None)
        intake_payload_cache.pop(oldest_key, None)
    intake_metadata_cache[metadata.intake_id] = metadata
    intake_payload_cache[metadata.intake_id] = normalized_payload


def get_intake_context(intake_id: str) -> tuple[RouteInferenceMetadata, NormalizedUniversalPredictionRequest]:
    metadata = intake_metadata_cache.get(intake_id)
    payload = intake_payload_cache.get(intake_id)
    if metadata is None or payload is None:
        raise HTTPException(status_code=404, detail="intake_id not found or expired")
    return metadata, payload


@router.post(
    "/predict/intake",
    response_model=PublicIntakeResponse,
    tags=["Estimation"],
    summary="Stage 1 – Submit project brief and receive adaptive follow-up questions",
)
def infer_followup_pack(payload: UniversalPredictionRequest) -> PublicIntakeResponse:
    """
    Submit universal project brief (Stage 1).

    The backend predicts the best internal estimation route from the brief,
    then returns the adaptive follow-up question pack for Stage 2.
    No dataset names or routing details are exposed.
    """
    normalized = normalize_universal_request(payload)
    intake_id = str(uuid4())
    metadata = universal_router.infer_route(intake_id=intake_id, brief=normalized.project_brief)
    cache_intake_context(metadata, normalized)

    try:
        follow_up_pack = get_followup_pack_by_id(metadata.follow_up_pack_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PublicIntakeResponse(
        intake_id=intake_id,
        follow_up_pack=follow_up_pack,
        intake_version=normalized.version,
    )


@router.get(
    "/predict/followup/{intake_id}",
    response_model=IntakeFollowUpResponse,
    tags=["Internal"],
    summary="[Internal] Retrieve follow-up pack by intake_id (deprecated – use POST /predict/intake)",
    include_in_schema=False,
)
def get_followup_questions(intake_id: str) -> IntakeFollowUpResponse:
    metadata, _ = get_intake_context(intake_id)
    try:
        follow_up_pack = get_followup_pack_by_id(metadata.follow_up_pack_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IntakeFollowUpResponse(
        intake_id=intake_id,
        follow_up_pack=follow_up_pack,
    )


@router.post(
    "/predict/final/assemble",
    response_model=FinalAssemblyResponse,
    tags=["Internal"],
    summary="[Internal] Assemble mapped feature vector (debug/admin only)",
    include_in_schema=False,
)
def assemble_final_inputs(payload: FinalAssemblyRequest) -> FinalAssemblyResponse:
    metadata, normalized_payload = get_intake_context(payload.intake_id)

    try:
        follow_up_pack = get_followup_pack_by_id(metadata.follow_up_pack_id)
        normalized_answers, unresolved_fields = normalize_followup_answers(follow_up_pack, payload.follow_up_answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    mapped_features, mapping_diagnostics = universal_mapper.assemble(
        route=metadata.detected_route,
        brief=normalized_payload.project_brief,
        follow_up_answers=normalized_answers,
        unresolved_fields=unresolved_fields,
    )

    return FinalAssemblyResponse(
        intake_id=payload.intake_id,
        mapped_features=mapped_features,
        mapping_diagnostics=mapping_diagnostics,
    )


@router.post(
    "/predict/universal/normalize",
    response_model=NormalizedUniversalPredictionRequest,
    tags=["Internal"],
    summary="[Internal] Normalize and validate a universal project brief",
    include_in_schema=False,
)
def normalize_universal_payload(payload: UniversalPredictionRequest) -> NormalizedUniversalPredictionRequest:
    return normalize_universal_request(payload)


@router.post(
    "/predict/final",
    response_model=FinalPredictionResponse,
    tags=["Estimation"],
    summary="Stage 2 – Submit follow-up answers and receive cost estimate",
    responses={
        404: {"description": "intake_id not found or expired"},
        422: {"description": "Invalid follow-up answer values"},
        500: {"description": "Model prediction error"},
        502: {"description": "AI provider error"},
    },
)
def predict_final(payload: FinalPredictionRequest) -> FinalPredictionResponse:
    """
    Two-step adaptive prediction endpoint (Phase 5 + Phase 6).

    Accepts a completed intake (Stage 1 + Stage 2) and returns:
    - Effort estimate in person-months
    - INR base cost + display-currency conversion
    - Assumptions, warnings, and confidence
    """
    metadata, normalized_payload = get_intake_context(payload.intake_id)

    # --- Normalise Stage 2 answers ---
    try:
        follow_up_pack = get_followup_pack_by_id(metadata.follow_up_pack_id)
        normalized_answers, unresolved_fields = normalize_followup_answers(
            follow_up_pack, payload.follow_up_answers
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    brief = normalized_payload.project_brief
    brief_dict = {
        "num_screens": brief.num_screens,
        "num_entities": brief.num_entities,
        "duration_months": brief.duration_months,
        "team_experience_years": brief.team_experience_years,
        "pm_experience_years": brief.pm_experience_years,
        "complexity": brief.complexity.value if hasattr(brief.complexity, "value") else str(brief.complexity),
        "reliability": brief.reliability.value if hasattr(brief.reliability, "value") else str(brief.reliability),
        "team_size": brief.team_size,
        "project_notes": brief.project_notes,
    }

    if cfg.PREDICTION_MODE == "ai":
        # --- AI mode ---
        try:
            result = ai_orchestrator.estimate_effort(
                brief=brief_dict,
                follow_up_answers=normalized_answers,
                profile_id=payload.profile_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"AI provider error: {exc}") from exc

        effort_months: float = result["effort_months"]
        confidence: float = result["confidence"]
        assumptions: list[str] = result["assumptions"]
        warnings: list[str] = result["warnings"]
        prediction_mode = "ai"

    else:
        # --- Model mode (baseline ML, Phase 10 will complete this) ---
        mapped_features, mapping_diagnostics = universal_mapper.assemble(
            route=metadata.detected_route,
            brief=brief,
            follow_up_answers=normalized_answers,
            unresolved_fields=unresolved_fields,
        )
        try:
            ml_result = predict_cost(
                metadata.detected_route.value,
                mapped_features,
                ensemble_method="simple",
                weights=None,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Model prediction error: {exc}") from exc

        effort_months = float(ml_result["ensemble_prediction"])
        confidence = float(mapping_diagnostics.mapping_confidence)
        assumptions = ["Effort derived from ensemble of baseline ML models."]
        warnings = []
        if unresolved_fields:
            warnings.append(f"Some fields used default values: {', '.join(unresolved_fields)}")
        prediction_mode = "model"

    # --- Phase 6: Cost derivation ---
    monthly_rate_inr = cfg.DEFAULT_MONTHLY_RATE_INR
    base_cost_inr = effort_to_inr(effort_months, monthly_rate_inr)
    target_currency = payload.target_currency
    try:
        display_cost, exchange_rate = convert_from_inr(base_cost_inr, target_currency)
    except ValueError:
        # Unsupported currency – fall back to INR.
        target_currency = "INR"
        display_cost = base_cost_inr
        exchange_rate = 1.0
        warnings.append(
            f"Requested currency '{payload.target_currency}' is not supported. Showing INR."
        )

    estimated_effort = EstimatedEffort(
        effort_months=round(effort_months, 2),
        confidence=round(confidence, 4),
        assumptions=assumptions,
        warnings=warnings,
        prediction_mode=prediction_mode,
    )
    cost_breakdown = CostBreakdown(
        effort_months=round(effort_months, 2),
        monthly_rate_inr=monthly_rate_inr,
        base_cost_inr=base_cost_inr,
        target_currency=target_currency,
        display_cost=display_cost,
        exchange_rate=exchange_rate,
    )
    return FinalPredictionResponse(
        intake_id=payload.intake_id,
        estimated_effort=estimated_effort,
        cost_breakdown=cost_breakdown,
        prediction_confidence=round(confidence, 4),
        assumptions=assumptions,
        warnings=warnings,
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Legacy"],
    summary="[Legacy] Direct dataset-based prediction (deprecated)",
    include_in_schema=False,
)
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
