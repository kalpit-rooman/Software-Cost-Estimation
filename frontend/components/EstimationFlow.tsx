"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import Step1ProjectType from "@/components/estimation/Step1ProjectType";
import Step2CoreInputs from "@/components/estimation/Step2CoreInputs";
import Step3AdvancedInputs from "@/components/estimation/Step3AdvancedInputs";
import type { AdvancedInputs, CoreInputs, ProjectType } from "@/components/estimation/types";
import {
  type DatasetKey,
  type DirectEstimatePayload,
  submitDirectEstimate,
} from "@/lib/api";

type FlowStep = 1 | 2 | 3;
type ComplexityLabel = "low" | "medium" | "high";
type ReliabilityLabel = "low" | "medium" | "high";

const PROJECT_TYPES: ProjectType[] = [
  {
    id: "large-code-system",
    title: "Large Code System",
    description: "Infrastructure-heavy and code-intensive platforms.",
    dataset: "cocomo81",
  },
  {
    id: "business-application",
    title: "Business Application",
    description: "Workflow-driven apps for business operations.",
    dataset: "desharnais",
  },
  {
    id: "medium-enterprise-system",
    title: "Medium Enterprise System",
    description: "Balanced enterprise products with integrations.",
    dataset: "china",
  },
];

const INITIAL_CORE: CoreInputs = {
  projectSize: 120,
  teamExperience: 6,
  complexity: 5,
};

const INITIAL_ADVANCED: AdvancedInputs = {
  reliabilityRequirement: "medium",
  dataIntensity: "medium",
  teamFamiliarity: "some_experience",
  timeConstraint: "moderate",
  toolingMaturity: "stable",
  monthlySalary: 150000,
};

function asComplexityLabel(score: number): ComplexityLabel {
  if (score <= 3) return "low";
  if (score <= 7) return "medium";
  return "high";
}

function asReliabilityLabel(value: AdvancedInputs["reliabilityRequirement"]): ReliabilityLabel {
  return value;
}

function clampNumber(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);
}

function extractError(error: unknown): string {
  if (error instanceof Error && error.message.trim()) return error.message;
  return "Could not complete the estimate. Check whether the backend is running.";
}

function buildFollowUpAnswers(
  dataset: DatasetKey,
  core: CoreInputs,
  advanced: AdvancedInputs,
): Record<string, string | number | boolean> {
  const RELY = { low: 0.9, medium: 1.0, high: 1.15 }[advanced.reliabilityRequirement];
  const DATA = { low: 0.85, medium: 1.0, high: 1.15 }[advanced.dataIntensity];
  const TOOL = { experimental: 1.15, stable: 1.0, optimized: 0.88 }[advanced.toolingMaturity];
  const TIME = { flexible: 0.9, moderate: 1.0, tight: 1.12 }[advanced.timeConstraint];
  const TEAM = { new: 1.12, some_experience: 1.0, expert: 0.86 }[advanced.teamFamiliarity];

  if (dataset === "cocomo81") {
    const estimatedKloc = clampNumber((core.projectSize * DATA * RELY) / 2.5, 0.1, 1000);
    const platformConstraintLevel =
      advanced.timeConstraint === "tight"
        ? "tight"
        : advanced.timeConstraint === "flexible"
          ? "relaxed"
          : "nominal";
    const toolingMaturity =
      advanced.toolingMaturity === "optimized"
        ? "high"
        : advanced.toolingMaturity === "experimental"
          ? "low"
          : "medium";
    const scheduleCompression =
      advanced.timeConstraint === "tight"
        ? "high"
        : advanced.timeConstraint === "flexible"
          ? "low"
          : "medium";

    return {
      estimated_kloc: Number(estimatedKloc.toFixed(2)),
      platform_constraint_level: platformConstraintLevel,
      tooling_maturity: toolingMaturity,
      schedule_compression: scheduleCompression,
    };
  }

  if (dataset === "desharnais") {
    const processCount = clampNumber(Math.round((core.projectSize / 3.5) * DATA), 1, 2000);
    const changeRequests = clampNumber(
      Math.round((core.complexity * 14 * TIME * RELY) / TEAM),
      0,
      20000,
    );
    const dataComplexity = clampNumber(core.complexity * DATA * RELY, 1, 10);
    const teamDistribution =
      advanced.teamFamiliarity === "expert"
        ? "co_located"
        : advanced.teamFamiliarity === "new"
          ? "distributed"
          : "hybrid";

    return {
      business_process_count: processCount,
      expected_change_requests: changeRequests,
      data_complexity_index: Number(dataComplexity.toFixed(1)),
      team_distribution: teamDistribution,
    };
  }

  const transactionVolume = clampNumber(Math.round(core.projectSize * 220 * DATA), 1, 1000000);
  const changeRequestVolume = clampNumber(
    Math.round((core.complexity * 16 * TIME * RELY) / TEAM),
    0,
    20000,
  );
  const integrationPoints = clampNumber(Math.round((core.complexity * 1.8 + core.projectSize / 30) * DATA), 0, 1000);
  const expectedReusePercent = clampNumber(Math.round((1 / TOOL) * 25 + (advanced.teamFamiliarity === "expert" ? 10 : 0)), 0, 100);

  return {
    transaction_volume: transactionVolume,
    change_request_volume: changeRequestVolume,
    integration_points: integrationPoints,
    expected_reuse_percent: expectedReusePercent,
  };
}

