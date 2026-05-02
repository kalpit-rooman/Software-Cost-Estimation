from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_currency_code(value: Any) -> str:
    """Shared currency normalisation used by multiple request models."""
    if value is None:
        return "INR"
    if not isinstance(value, str):
        raise TypeError("target_currency must be a string")
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError("target_currency must be a 3-letter alphabetic currency code")
    return normalized


class ComplexityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ReliabilityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class UniversalProjectBrief(BaseModel):
    num_screens: int = Field(..., ge=1, le=5000)
    num_entities: int = Field(..., ge=1, le=10000)
    duration_months: float = Field(..., gt=0.0, le=120.0)
    team_experience_years: float = Field(..., ge=0.0, le=50.0)
    pm_experience_years: float = Field(..., ge=0.0, le=50.0)
    complexity: ComplexityLevel
    reliability: ReliabilityLevel
    team_size: int = Field(..., ge=1, le=1000)
    project_notes: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("project_notes", mode="before")
    @classmethod
    def normalize_project_notes(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value


class UniversalPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_brief: UniversalProjectBrief
    target_currency: str = Field(default="INR", min_length=3, max_length=3)
    version: int = Field(default=1, ge=1, le=10)

    @field_validator("target_currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: Any) -> str:
        return _normalize_currency_code(value)


class NormalizedUniversalProjectBrief(BaseModel):
    num_screens: int
    num_entities: int
    duration_months: float
    team_experience_years: float
    pm_experience_years: float
    complexity: ComplexityLevel
    reliability: ReliabilityLevel
    team_size: int
    project_notes: str | None = None


class NormalizedUniversalPredictionRequest(BaseModel):
    project_brief: NormalizedUniversalProjectBrief
    target_currency: str
    version: int


class InternalRoute(str, Enum):
    china = "china"
    cocomo81 = "cocomo81"
    desharnais = "desharnais"


class RouteInferenceMetadata(BaseModel):
    intake_id: str
    detected_route: InternalRoute
    follow_up_pack_id: str
    routing_confidence: float = Field(..., ge=0.0, le=1.0)
    routing_rationale: list[str] = Field(default_factory=list)
    route_scores: dict[str, float] = Field(default_factory=dict)


class IntakeInferenceResponse(BaseModel):
    intake_id: str
    follow_up_pack_id: str
    intake_version: int
    next_step: str = "collect_followup_inputs"


class FollowUpInputType(str, Enum):
    integer = "integer"
    number = "number"
    select = "select"
    text = "text"
    boolean = "boolean"


class FollowUpQuestionField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_key: str = Field(..., min_length=2, max_length=100)
    label: str = Field(..., min_length=2, max_length=120)
    input_type: FollowUpInputType
    required: bool = True
    help_text: str | None = Field(default=None, max_length=280)
    placeholder: str | None = Field(default=None, max_length=120)
    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None
    options: list[str] | None = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str] | None, info: Any) -> list[str] | None:
        input_type = info.data.get("input_type") if isinstance(info.data, dict) else None
        if input_type == FollowUpInputType.select:
            if not value:
                raise ValueError("options are required when input_type is select")
            return value
        if value is not None:
            raise ValueError("options are only allowed for select input_type")
        return value


class FollowUpQuestionPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pack_id: str
    version: int = Field(default=1, ge=1, le=10)
    title: str = Field(default="Additional project details", min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=300)
    fields: list[FollowUpQuestionField] = Field(default_factory=list)


class IntakeFollowUpResponse(BaseModel):
    intake_id: str
    follow_up_pack: FollowUpQuestionPack
    next_step: str = "submit_followup_answers"


class FinalAssemblyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intake_id: str
    follow_up_answers: dict[str, Any] = Field(default_factory=dict)


class MappingDiagnostics(BaseModel):
    internal_route: InternalRoute
    mapping_confidence: float = Field(..., ge=0.0, le=1.0)
    mapping_rationale: list[str] = Field(default_factory=list)
    unresolved_fields: list[str] = Field(default_factory=list)


class FinalAssemblyResponse(BaseModel):
    intake_id: str
    mapped_features: dict[str, float] = Field(default_factory=dict)
    mapping_diagnostics: MappingDiagnostics


