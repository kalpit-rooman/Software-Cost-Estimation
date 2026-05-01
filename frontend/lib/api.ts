export type DatasetCode = "china" | "cocomo81" | "desharnais";

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