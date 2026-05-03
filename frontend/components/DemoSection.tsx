"use client";

import { FormEvent, useMemo, useState } from "react";

import {
  type FinalPredictionResponse,
  type FollowUpQuestionField,
  type FollowUpQuestionPack,
  type UniversalProjectBrief,
  submitFinal,
  submitIntake,
} from "../lib/api";

type ComplexityLevel = "low" | "medium" | "high";
type ReliabilityLevel = "low" | "medium" | "high";
type DemoStep = "brief" | "followup" | "result";

type BriefFormState = {
  numScreens: string;
  numEntities: string;
  durationMonths: string;
  teamExperienceYears: string;
  pmExperienceYears: string;
  teamSize: string;
  complexity: ComplexityLevel;
  reliability: ReliabilityLevel;
  projectNotes: string;
  targetCurrency: string;
};

type FollowUpValues = Record<string, string | boolean>;

const INITIAL_BRIEF_FORM: BriefFormState = {
  numScreens: "12",
  numEntities: "18",
  durationMonths: "7.5",
  teamExperienceYears: "4",
  pmExperienceYears: "6",
  teamSize: "6",
  complexity: "medium",
  reliability: "high",
  projectNotes: "",
  targetCurrency: "INR",
};

const DEMO_NOTES = [
  {
    label: "Two-step flow",
    value: "Stage 1 captures a universal brief. Stage 2 asks adaptive follow-up questions.",
  },
  {
    label: "Public contract",
    value: "The UI calls POST /predict/intake then POST /predict/final with no dataset selection.",
  },
  {
    label: "Result",
    value: "Returns effort, confidence, assumptions, warnings, and cost breakdown in your target currency.",
  },
];

const CURRENCY_OPTIONS = ["INR", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "SGD", "AED"];

function parseNumber(value: string, fieldLabel: string, minValue: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < minValue) {
    throw new Error(`${fieldLabel} must be at least ${minValue}.`);
  }
  return parsed;
}

function buildBriefPayload(form: BriefFormState): UniversalProjectBrief {
  const projectNotes = form.projectNotes.trim();
  return {
    num_screens: Math.round(parseNumber(form.numScreens, "Number of screens", 1)),
    num_entities: Math.round(parseNumber(form.numEntities, "Number of entities", 1)),
    duration_months: parseNumber(form.durationMonths, "Duration (months)", 0.1),
    team_experience_years: parseNumber(form.teamExperienceYears, "Team experience", 0),
    pm_experience_years: parseNumber(form.pmExperienceYears, "PM experience", 0),
    complexity: form.complexity,
    reliability: form.reliability,
    team_size: Math.round(parseNumber(form.teamSize, "Team size", 1)),
    ...(projectNotes ? { project_notes: projectNotes } : {}),
  };
}

function formatMoney(value: number, currency: string): string {
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(value);
  } catch {
    return `${value.toFixed(2)} ${currency}`;
  }
}

function initFollowUpValues(pack: FollowUpQuestionPack): FollowUpValues {
  const initial: FollowUpValues = {};
  for (const field of pack.fields) {
    if (field.input_type === "boolean") {
      initial[field.field_key] = false;
      continue;
    }
    if (field.input_type === "select") {
      initial[field.field_key] = field.options?.[0] ?? "";
      continue;
    }
    initial[field.field_key] = "";
  }
  return initial;
}

function normalizeFollowUpAnswers(
  pack: FollowUpQuestionPack,
  values: FollowUpValues,
): Record<string, string | number | boolean> {
  const normalized: Record<string, string | number | boolean> = {};

  for (const field of pack.fields) {
    const value = values[field.field_key];

    if (field.input_type === "boolean") {
      normalized[field.field_key] = Boolean(value);
      continue;
    }

    const raw = typeof value === "string" ? value.trim() : "";
    if (!raw) {
      if (field.required) {
        throw new Error(`${field.label} is required.`);
      }
      continue;
    }

    if (field.input_type === "integer") {
      const parsed = Number.parseInt(raw, 10);
      if (!Number.isFinite(parsed)) {
        throw new Error(`${field.label} must be an integer.`);
      }
      normalized[field.field_key] = parsed;
      continue;
    }

    if (field.input_type === "number") {
      const parsed = Number(raw);
      if (!Number.isFinite(parsed)) {
        throw new Error(`${field.label} must be a number.`);
      }
      normalized[field.field_key] = parsed;
      continue;
    }

    normalized[field.field_key] = raw;
  }

  return normalized;
}

function extractErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }
  return "Something went wrong while contacting the backend.";
}

export default function DemoSection() {
  const [step, setStep] = useState<DemoStep>("brief");
  const [briefForm, setBriefForm] = useState<BriefFormState>(INITIAL_BRIEF_FORM);
  const [intakeId, setIntakeId] = useState<string | null>(null);
  const [followUpPack, setFollowUpPack] = useState<FollowUpQuestionPack | null>(null);
  const [followUpValues, setFollowUpValues] = useState<FollowUpValues>({});
  const [result, setResult] = useState<FinalPredictionResponse | null>(null);
  const [isSubmittingBrief, setIsSubmittingBrief] = useState(false);
  const [isSubmittingFinal, setIsSubmittingFinal] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const confidencePercent = useMemo(() => {
    if (!result) {
      return null;
    }
    return `${Math.round(result.prediction_confidence * 100)}%`;
  }, [result]);

  async function handleBriefSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmittingBrief(true);

    try {
      const briefPayload = buildBriefPayload(briefForm);
      const intakeResponse = await submitIntake(briefPayload, briefForm.targetCurrency);
      setIntakeId(intakeResponse.intake_id);
      setFollowUpPack(intakeResponse.follow_up_pack);
      setFollowUpValues(initFollowUpValues(intakeResponse.follow_up_pack));
      setResult(null);
      setStep("followup");
    } catch (error) {
      setErrorMessage(extractErrorMessage(error));
    } finally {
      setIsSubmittingBrief(false);
    }
  }

  async function handleFinalSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);

    if (!intakeId || !followUpPack) {
      setErrorMessage("Missing intake context. Please restart the estimate flow.");
      setStep("brief");
      return;
    }

    setIsSubmittingFinal(true);
    try {
      const normalizedAnswers = normalizeFollowUpAnswers(followUpPack, followUpValues);
      const finalResponse = await submitFinal(intakeId, normalizedAnswers, briefForm.targetCurrency);
      setResult(finalResponse);
      setStep("result");
    } catch (error) {
      setErrorMessage(extractErrorMessage(error));
    } finally {
      setIsSubmittingFinal(false);
    }
  }

  function handleRestart(): void {
    setStep("brief");
    setIntakeId(null);
    setFollowUpPack(null);
    setFollowUpValues({});
    setResult(null);
    setErrorMessage(null);
  }

  function renderFollowUpField(field: FollowUpQuestionField) {
    const value = followUpValues[field.field_key];

    if (field.input_type === "select") {
      return (
        <select
          value={typeof value === "string" ? value : ""}
          onChange={(event) =>
            setFollowUpValues((current) => ({
              ...current,
              [field.field_key]: event.target.value,
            }))
          }
          className="w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground"
        >
          {(field.options ?? []).map((option: string) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      );
    }

    if (field.input_type === "boolean") {
      return (
        <label className="flex items-center gap-3 border border-line bg-background px-4 py-3">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(event) =>
              setFollowUpValues((current) => ({
                ...current,
                [field.field_key]: event.target.checked,
              }))
            }
            className="h-4 w-4"
          />
          <span className="text-sm text-muted">Enable</span>
        </label>
      );
    }

    const inputType = field.input_type === "text" ? "text" : "number";
    return (
      <input
        type={inputType}
        value={typeof value === "string" ? value : ""}
        onChange={(event) =>
          setFollowUpValues((current) => ({
            ...current,
            [field.field_key]: event.target.value,
          }))
        }
        min={field.min_value ?? undefined}
        max={field.max_value ?? undefined}
        step={field.step ?? (field.input_type === "integer" ? 1 : undefined)}
        placeholder={field.placeholder ?? undefined}
        className="w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground"
      />
    );
  }

  const displayCurrency = result?.cost_breakdown?.target_currency ?? briefForm.targetCurrency;
  const panelTitle = step === "brief" ? "Stage 1" : step === "followup" ? "Stage 2" : "Result";
  const panelSubtitle =
    step === "brief"
      ? "Submit universal project details"
      : step === "followup"
      ? "Answer adaptive follow-up questions"
      : "Effort and cost estimate";

  const summaryLines = [
    `Mode: ${result?.estimated_effort.prediction_mode ?? "pending"}`,
    result ? `Effort: ${result.estimated_effort.effort_months.toFixed(2)} person-months` : "Effort: awaiting final submission",
    result
      ? `Display cost: ${formatMoney(result.cost_breakdown?.display_cost ?? 0, displayCurrency)}`
      : "Display cost: awaiting final submission",
  ];

  const assumptions = result?.assumptions ?? [];
  const warnings = result?.warnings ?? [];
  const stageLabel = step === "brief" ? "1 / 2" : step === "followup" ? "2 / 2" : "Done";
  const isSubmitting = isSubmittingBrief || isSubmittingFinal;
  const shouldShowFollowup = step === "followup" && followUpPack !== null;
  const hasResult = result !== null;

  const nextStepCopy =
    step === "brief"
      ? "After Stage 1, the backend returns only the adaptive question pack needed for Stage 2."
      : step === "followup"
      ? "Submit Stage 2 to get effort, confidence, assumptions, warnings, and cost conversion."
      : "Restart to run another estimate with a new project brief.";

  const inputClass =
    "w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground";

  return (
    <section id="demo" className="section-wash border-b border-line/80">
      <div className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
        <div className="grid gap-14 lg:grid-cols-[1.02fr_0.98fr]">
          <div>
            <p className="editorial-kicker">Demo</p>
            <h2 className="mt-4 max-w-2xl font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
              Estimate cost through an adaptive two-step intake.
            </h2>
            <p className="mt-6 max-w-2xl text-base leading-8 text-muted sm:text-lg">
              Stage 1 captures a universal brief. Stage 2 adapts questions automatically, then returns effort and cost with assumptions and warnings.
            </p>

            <div className="mt-8 grid gap-px border border-line bg-line sm:grid-cols-3">
              {DEMO_NOTES.map((note) => (
                <div key={note.label} className="bg-background px-5 py-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted">{note.label}</p>
                  <p className="mt-3 text-sm leading-7 text-muted">{note.value}</p>
                </div>
              ))}
            </div>

            {step === "brief" ? (
              <form onSubmit={handleBriefSubmit} className="paper-panel mt-10 space-y-8 border border-line bg-card px-6 py-7 sm:px-8">
                <div className="grid gap-6 md:grid-cols-2">
                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Screens</span>
                    <input
                      type="number"
                      min="1"
                      value={briefForm.numScreens}
                      onChange={(event) => setBriefForm((current) => ({ ...current, numScreens: event.target.value }))}
                      className={inputClass}
                    />
                  </label>

                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Entities</span>
                    <input
                      type="number"
                      min="1"
                      value={briefForm.numEntities}
                      onChange={(event) => setBriefForm((current) => ({ ...current, numEntities: event.target.value }))}
                      className={inputClass}
                    />
                  </label>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Duration (months)</span>
                    <input
                      type="number"
                      min="0.1"
                      step="0.1"
                      value={briefForm.durationMonths}
                      onChange={(event) => setBriefForm((current) => ({ ...current, durationMonths: event.target.value }))}
                      className={inputClass}
                    />
                  </label>

                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Team size</span>
                    <input
                      type="number"
                      min="1"
                      value={briefForm.teamSize}
                      onChange={(event) => setBriefForm((current) => ({ ...current, teamSize: event.target.value }))}
                      className={inputClass}
                    />
                  </label>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Team experience (years)</span>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      value={briefForm.teamExperienceYears}
                      onChange={(event) => setBriefForm((current) => ({ ...current, teamExperienceYears: event.target.value }))}
                      className={inputClass}
                    />
                  </label>

                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">PM experience (years)</span>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      value={briefForm.pmExperienceYears}
                      onChange={(event) => setBriefForm((current) => ({ ...current, pmExperienceYears: event.target.value }))}
                      className={inputClass}
                    />
                  </label>
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Complexity</span>
                    <select
                      value={briefForm.complexity}
                      onChange={(event) =>
                        setBriefForm((current) => ({
                          ...current,
                          complexity: event.target.value as ComplexityLevel,
                        }))
                      }
                      className={inputClass}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </label>

                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Reliability</span>
                    <select
                      value={briefForm.reliability}
                      onChange={(event) =>
                        setBriefForm((current) => ({
                          ...current,
                          reliability: event.target.value as ReliabilityLevel,
                        }))
                      }
                      className={inputClass}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </label>

                  <label className="space-y-3">
                    <span className="text-sm uppercase tracking-[0.18em] text-muted">Target currency</span>
                    <select
                      value={briefForm.targetCurrency}
                      onChange={(event) =>
                        setBriefForm((current) => ({
                          ...current,
                          targetCurrency: event.target.value,
                        }))
                      }
                      className={inputClass}
                    >
                      {CURRENCY_OPTIONS.map((currency) => (
                        <option key={currency} value={currency}>
                          {currency}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <label className="block space-y-3">
                  <span className="text-sm uppercase tracking-[0.18em] text-muted">Project notes (optional)</span>
                  <textarea
                    value={briefForm.projectNotes}
                    onChange={(event) =>
                      setBriefForm((current) => ({
                        ...current,
                        projectNotes: event.target.value,
                      }))
                    }
                    className="min-h-[120px] w-full border border-line bg-background px-4 py-3 text-base text-foreground outline-none transition-colors focus:border-foreground"
                    placeholder="Scope boundaries, integration constraints, or delivery assumptions"
                  />
                </label>

                <div className="flex flex-wrap items-center gap-4">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="border border-foreground bg-foreground px-6 py-3 text-sm uppercase tracking-[0.18em] text-background transition-colors hover:border-accent hover:bg-accent disabled:cursor-not-allowed disabled:border-line disabled:bg-line disabled:text-muted"
                  >
                    {isSubmittingBrief ? "Submitting..." : "Continue to Stage 2"}
                  </button>
                  <p className="text-sm leading-7 text-muted">Stage 1 of 2</p>
                </div>
              </form>
            ) : null}

            {shouldShowFollowup ? (
              <form onSubmit={handleFinalSubmit} className="paper-panel mt-10 space-y-8 border border-line bg-card px-6 py-7 sm:px-8">
                <div className="border border-line bg-background/90 px-4 py-4 text-sm leading-7 text-muted">
                  <p className="font-medium uppercase tracking-[0.18em] text-foreground">{followUpPack.title}</p>
                  {followUpPack.description ? <p className="mt-2">{followUpPack.description}</p> : null}
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  {followUpPack.fields.map((field: FollowUpQuestionField) => (
                    <label key={field.field_key} className="space-y-3">
                      <span className="text-sm uppercase tracking-[0.18em] text-muted">
                        {field.label}
                        {field.required ? " *" : ""}
                      </span>
                      {renderFollowUpField(field)}
                      {field.help_text ? <span className="block text-xs leading-6 text-muted">{field.help_text}</span> : null}
                    </label>
                  ))}
                </div>

                <div className="flex flex-wrap items-center gap-4">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="border border-foreground bg-foreground px-6 py-3 text-sm uppercase tracking-[0.18em] text-background transition-colors hover:border-accent hover:bg-accent disabled:cursor-not-allowed disabled:border-line disabled:bg-line disabled:text-muted"
                  >
                    {isSubmittingFinal ? "Estimating..." : "Get Final Estimate"}
                  </button>
                  <button
                    type="button"
                    onClick={handleRestart}
                    className="border border-line bg-background px-6 py-3 text-sm uppercase tracking-[0.18em] text-foreground transition-colors hover:border-foreground"
                  >
                    Start Over
                  </button>
                  <p className="text-sm leading-7 text-muted">Stage 2 of 2</p>
                </div>
              </form>
            ) : null}

            {errorMessage ? (
              <div className="mt-10 border border-[#b94735] bg-[#fff0eb] px-4 py-3 text-sm leading-7 text-[#8f3528]">
                {errorMessage}
              </div>
            ) : null}
          </div>

          <div className="space-y-6">
            <div className="paper-panel border border-line bg-card px-6 py-7 sm:px-8">
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line/80 pb-6">
                <div>
                  <p className="editorial-kicker">{panelTitle}</p>
                  <h3 className="mt-3 font-serif text-3xl tracking-editorial text-foreground">{panelSubtitle}</h3>
                </div>
                <div className="border border-line bg-background/90 px-4 py-3 text-right">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Progress</p>
                  <p className="mt-2 font-serif text-2xl text-foreground">{stageLabel}</p>
                </div>
              </div>

              <div className="mt-8 space-y-6">
                <div className="border border-line bg-background/90 px-5 py-5">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Workflow note</p>
                  <p className="mt-4 text-sm leading-7 text-muted">{nextStepCopy}</p>
                </div>

                <div className="space-y-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Live summary</p>
                  {summaryLines.map((line) => (
                    <div key={line} className="border border-line bg-background/80 px-4 py-3 text-sm text-muted">
                      {line}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="paper-panel border border-line bg-card px-6 py-7 sm:px-8">
              <p className="editorial-kicker">Estimate</p>
              {hasResult ? (
                <div className="mt-5 space-y-5">
                  <div className="border border-line bg-background/90 px-5 py-5">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Effort</p>
                    <p className="mt-3 font-serif text-4xl tracking-editorial text-foreground">
                      {result.estimated_effort.effort_months.toFixed(2)} PM
                    </p>
                    <p className="mt-3 text-sm leading-7 text-muted">Confidence: {confidencePercent}</p>
                    <p className="mt-2 text-sm leading-7 text-muted">Prediction mode: {result.estimated_effort.prediction_mode}</p>
                  </div>

                  <div className="border border-line bg-background/90 px-5 py-5">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Cost breakdown</p>
                    {result.cost_breakdown ? (
                      <>
                        <p className="mt-3 text-sm leading-7 text-muted">
                          Display cost: {formatMoney(result.cost_breakdown.display_cost, displayCurrency)}
                        </p>
                        <p className="text-sm leading-7 text-muted">
                          Base INR: {formatMoney(result.cost_breakdown.base_cost_inr, "INR")}
                        </p>
                        <p className="text-sm leading-7 text-muted">
                          Monthly INR rate: {formatMoney(result.cost_breakdown.monthly_rate_inr, "INR")}
                        </p>
                        <p className="text-sm leading-7 text-muted">
                          Exchange rate: {result.cost_breakdown.exchange_rate.toFixed(4)}
                        </p>
                      </>
                    ) : (
                      <p className="mt-3 text-sm leading-7 text-muted">No cost analysis included.</p>
                    )}
                  </div>

                  <div className="space-y-3">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Assumptions</p>
                    {assumptions.length > 0 ? (
                      assumptions.map((item: string) => (
                        <div key={item} className="border border-line bg-background/80 px-4 py-3 text-sm text-muted">
                          {item}
                        </div>
                      ))
                    ) : (
                      <div className="border border-line bg-background/80 px-4 py-3 text-sm text-muted">No assumptions returned.</div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Warnings</p>
                    {warnings.length > 0 ? (
                      warnings.map((item: string) => (
                        <div key={item} className="border border-line bg-[#fff0eb] px-4 py-3 text-sm text-[#8f3528]">
                          {item}
                        </div>
                      ))
                    ) : (
                      <div className="border border-line bg-background/80 px-4 py-3 text-sm text-muted">No warnings returned.</div>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={handleRestart}
                    className="border border-line bg-background px-6 py-3 text-sm uppercase tracking-[0.18em] text-foreground transition-colors hover:border-foreground"
                  >
                    Run Another Estimate
                  </button>
                </div>
              ) : (
                <div className="mt-5 border border-dashed border-line bg-background/90 px-5 py-10">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Awaiting estimate</p>
                  <p className="mt-4 max-w-lg font-serif text-3xl tracking-editorial text-foreground">
                    Complete Stage 1 and Stage 2 to receive effort and cost output.
                  </p>
                  <p className="mt-5 max-w-lg text-sm leading-7 text-muted">
                    The final panel includes prediction mode, confidence, assumptions, warnings, and full currency-aware cost details.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