def normalize_universal_request(payload: UniversalPredictionRequest) -> NormalizedUniversalPredictionRequest:
    brief = payload.project_brief
    return NormalizedUniversalPredictionRequest(
        project_brief=NormalizedUniversalProjectBrief(
            num_screens=int(brief.num_screens),
            num_entities=int(brief.num_entities),
            duration_months=round(float(brief.duration_months), 4),
            team_experience_years=round(float(brief.team_experience_years), 4),
            pm_experience_years=round(float(brief.pm_experience_years), 4),
            complexity=brief.complexity,
            reliability=brief.reliability,
            team_size=int(brief.team_size),
            project_notes=brief.project_notes,
        ),
        target_currency=payload.target_currency,
        version=int(payload.version),
    )


# ---------------------------------------------------------------------------
# Phase 5 – AI estimation result
# ---------------------------------------------------------------------------


class EstimatedEffort(BaseModel):
    """Internal effort estimation output (from AI or model orchestrator)."""

    effort_months: float = Field(..., gt=0.0, le=600.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    prediction_mode: str = Field(default="model")  # "ai" | "model"


# ---------------------------------------------------------------------------
# Phase 6 – Cost breakdown and public prediction response
# ---------------------------------------------------------------------------


class CostBreakdown(BaseModel):
    """Effort-to-cost derivation, always traceable back to INR."""

    effort_months: float
    monthly_rate_inr: float
    base_cost_inr: float
    target_currency: str
    display_cost: float
    exchange_rate: float


class ModelPredictions(BaseModel):
    """Individual model predictions for transparency."""

    random_forest: float
    xgboost: float
    linear_regression: float
    ensemble: float
    best_model: str


class CostRange(BaseModel):
    """Optimistic / most-likely / pessimistic cost envelope."""

    optimistic_cost_inr: float
    most_likely_cost_inr: float
    pessimistic_cost_inr: float
    optimistic_effort: float
    most_likely_effort: float
    pessimistic_effort: float


class FinalPredictionResponse(BaseModel):
    """Public response for POST /predict/final."""

    intake_id: str
    estimated_effort: EstimatedEffort
    cost_breakdown: CostBreakdown
    prediction_confidence: float = Field(..., ge=0.0, le=1.0)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    model_predictions: ModelPredictions | None = None
    cost_range: CostRange | None = None


# ---------------------------------------------------------------------------
# Phase 7 – Consolidated public contract
# ---------------------------------------------------------------------------


class PublicIntakeResponse(BaseModel):
    """
    Public response for POST /predict/intake.

    Returns the adaptive follow-up question pack inline so the frontend
    only needs two API calls: POST /predict/intake then POST /predict/final.
    No dataset names or internal routing metadata are exposed.
    """

    intake_id: str
    follow_up_pack: FollowUpQuestionPack
    intake_version: int
    next_step: str = "submit_followup_answers"


class PublicErrorResponse(BaseModel):
    """Standardised error envelope used by all public endpoints."""

    error_code: str
    message: str
    field: str | None = None


class FinalPredictionRequest(BaseModel):
    """Public request for POST /predict/final (Stage 1 + Stage 2 combined)."""

    model_config = ConfigDict(extra="forbid")

    intake_id: str
    follow_up_answers: dict[str, Any] = Field(default_factory=dict)
    target_currency: str = Field(default="INR", min_length=3, max_length=3)
    profile_id: str | None = Field(default=None)  # prompt profile override
    monthly_rate_inr: float | None = Field(default=None, ge=10000, le=5000000)

    @field_validator("target_currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: Any) -> str:
        return _normalize_currency_code(value)


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


class DirectEstimateRequest(BaseModel):
    """Public request for POST /predict/estimate.

    The user explicitly selects the dataset. The backend skips the
    UniversalRouter and always uses model mode — no API key required.
    """

    model_config = ConfigDict(extra="forbid")

    dataset: InternalRoute  # "cocomo81" | "desharnais" | "china"
    project_brief: UniversalProjectBrief
    follow_up_answers: dict[str, Any] = Field(default_factory=dict)
    target_currency: str = Field(default="INR", min_length=3, max_length=3)
    monthly_rate_inr: float | None = Field(default=None, ge=10000, le=5000000)

    @field_validator("target_currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: Any) -> str:
        return _normalize_currency_code(value)


# ---------------------------------------------------------------------------
# Phase 4 – Chatbot schemas
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    """A single turn in the conversation history."""

    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=8000)


class EstimationContext(BaseModel):
    """Serialised estimation result sent from the frontend to seed the chatbot."""

    dataset: str  # e.g. "cocomo81"
    effort_months: float
    confidence: float
    prediction_mode: str
    display_cost: float
    target_currency: str
    base_cost_inr: float
    monthly_rate_inr: float
    exchange_rate: float
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., min_length=1, max_length=2000)
    context: EstimationContext
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str
    history: list[ChatMessage]