function buildPayload(
  dataset: DatasetKey,
  core: CoreInputs,
  advanced: AdvancedInputs,
): DirectEstimatePayload {
  const teamSize = clampNumber(Math.round(3 + core.projectSize / 26), 2, 40);
  const baseDuration = 4 + core.complexity * 1.2;
  const durationMultiplier =
    advanced.timeConstraint === "tight" ? 0.85 : advanced.timeConstraint === "flexible" ? 1.2 : 1;

  return {
    dataset,
    target_currency: "INR",
    monthly_rate_inr: advanced.monthlySalary,
    project_brief: {
      num_screens: clampNumber(Math.round(core.projectSize * 0.65), 1, 10000),
      num_entities: clampNumber(Math.round(core.projectSize * 0.48), 1, 10000),
      duration_months: Number(clampNumber(baseDuration * durationMultiplier, 1, 60).toFixed(1)),
      team_experience_years: Number(clampNumber(core.teamExperience, 0, 30).toFixed(1)),
      pm_experience_years: Number(clampNumber(core.teamExperience + 1.5, 0, 30).toFixed(1)),
      complexity: asComplexityLabel(core.complexity),
      reliability: asReliabilityLabel(advanced.reliabilityRequirement),
      team_size: teamSize,
      project_notes: "Estimate generated from simplified multi-step UI.",
    },
    follow_up_answers: buildFollowUpAnswers(dataset, core, advanced),
  };
}

export default function EstimationFlow() {
  const router = useRouter();
  const [step, setStep] = useState<FlowStep>(1);
  const [projectTypeId, setProjectTypeId] = useState<ProjectType["id"] | null>(null);
  const [coreInputs, setCoreInputs] = useState<CoreInputs>(INITIAL_CORE);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [advancedInputs, setAdvancedInputs] = useState<AdvancedInputs>(INITIAL_ADVANCED);
  const [isEstimating, setIsEstimating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedProjectType = useMemo(
    () => PROJECT_TYPES.find((option) => option.id === projectTypeId) ?? null,
    [projectTypeId],
  );

  const stepLabel = `Step ${step} / 3`;

  function nextStep(): void {
    if (step === 1 && !projectTypeId) return;
    setStep((current) => (current < 3 ? ((current + 1) as FlowStep) : current));
  }

  function prevStep(): void {
    setStep((current) => (current > 1 ? ((current - 1) as FlowStep) : current));
  }

  async function estimateCost(): Promise<void> {
    if (!selectedProjectType || isEstimating) return;

    setError(null);
    setIsEstimating(true);

    try {
      const payload = buildPayload(
        selectedProjectType.dataset,
        coreInputs,
        showAdvanced ? advancedInputs : INITIAL_ADVANCED,
      );

      const response = await submitDirectEstimate(payload);
      sessionStorage.setItem(
        "estimation_result",
        JSON.stringify({ result: response, dataset: selectedProjectType.dataset }),
      );
      router.push("/estimate/results");
    } catch (estimateError) {
      setError(extractError(estimateError));
    } finally {
      setIsEstimating(false);
    }
  }

  return (
    <section className="min-h-screen bg-background px-4 py-20 sm:px-6">
      <div className="mx-auto max-w-2xl space-y-8">
        <header className="space-y-4 rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">Software Cost Estimator</p>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">Answer a few simple questions and get an estimate</h1>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm text-muted">
              <span>{stepLabel}</span>
              <span>{Math.round((step / 3) * 100)}%</span>
            </div>
            <div className="h-2 rounded-full bg-background">
              <div
                className="h-2 rounded-full bg-primary transition-all duration-300"
                style={{ width: `${(step / 3) * 100}%` }}
              />
            </div>
          </div>
        </header>

        <div className="space-y-8">
          {step === 1 && (
            <Step1ProjectType
              options={PROJECT_TYPES}
              selectedId={projectTypeId}
              onSelect={setProjectTypeId}
            />
          )}

          {step === 2 && (
            <Step2CoreInputs
              values={coreInputs}
              onChange={setCoreInputs}
            />
          )}

          {step === 3 && (
            <div className="space-y-6">
              <Step3AdvancedInputs
                showAdvanced={showAdvanced}
                onToggleAdvanced={setShowAdvanced}
                values={advancedInputs}
                onChange={setAdvancedInputs}
              />

              <section className="rounded-2xl border border-line/60 bg-card p-5 shadow-sm">
                <h3 className="text-base font-semibold text-foreground">Step 4: Prediction</h3>
                <p className="mt-1 text-sm text-muted">Ready when you are. We will convert your answers into model inputs and run the estimation.</p>

                <button
                  type="button"
                  onClick={estimateCost}
                  disabled={isEstimating || !selectedProjectType}
                  className="btn-primary mt-4 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isEstimating ? "Estimating…" : "Get Estimate →"}
                </button>

                {error && (
                  <p className="mt-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
                )}
              </section>
            </div>
          )}
        </div>

        <footer className="flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={prevStep}
            disabled={step === 1}
            className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60"
          >
            Back
          </button>
          <button
            type="button"
            onClick={nextStep}
            disabled={(step === 1 && !projectTypeId) || step === 3}
            className="btn-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
            Next
          </button>
        </footer>
      </div>
    </section>
  );
}
