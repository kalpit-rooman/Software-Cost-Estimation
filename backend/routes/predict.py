from uuid import uuid4

from fastapi import APIRouter, HTTPException

import core.config as cfg
from core.config import INSIGHT_TEMPLATE
from services.followup_questions import get_followup_pack_by_id, get_followup_pack_for_route, normalize_followup_answers
from services.mapper import UniversalMapper
from services.router import UniversalRouter
from services.ai_orchestrator import AIOrchestrator
from services.cost_converter import effort_to_inr
from services.currency_converter import convert_from_inr
from services.intake_cache import intake_context_store
from services.model_orchestrator import ModelOrchestrator
from services.state_manager import get_state
from schemas.request_response import (
    CostBreakdown,
    CostRange,
    DirectEstimateRequest,
    EstimatedEffort,
    FinalAssemblyRequest,
    FinalAssemblyResponse,
    FinalPredictionRequest,
    FinalPredictionResponse,
    IntakeFollowUpResponse,
    ModelPredictions,
    NormalizedUniversalProjectBrief,
    PublicIntakeResponse,
    RoleCostBreakdown,
    RouteInferenceMetadata,
    NormalizedUniversalPredictionRequest,
    PredictionRequest,
    PredictionResponse,
    TeamComposition,
    TechStack,
    UniversalPredictionRequest,
    normalize_universal_request,
)
from services.phase_distributor import distribute_phases
from services.risk_assessor import assess_risks
from services.explainability import generate_waterfall
from src.predictor import predict_cost

router = APIRouter()
universal_router = UniversalRouter()
universal_mapper = UniversalMapper()
ai_orchestrator = AIOrchestrator()
model_orchestrator = ModelOrchestrator()


def cache_intake_context(metadata: RouteInferenceMetadata, normalized_payload: NormalizedUniversalPredictionRequest) -> None:
    intake_context_store.cache_context(metadata, normalized_payload)


def get_intake_context(intake_id: str) -> tuple[RouteInferenceMetadata, NormalizedUniversalPredictionRequest]:
    try:
        metadata, payload = intake_context_store.get_context(intake_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="intake_id not found or expired")
    return metadata, payload


# ---------------------------------------------------------------------------
# Shared cost derivation helper (eliminates duplication)
# ---------------------------------------------------------------------------

