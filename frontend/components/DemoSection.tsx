"use client";

import { FormEvent, useEffect, useState } from "react";

import { DatasetCode, PredictCostResponse, getDatasets, predictCost } from "@/lib/api";

type ReliabilityLevel = "Low" | "Nominal" | "High" | "Very High";

type DemoFormState = {
  kloc: string;
  complexity: number;
  teamExperience: number;
  reliability: ReliabilityLevel;
};

type DatasetMeta = {
  label: string;
  shortLabel: string;
  note: string;
  proxyFields: string[];
};

const FALLBACK_DATASETS: DatasetCode[] = ["china", "cocomo81", "desharnais"];
const RELIABILITY_OPTIONS: ReliabilityLevel[] = ["Low", "Nominal", "High", "Very High"];
const INITIAL_FORM: DemoFormState = {
  kloc: "25",
  complexity: 3,
  teamExperience: 3,
  reliability: "Nominal",
};

const DATASET_META: Record<DatasetCode, DatasetMeta> = {
  china: {
    label: "China Dataset",
    shortLabel: "China",
    note: "Maps the compact form to AFP, transaction volume, change volume, staffing, and duration proxies.",
    proxyFields: ["AFP", "Input", "Output", "Added", "Changed", "Resource", "Duration"],
  },
  cocomo81: {
    label: "COCOMO-81 Dataset",
    shortLabel: "COCOMO-81",
    note: "Maps directly into classic COCOMO cost-driver fields such as LOC, reliability, complexity, and analyst capability.",
    proxyFields: ["loc", "rely", "cplx", "acap", "aexp", "tool"],
  },
  desharnais: {
    label: "Desharnais Dataset",
    shortLabel: "Desharnais",
    note: "Translates the form into size, team experience, transaction count, entity count, and adjustment proxies.",
    proxyFields: ["Length", "TeamExp", "ManagerExp", "Transactions", "Entities", "PointsNonAdjust"],
  },
};

const DEMO_NOTES = [
  {
    label: "Live service",
    value: "Fetches datasets from /datasets and sends prediction requests to /predict.",
  },
  {
    label: "Input method",
    value: "A compact brief is translated into dataset-aware proxy features before submission.",
  },
];

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function parseKloc(value: string): number | null {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }
  return parsed;
}

function extractErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }
  return "Something went wrong while contacting the backend.";
}

function getReliabilityRank(level: ReliabilityLevel): number {
  return RELIABILITY_OPTIONS.indexOf(level) + 1;
}

function formatModelName(modelName: string): string {
  const knownNames: Record<string, string> = {
    RandomForest: "Random Forest",
    XGBoost: "XGBoost",
    LinearRegression: "Linear Regression",
  };
  return knownNames[modelName] ?? modelName;
}

function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

function buildFeaturePayload(dataset: DatasetCode, form: DemoFormState): Record<string, number> {
  const kloc = parseKloc(form.kloc) ?? 0;
  const complexity = clamp(form.complexity, 1, 5);
  const teamExperience = clamp(form.teamExperience, 1, 5);
  const reliabilityRank = getReliabilityRank(form.reliability);

  if (dataset === "cocomo81") {
    const capabilityScale = [1.29, 1.13, 1.0, 0.91, 0.82];
    const experienceScale = [1.22, 1.1, 1.0, 0.88, 0.81];
    const complexityScale = [0.7, 0.85, 1.0, 1.15, 1.3];
    const reliabilityScale: Record<ReliabilityLevel, number> = {
      Low: 0.88,
      Nominal: 1.0,
      High: 1.15,
      "Very High": 1.4,
    };

    return {
      loc: Math.max(1, Math.round(kloc)),
      cplx: complexityScale[complexity - 1],
      rely: reliabilityScale[form.reliability],
      acap: capabilityScale[teamExperience - 1],
      aexp: experienceScale[teamExperience - 1],
      tool: teamExperience >= 4 ? 0.91 : teamExperience <= 2 ? 1.1 : 1.0,
    };
  }

  if (dataset === "desharnais") {
    return {
      Length: Math.max(1, Math.round(kloc / 3)),
      TeamExp: teamExperience,
      ManagerExp: Math.max(0, teamExperience - 1),
      Transactions: Math.max(10, Math.round(kloc * (6 + complexity * 2))),
      Entities: Math.max(5, Math.round(kloc * (1.5 + reliabilityRank * 0.7))),
      PointsNonAdjust: Math.max(20, Math.round(kloc * (8 + complexity * 1.8))),
      Adjustment: clamp(Math.round(20 + complexity * 4 + reliabilityRank * 3), 10, 60),
      Language: reliabilityRank >= 4 ? 3 : reliabilityRank >= 3 ? 2 : 1,
    };
  }

  return {
    AFP: Math.max(20, Math.round(kloc * 12)),
    Input: Math.max(5, Math.round(kloc * (2 + complexity))),
    Output: Math.max(5, Math.round(kloc * (1.5 + reliabilityRank))),
    Enquiry: Math.max(1, Math.round(kloc * (0.8 + complexity * 0.6))),
    File: Math.max(1, Math.round(kloc * 0.9)),
    Interface: Math.max(0, Math.round((reliabilityRank - 1) * 6)),
    Added: Math.max(5, Math.round(kloc * (3 + complexity))),
    Changed: Math.max(2, Math.round(kloc * (1.5 + complexity))),
    Deleted: Math.max(0, Math.round(kloc * (reliabilityRank - 0.5))),
    Resource: teamExperience <= 2 ? 1 : teamExperience === 3 ? 2 : 4,
    "Dev.Type": 0,
    Duration: Math.max(1, Math.round(kloc / 4 + complexity + reliabilityRank)),
  };
}

