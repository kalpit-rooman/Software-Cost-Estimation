export type DatasetCode = "china" | "cocomo81" | "desharnais";

export type ComplexityLevel = "low" | "medium" | "high";
export type ReliabilityLevel = "low" | "medium" | "high";

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
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json().catch(() => null)) as T | ApiErrorPayload | null;

  if (!response.ok) {
    const message = payload && typeof (payload as ApiErrorPayload).detail === "string"
      ? (payload as ApiErrorPayload).detail
      : `Request failed with status ${response.status}`;
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