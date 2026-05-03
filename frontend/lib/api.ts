export type DatasetCode = "china" | "cocomo81" | "desharnais";

export type ComplexityLevel = "low" | "medium" | "high";
export type ReliabilityLevel = "low" | "medium" | "high";

export type TechStack = "web" | "mobile_cross" | "mobile_native" | "enterprise" | "ai_ml" | "embedded";

export type UniversalProjectBrief = {
  num_screens: number;
  num_entities: number;
  duration_months: number;
  team_experience_years: number;
  pm_experience_years: number;
  complexity: ComplexityLevel;
  reliability: ReliabilityLevel;
  team_size: number;
  project_notes?: string;
};

export type UniversalPredictRequest = {
  project_brief: UniversalProjectBrief;
  target_currency?: string;
  version?: number;
};

export type NormalizedUniversalPredictRequest = {
  project_brief: UniversalProjectBrief & {
    project_notes?: string | null;
  };
  target_currency: string;
  version: number;
};

export type IntakeInferenceResponse = {
  intake_id: string;
  follow_up_pack_id: string;
  intake_version: number;
  next_step: string;
};

// Phase 7 / Phase 8 public types ─────────────────────────────────────────────

export type PublicIntakeResponse = {
  intake_id: string;
  follow_up_pack: FollowUpQuestionPack;
  intake_version: number;
  next_step: string;
};

export type EstimatedEffort = {
  effort_months: number;
  confidence: number;
  assumptions: string[];
  warnings: string[];
  prediction_mode: string;
};

export type CostBreakdown = {
  effort_months: number;
  monthly_rate_inr: number;
  base_cost_inr: number;
  target_currency: string;
  display_cost: number;
  exchange_rate: number;
};

export type TeamRole = {
  role_name: string;
  percentage: number;
  monthly_rate_inr: number;
};

export type TeamComposition = {
  roles: TeamRole[];
};

export type RoleCostBreakdown = {
  role_name: string;
  percentage: number;
  monthly_rate_inr: number;
  effort_months: number;
  cost_inr: number;
};

export type PhaseBreakdown = {
  phase_name: string;
  percentage: number;
  effort_months: number;
  cost_inr: number | null;
};

export type RiskFactor = {
  risk_name: string;
  impact_level: "High" | "Medium" | "Low";
  probability: "High" | "Medium" | "Low";
  mitigation: string;
  potential_cost_impact_inr: number | null;
};

export type ExplainabilityStep = {
  step_name: string;
  effort_change_months: number;
  is_base: boolean;
  description: string;
};

export type ModelPredictions = {
  random_forest: number;
  xgboost: number;
  linear_regression: number;
  ensemble: number;
  best_model: string;
};

export type CostRange = {
  optimistic_cost_inr: number;
  most_likely_cost_inr: number;
  pessimistic_cost_inr: number;
  optimistic_effort: number;
  most_likely_effort: number;
  pessimistic_effort: number;
};

export type FinalPredictionResponse = {
  intake_id: string;
  estimated_effort: EstimatedEffort;
  cost_breakdown: CostBreakdown | null;
  prediction_confidence: number;
  assumptions: string[];
  warnings: string[];
  model_predictions: ModelPredictions | null;
  cost_range: CostRange | null;
  role_breakdown: RoleCostBreakdown[] | null;
  phase_breakdown: PhaseBreakdown[] | null;
  risk_assessment: RiskFactor[] | null;
  explainability_waterfall: ExplainabilityStep[] | null;
};

export type FollowUpInputType = "integer" | "number" | "select" | "text" | "boolean";

export type FollowUpQuestionField = {
  field_key: string;
  label: string;
  input_type: FollowUpInputType;
  required: boolean;
  help_text?: string | null;
  placeholder?: string | null;
  min_value?: number | null;
  max_value?: number | null;
  step?: number | null;
  options?: string[] | null;
};

export type FollowUpQuestionPack = {
  pack_id: string;
  version: number;
  title: string;
  description?: string | null;
  fields: FollowUpQuestionField[];
};

export type IntakeFollowUpResponse = {
  intake_id: string;
  follow_up_pack: FollowUpQuestionPack;
  next_step: string;
};

export type FinalAssemblyRequest = {
  intake_id: string;
  follow_up_answers: Record<string, string | number | boolean>;
};

export type MappingDiagnostics = {
  internal_route: "china" | "cocomo81" | "desharnais";
  mapping_confidence: number;
  mapping_rationale: string[];
  unresolved_fields: string[];
};