def _build_prediction_response(
    *,
    intake_id: str,
    effort_months: float,
    confidence: float,
    assumptions: list[str],
    warnings: list[str],
    prediction_mode: str,
    target_currency: str,
    original_currency: str,
    monthly_rate_inr_override: float | None = None,
    team_composition: TeamComposition | None = None,
    model_predictions_data: dict | None = None,
    cost_range_data: dict | None = None,
    phase_breakdown_data: list | None = None,
    risk_assessment_data: list | None = None,
    explainability_data: list | None = None,
) -> FinalPredictionResponse:
    """Build the complete FinalPredictionResponse with cost derivation."""
    if team_composition and team_composition.roles:
        # Calculate blended rate based on role percentages
        total_pct = sum(role.percentage for role in team_composition.roles)
        if total_pct <= 0:
            monthly_rate_inr = monthly_rate_inr_override or get_state().monthly_rate_inr
        else:
            monthly_rate_inr = sum(
                (role.percentage / total_pct) * role.monthly_rate_inr
                for role in team_composition.roles
            )
    else:
        monthly_rate_inr = monthly_rate_inr_override or get_state().monthly_rate_inr

    base_cost_inr = effort_to_inr(effort_months, monthly_rate_inr)
    try:
        display_cost, exchange_rate = convert_from_inr(base_cost_inr, target_currency)
    except ValueError:
        # Unsupported currency – fall back to INR.
        target_currency = "INR"
        display_cost = base_cost_inr
        exchange_rate = 1.0
        warnings.append(
            f"Requested currency '{original_currency}' is not supported. Showing INR."
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
        monthly_rate_inr=round(monthly_rate_inr, 2),
        base_cost_inr=base_cost_inr,
        target_currency=target_currency,
        display_cost=display_cost,
        exchange_rate=exchange_rate,
    )

    role_breakdown = None
    if team_composition and team_composition.roles:
        total_pct = sum(role.percentage for role in team_composition.roles) or 100.0
        role_breakdown = []
        for role in team_composition.roles:
            pct = role.percentage / total_pct
            r_effort = effort_months * pct
            r_cost = r_effort * role.monthly_rate_inr
            role_breakdown.append(
                RoleCostBreakdown(
                    role_name=role.role_name,
                    percentage=round(pct * 100, 2),
                    monthly_rate_inr=role.monthly_rate_inr,
                    effort_months=round(r_effort, 2),
                    cost_inr=round(r_cost, 2),
                )
            )

    # Build model predictions and cost range if available (model mode only).
    model_predictions_obj = None
    cost_range_obj = None
    if model_predictions_data:
        model_predictions_obj = ModelPredictions(**model_predictions_data)
    if cost_range_data:
        cost_range_obj = CostRange(
            optimistic_cost_inr=round(cost_range_data["optimistic_effort"] * monthly_rate_inr, 2),
            most_likely_cost_inr=round(cost_range_data["most_likely_effort"] * monthly_rate_inr, 2),
            pessimistic_cost_inr=round(cost_range_data["pessimistic_effort"] * monthly_rate_inr, 2),
            optimistic_effort=cost_range_data["optimistic_effort"],
            most_likely_effort=cost_range_data["most_likely_effort"],
            pessimistic_effort=cost_range_data["pessimistic_effort"],
        )

    return FinalPredictionResponse(
        intake_id=intake_id,
        estimated_effort=estimated_effort,
        cost_breakdown=cost_breakdown,
        prediction_confidence=round(confidence, 4),
        assumptions=assumptions,
        warnings=warnings,
        model_predictions=model_predictions_obj,
        cost_range=cost_range_obj,
        role_breakdown=role_breakdown,
        phase_breakdown=phase_breakdown_data,
        risk_assessment=risk_assessment_data,
        explainability_waterfall=explainability_data,
    )


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

    runtime_mode = get_state().prediction_mode
    if runtime_mode == "ai":
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
        # --- Model mode (Phase 10) ---
        mapped_features, mapping_diagnostics = universal_mapper.assemble(
            route=metadata.detected_route,
            brief=brief,
            follow_up_answers=normalized_answers,
            unresolved_fields=unresolved_fields,
        )
        try:
            result = model_orchestrator.estimate_effort(
                route=metadata.detected_route.value,
                mapped_features=mapped_features,
                mapping_confidence=float(mapping_diagnostics.mapping_confidence),
                unresolved_fields=unresolved_fields,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        effort_months = result["effort_months"]
        confidence = result["confidence"]
        assumptions = result["assumptions"]
        warnings = result["warnings"]
        prediction_mode = "model"

    # Apply Tech Stack Multiplier
    stack_multipliers = {
        TechStack.web: 1.0,
        TechStack.mobile_cross: 1.15,
        TechStack.mobile_native: 1.35,
        TechStack.enterprise: 1.20,
        TechStack.ai_ml: 1.40,
        TechStack.embedded: 1.50,
    }
    multiplier = stack_multipliers.get(payload.tech_stack, 1.0)
    final_effort_months = effort_months * multiplier
    if multiplier != 1.0:
        assumptions.append(f"Applied {multiplier}x effort multiplier for {payload.tech_stack.value} stack.")

    blended_rate = payload.monthly_rate_inr or get_state().monthly_rate_inr

    # Apply Phase Distributor
    phase_breakdown = distribute_phases(
        effort_months=final_effort_months,
        monthly_rate_inr=blended_rate,
        complexity=original_payload.project_brief.complexity,
        reliability=original_payload.project_brief.reliability,
    )

    # Risk Assessment
    risks = assess_risks(
        complexity=original_payload.project_brief.complexity,
        reliability=original_payload.project_brief.reliability,
        base_effort=final_effort_months,
        monthly_rate_inr=blended_rate,
    )

    # Explainability Waterfall
    waterfall = generate_waterfall(
        base_ml_effort=effort_months,
        tech_stack=payload.tech_stack,
        multiplier=multiplier
    )

    return _build_prediction_response(
        intake_id=payload.intake_id,
        effort_months=final_effort_months,
        confidence=confidence,
        assumptions=assumptions,
        warnings=warnings,
        prediction_mode=prediction_mode,
        target_currency=payload.target_currency,
        original_currency=payload.target_currency,
        monthly_rate_inr_override=payload.monthly_rate_inr,
        team_composition=payload.team_composition,
        model_predictions_data=result.get("model_predictions") if prediction_mode == "model" else None,
        cost_range_data=result.get("cost_range") if prediction_mode == "model" else None,
        phase_breakdown_data=phase_breakdown,
        risk_assessment_data=risks,
        explainability_data=waterfall,
    )


@router.post(
    "/predict/estimate",
    response_model=FinalPredictionResponse,
    tags=["Estimation"],
    summary="Direct estimate — user selects dataset, always model mode",
    responses={
        422: {"description": "Invalid input values or follow-up answers"},
        500: {"description": "Model prediction error"},
    },
)
def predict_direct(payload: DirectEstimateRequest) -> FinalPredictionResponse:
    """
    Direct estimation endpoint (Phase 2 / Phase 3).

    The user selects the dataset explicitly from the UI. The backend:
    1. Skips UniversalRouter entirely.
    2. Normalises the project brief.
    3. Validates follow-up answers against the pack for the chosen dataset.
    4. Maps features via UniversalMapper.
    5. Runs the ML ensemble (model mode only — no AI API key required).
    6. Returns the same FinalPredictionResponse contract.
    """
    route = payload.dataset  # InternalRoute enum

    # --- Normalise brief ---
    normalized_brief = NormalizedUniversalProjectBrief(
        num_screens=int(payload.project_brief.num_screens),
        num_entities=int(payload.project_brief.num_entities),
        duration_months=round(float(payload.project_brief.duration_months), 4),
        team_experience_years=round(float(payload.project_brief.team_experience_years), 4),
        pm_experience_years=round(float(payload.project_brief.pm_experience_years), 4),
        complexity=payload.project_brief.complexity,
        reliability=payload.project_brief.reliability,
        team_size=int(payload.project_brief.team_size),
        project_notes=payload.project_brief.project_notes,
    )

    # --- Normalise follow-up answers against the pack for this dataset ---
    try:
        follow_up_pack = get_followup_pack_for_route(route)
        normalized_answers, unresolved_fields = normalize_followup_answers(
            follow_up_pack, payload.follow_up_answers
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # --- Map universal brief → dataset-specific feature vector ---
    mapped_features, mapping_diagnostics = universal_mapper.assemble(
        route=route,
        brief=normalized_brief,
        follow_up_answers=normalized_answers,
        unresolved_fields=unresolved_fields,
    )

    # --- ML ensemble (always model mode) ---
    try:
        result = model_orchestrator.estimate_effort(
            route=route.value,
            mapped_features=mapped_features,
            mapping_confidence=float(mapping_diagnostics.mapping_confidence),
            unresolved_fields=unresolved_fields,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply Tech Stack Multiplier
    stack_multipliers = {
        TechStack.web: 1.0,
        TechStack.mobile_cross: 1.15,
        TechStack.mobile_native: 1.35,
        TechStack.enterprise: 1.20,
        TechStack.ai_ml: 1.40,
        TechStack.embedded: 1.50,
    }
    multiplier = stack_multipliers.get(payload.tech_stack, 1.0)
    base_effort = result["effort_months"]
    final_effort_months = base_effort * multiplier
    if multiplier != 1.0:
        result["assumptions"].append(f"Applied {multiplier}x effort multiplier for {payload.tech_stack.value} stack.")

    blended_rate = payload.monthly_rate_inr or get_state().monthly_rate_inr

    # Apply Phase Distributor
    phase_breakdown = distribute_phases(
        effort_months=final_effort_months,
        monthly_rate_inr=blended_rate,
        complexity=payload.project_brief.complexity,
        reliability=payload.project_brief.reliability,
    )

    # Risk Assessment
    risks = assess_risks(
        complexity=payload.project_brief.complexity,
        reliability=payload.project_brief.reliability,
        base_effort=final_effort_months,
        monthly_rate_inr=blended_rate,
    )

    # Explainability Waterfall
    waterfall = generate_waterfall(
        base_ml_effort=base_effort,
        tech_stack=payload.tech_stack,
        multiplier=multiplier
    )

    return _build_prediction_response(
        intake_id=f"direct-{route.value}",
        effort_months=final_effort_months,
        confidence=result["confidence"],
        assumptions=result["assumptions"],
        warnings=result["warnings"],
        prediction_mode="model",
        target_currency=payload.target_currency,
        original_currency=payload.target_currency,
        monthly_rate_inr_override=payload.monthly_rate_inr,
        team_composition=payload.team_composition,
        model_predictions_data=result.get("model_predictions"),
        cost_range_data=result.get("cost_range"),
        phase_breakdown_data=phase_breakdown,
        risk_assessment_data=risks,
        explainability_data=waterfall,
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