export default function DemoSection() {
  const [datasets, setDatasets] = useState<DatasetCode[]>([]);
  const [dataset, setDataset] = useState<DatasetCode>(FALLBACK_DATASETS[0]);
  const [formState, setFormState] = useState<DemoFormState>(INITIAL_FORM);
  const [prediction, setPrediction] = useState<PredictCostResponse | null>(null);
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [datasetNotice, setDatasetNotice] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadDatasetOptions() {
      try {
        const apiDatasets = await getDatasets();
        if (!isMounted) {
          return;
        }

        const supportedDatasets = apiDatasets.filter((item): item is DatasetCode => item in DATASET_META);
        const resolvedDatasets = supportedDatasets.length > 0 ? supportedDatasets : FALLBACK_DATASETS;
        setDatasets(resolvedDatasets);
        setDataset((current) => (resolvedDatasets.includes(current) ? current : resolvedDatasets[0]));
        setDatasetNotice("Live dataset list loaded from the backend.");
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setDatasets(FALLBACK_DATASETS);
        setDataset(FALLBACK_DATASETS[0]);
        setDatasetNotice("Could not load /datasets. Using the known project datasets instead.");
        setErrorMessage(extractErrorMessage(error));
      } finally {
        if (isMounted) {
          setIsLoadingDatasets(false);
        }
      }
    }

    loadDatasetOptions();

    return () => {
      isMounted = false;
    };
  }, []);

  const datasetMeta = DATASET_META[dataset];
  const comparisonRows = prediction
    ? [
        { label: "Random Forest", value: prediction.rf_prediction },
        { label: "XGBoost", value: prediction.xgb_prediction },
        { label: "Linear Regression", value: prediction.lr_prediction },
        { label: "Ensemble", value: prediction.ensemble_prediction },
      ]
    : [];
  const maxMagnitude = comparisonRows.reduce((currentMax, row) => Math.max(currentMax, Math.abs(row.value)), 0) || 1;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);

    const parsedKloc = parseKloc(formState.kloc);
    if (parsedKloc === null) {
      setPrediction(null);
      setErrorMessage("KLOC must be a positive number.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await predictCost({
        dataset,
        features: buildFeaturePayload(dataset, { ...formState, kloc: String(parsedKloc) }),
      });
      setPrediction(response);
    } catch (error) {
      setPrediction(null);
      setErrorMessage(extractErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section id="demo" className="section-wash border-b border-line/80">
      <div className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
        <div className="grid gap-14 lg:grid-cols-[1.02fr_0.98fr]">
          <div>
            <p className="editorial-kicker">Demo</p>
            <h2 className="mt-4 max-w-2xl font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
              Estimate cost from a compact project brief.
            </h2>
            <p className="mt-6 max-w-2xl text-base leading-8 text-muted sm:text-lg">
              The demo keeps the interaction simple, then translates each input into the nearest valid feature payload for the selected backend dataset.
            </p>

            <div className="mt-8 grid gap-px border border-line bg-line sm:grid-cols-2">
              {DEMO_NOTES.map((note) => (
                <div key={note.label} className="bg-background px-5 py-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted">{note.label}</p>
                  <p className="mt-3 text-sm leading-7 text-muted">{note.value}</p>
                </div>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="paper-panel mt-10 space-y-8 border border-line bg-card px-6 py-7 sm:px-8">
              <div className="grid gap-6 md:grid-cols-2">
                <label className="space-y-3">
                  <span className="text-sm uppercase tracking-[0.18em] text-muted">Dataset</span>
                  <select
                    value={dataset}
                    onChange={(event) => setDataset(event.target.value as DatasetCode)}
                    disabled={isLoadingDatasets}
                    className="w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground disabled:cursor-not-allowed disabled:bg-card"
                  >
                    {(datasets.length > 0 ? datasets : FALLBACK_DATASETS).map((item) => (
                      <option key={item} value={item}>
                        {DATASET_META[item].label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="space-y-3">
                  <span className="text-sm uppercase tracking-[0.18em] text-muted">Reliability</span>
                  <select
                    value={formState.reliability}
                    onChange={(event) =>
                      setFormState((current) => ({
                        ...current,
                        reliability: event.target.value as ReliabilityLevel,
                      }))
                    }
                    className="w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground"
                  >
                    {RELIABILITY_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="block space-y-3">
                <span className="text-sm uppercase tracking-[0.18em] text-muted">KLOC</span>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={formState.kloc}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      kloc: event.target.value,
                    }))
                  }
                  className="w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground"
                  placeholder="Enter project size in KLOC"
                />
              </label>

              <div className="grid gap-6 md:grid-cols-2">
                <label className="space-y-4">
                  <div className="flex items-center justify-between gap-4 text-sm uppercase tracking-[0.18em] text-muted">
                    <span>Complexity</span>
                    <span className="text-foreground">{formState.complexity}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="1"
                    value={formState.complexity}
                    onChange={(event) =>
                      setFormState((current) => ({
                        ...current,
                        complexity: Number(event.target.value),
                      }))
                    }
                    className="w-full"
                  />
                </label>

                <label className="space-y-4">
                  <div className="flex items-center justify-between gap-4 text-sm uppercase tracking-[0.18em] text-muted">
                    <span>Team Experience</span>
                    <span className="text-foreground">{formState.teamExperience}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="1"
                    value={formState.teamExperience}
                    onChange={(event) =>
                      setFormState((current) => ({
                        ...current,
                        teamExperience: Number(event.target.value),
                      }))
                    }
                    className="w-full"
                  />
                </label>
              </div>

              <div className="border border-line bg-background/90 px-4 py-4 text-sm leading-7 text-muted">
                <p className="font-medium uppercase tracking-[0.18em] text-foreground">Selected mapping</p>
                <p className="mt-2">{datasetMeta.note}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.18em] text-muted">
                  Backend fields: {datasetMeta.proxyFields.join(" · ")}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <button
                  type="submit"
                  disabled={isSubmitting || isLoadingDatasets}
                  className="border border-foreground bg-foreground px-6 py-3 text-sm uppercase tracking-[0.18em] text-background transition-colors hover:border-accent hover:bg-accent disabled:cursor-not-allowed disabled:border-line disabled:bg-line disabled:text-muted"
                >
                  {isSubmitting ? "Predicting..." : "Predict Cost"}
                </button>
                <p className="text-sm leading-7 text-muted">
                  {isLoadingDatasets ? "Loading datasets from the backend..." : datasetNotice}
                </p>
              </div>

              {errorMessage ? (
                <div className="border border-[#b94735] bg-[#fff0eb] px-4 py-3 text-sm leading-7 text-[#8f3528]">
                  {errorMessage}
                </div>
              ) : null}
            </form>
          </div>

          <div className="space-y-6">
            <div className="paper-panel border border-line bg-card px-6 py-7 sm:px-8">
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line/80 pb-6">
                <div>
                  <p className="editorial-kicker">Result</p>
                  <h3 className="mt-3 font-serif text-3xl tracking-editorial text-foreground">{datasetMeta.shortLabel}</h3>
                </div>
                {prediction ? (
                  <div className="border border-line bg-background/90 px-4 py-3 text-right">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Best model</p>
                    <p className="mt-2 font-serif text-2xl text-foreground">{formatModelName(prediction.best_model)}</p>
                  </div>
                ) : null}
              </div>

              {prediction ? (
                <div className="mt-8 space-y-6">
                  <div className="border border-line bg-background/90 px-5 py-5">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Predicted cost</p>
                    <p className="mt-4 font-serif text-5xl tracking-editorial text-foreground">
                      {formatCurrency(prediction.ensemble_prediction)}
                    </p>
                    <p className="mt-4 max-w-md text-sm leading-7 text-muted">
                      Ensemble prediction is used as the headline estimate while the full model comparison remains visible below.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <p className="text-xs uppercase tracking-[0.2em] text-muted">Model comparison</p>
                      <p className="text-xs uppercase tracking-[0.2em] text-muted">Absolute width scale</p>
                    </div>

                    {comparisonRows.map((row) => {
                      const width = `${Math.max(10, Math.round((Math.abs(row.value) / maxMagnitude) * 100))}%`;
                      const isEnsemble = row.label === "Ensemble";
                      return (
                        <div key={row.label} className="space-y-2">
                          <div className="flex items-center justify-between gap-4 text-sm">
                            <span className="text-foreground">{row.label}</span>
                            <span className="font-medium text-muted">{formatCurrency(row.value)}</span>
                          </div>
                          <div className="h-3 border border-line bg-background/80">
                            <div
                              className={isEnsemble ? "h-full bg-foreground" : "h-full bg-accent"}
                              style={{ width }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="mt-8 border border-dashed border-line bg-background/90 px-5 py-10">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Awaiting estimate</p>
                  <p className="mt-4 max-w-lg font-serif text-3xl tracking-editorial text-foreground">
                    Submit the form to load a live ensemble prediction from the FastAPI backend.
                  </p>
                  <p className="mt-5 max-w-lg text-sm leading-7 text-muted">
                    The response panel will show the ensemble estimate, the recommended best model, and the per-model comparison bars.
                  </p>
                </div>
              )}
            </div>

            <div className="paper-panel border border-line bg-card px-6 py-7 sm:px-8">
              <p className="editorial-kicker">Insight</p>
              <div className="mt-5 border border-line bg-background/90 px-5 py-5">
                <p className="text-base leading-8 text-muted">
                  {prediction?.insight ?? "The backend insight will appear here after a successful prediction request."}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}