export type FinalAssemblyResponse = {
  intake_id: string;
  mapped_features: Record<string, number>;
  mapping_diagnostics: MappingDiagnostics;
};

export type PredictCostRequest = {
  dataset: DatasetCode;
  features: Record<string, number | string>;
};

export type PredictCostResponse = {
  rf_prediction: number;
  xgb_prediction: number;
  lr_prediction: number;
  ensemble_prediction: number;
  best_model: string;
  insight: string;
};

type DatasetsResponse = {
  datasets: string[];
};

type ApiErrorPayload = {
  detail?: string;
  message?: string;
  error_code?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json().catch(() => null)) as T | ApiErrorPayload | null;

  if (!response.ok) {
    const errPayload = payload as ApiErrorPayload | null;
    const message =
      errPayload?.message ??
      errPayload?.detail ??
      `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  if (payload === null) {
    throw new Error("The API returned an empty response.");
  }

  return payload as T;
}

export async function getDatasets(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/datasets`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  const payload = await parseResponse<DatasetsResponse>(response);
  return payload.datasets;
}

export async function predictCost(request: PredictCostRequest): Promise<PredictCostResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });

  return parseResponse<PredictCostResponse>(response);
}

export async function normalizeUniversalPayload(
  request: UniversalPredictRequest,
): Promise<NormalizedUniversalPredictRequest> {
  const response = await fetch(`${API_BASE_URL}/predict/universal/normalize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });

  return parseResponse<NormalizedUniversalPredictRequest>(response);
}

export async function inferIntakeRoute(request: UniversalPredictRequest): Promise<IntakeInferenceResponse> {
  const response = await fetch(`${API_BASE_URL}/predict/intake`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });

  return parseResponse<IntakeInferenceResponse>(response);
}

export async function getFollowUpQuestions(intakeId: string): Promise<IntakeFollowUpResponse> {
  const response = await fetch(`${API_BASE_URL}/predict/followup/${encodeURIComponent(intakeId)}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  return parseResponse<IntakeFollowUpResponse>(response);
}

export async function assembleFinalInputs(request: FinalAssemblyRequest): Promise<FinalAssemblyResponse> {
  const response = await fetch(`${API_BASE_URL}/predict/final/assemble`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });

  return parseResponse<FinalAssemblyResponse>(response);
}

// Phase 8 public two-step API ─────────────────────────────────────────────────

export async function submitIntake(
  brief: UniversalProjectBrief,
  targetCurrency = "INR",
): Promise<PublicIntakeResponse> {
  const response = await fetch(`${API_BASE_URL}/predict/intake`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ project_brief: brief, target_currency: targetCurrency }),
  });
  return parseResponse<PublicIntakeResponse>(response);
}

export async function submitFinal(
  intakeId: string,
  followUpAnswers: Record<string, string | number | boolean>,
  targetCurrency = "INR",
  profileId?: string,
): Promise<FinalPredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict/final`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      intake_id: intakeId,
      follow_up_answers: followUpAnswers,
      target_currency: targetCurrency,
      ...(profileId ? { profile_id: profileId } : {}),
    }),
  });
  return parseResponse<FinalPredictionResponse>(response);
}

// Phase 2 / Phase 3 — direct dataset-aware estimation (model mode only) ───────

export type DatasetKey = "cocomo81" | "desharnais" | "china";

export type DirectEstimatePayload = {
  dataset: DatasetKey;
  project_brief: UniversalProjectBrief;
  follow_up_answers: Record<string, string | number | boolean>;
  target_currency?: string;
  monthly_rate_inr?: number;
  team_composition?: TeamComposition;
  tech_stack?: TechStack;
  include_cost_analysis?: boolean;
};

export async function submitDirectEstimate(
  payload: DirectEstimatePayload,
): Promise<FinalPredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict/estimate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
  });
  return parseResponse<FinalPredictionResponse>(response);
}

// Phase 4 — Chatbot ───────────────────────────────────────────────────────────

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type EstimationContext = {
  dataset: string;
  effort_months: number;
  confidence: number;
  prediction_mode: string;
  display_cost: number;
  target_currency: string;
  base_cost_inr: number;
  monthly_rate_inr: number;
  exchange_rate: number;
  assumptions: string[];
  warnings: string[];
};

export type ChatRequest = {
  message: string;
  context: EstimationContext;
  history: ChatMessage[];
};

export type ChatResponse = {
  reply: string;
  history: ChatMessage[];
};

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(request),
  });
  return parseResponse<ChatResponse>(response);
}

