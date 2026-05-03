"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Brain, Calendar, ChartBar, ChartPieSlice, CurrencyInr, FloppyDisk, Function, Info, Printer, ShieldWarning, Users, UsersThree } from "@phosphor-icons/react";
import ChatPanel from "./ChatPanel";
import type { CostRange, DatasetKey, EstimationContext, ExplainabilityStep, FinalPredictionResponse, ModelPredictions, PhaseBreakdown, RiskFactor, RoleCostBreakdown } from "@/lib/api";

// ── Loading animation config ──────────────────────────────────────────────────

const LOADING_STEPS = [
  "Analyzing project parameters...",
  "Computing cost using ML models...",
  "Running ensemble model...",
  "Aggregating predictions...",
  "Optimizing estimation...",
];

const CHAR_MS = 28;
const STEP_PAUSE_MS = 220;
const FINAL_PAUSE_MS = 600;

// ── Chatbot suggested questions ───────────────────────────────────────────────

const SUGGESTED_QUESTIONS = [
  "Explain me the results",
  "Breakdown the costs",
  "What will be the total cost in INR?",
  "If we use AI tools, how can we reduce the development time?",
  "How much should I pay the developers based on their experience?",
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

/** Convert raw person-months into a plain-English duration + team breakdown. */
function humanizeEffort(effortMonths: number): {
  duration: string;
  teamCard: { size: number; months: string }[];
  raw: string;
} {
  const rounded = Math.round(effortMonths * 10) / 10;
  const raw = `${rounded} person-months`;

  // Duration at different realistic team sizes
  const teamSizes = [3, 5, 8, 12];
  const teamCard = teamSizes.map((size) => {
    const months = effortMonths / size;
    const yrs = Math.floor(months / 12);
    const mos = Math.round(months % 12);
    let label = "";
    if (yrs > 0 && mos > 0) label = `${yrs}y ${mos}m`;
    else if (yrs > 0) label = `${yrs} year${yrs > 1 ? "s" : ""}`;
    else label = `${mos} month${mos !== 1 ? "s" : ""}`;
    return { size, months: label };
  });

  // Human duration summary at team of 5
  const atFive = effortMonths / 5;
  const yrs = Math.floor(atFive / 12);
  const mos = Math.round(atFive % 12);
  let duration = "";
  if (yrs > 0 && mos > 0) duration = `${yrs} year${yrs > 1 ? "s" : ""} and ${mos} month${mos !== 1 ? "s" : ""}`;
  else if (yrs > 0) duration = `${yrs} year${yrs > 1 ? "s" : ""}`;
  else duration = `${mos} month${mos !== 1 ? "s" : ""}`;

  return { duration, teamCard, raw };
}

type StoredEstimation = {
  result: FinalPredictionResponse;
  dataset: DatasetKey;
};

// ── Sub-components ────────────────────────────────────────────────────────────

function CostRangeCard({ costRange }: { costRange: CostRange }) {
  const opt = costRange.optimistic_cost_inr;
  const likely = costRange.most_likely_cost_inr;
  const pess = costRange.pessimistic_cost_inr;
  const total = pess - opt || 1;
  const likelyPct = Math.max(2, Math.min(98, ((likely - opt) / total) * 100));

  return (
    <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
      <div className="flex items-start gap-4">
        <span className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-700">
          <ChartBar size={26} weight="duotone" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">
            Cost Confidence Range
          </p>
          <p className="mt-1 text-sm text-muted">
            Based on the spread across Random Forest, XGBoost, and Linear Regression models
          </p>

          {/* Range bar */}
          <div className="relative mt-5 mb-8">
            <div className="h-3 w-full rounded-full bg-gradient-to-r from-emerald-200 via-amber-200 to-rose-200" />

            {/* Optimistic marker */}
            <div className="absolute top-0 flex flex-col items-center" style={{ left: "0%" }}>
              <div className="h-3 w-0.5 bg-emerald-600" />
              <div className="mt-1.5 whitespace-nowrap text-center">
                <p className="text-[10px] font-semibold text-emerald-700">Optimistic</p>
                <p className="text-xs font-semibold text-foreground">{formatINR(opt)}</p>
                <p className="text-[10px] text-muted">{costRange.optimistic_effort} PM</p>
              </div>
            </div>

            {/* Most likely marker */}
            <div className="absolute top-0 flex flex-col items-center -translate-x-1/2" style={{ left: `${likelyPct}%` }}>
              <div className="h-5 w-1 rounded-full bg-foreground -mt-1" />
              <div className="mt-1.5 whitespace-nowrap text-center">
                <p className="text-[10px] font-semibold text-amber-700">Most Likely</p>
                <p className="text-sm font-bold text-foreground">{formatINR(likely)}</p>
                <p className="text-[10px] text-muted">{costRange.most_likely_effort} PM</p>
              </div>
            </div>

            {/* Pessimistic marker */}
            <div className="absolute top-0 flex flex-col items-center" style={{ right: "0%" }}>
              <div className="h-3 w-0.5 bg-rose-600" />
              <div className="mt-1.5 whitespace-nowrap text-center">
                <p className="text-[10px] font-semibold text-rose-700">Pessimistic</p>
                <p className="text-xs font-semibold text-foreground">{formatINR(pess)}</p>
                <p className="text-[10px] text-muted">{costRange.pessimistic_effort} PM</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModelComparisonCard({
  predictions,
  monthlyRate,
}: {
  predictions: ModelPredictions;
  monthlyRate: number | null;
}) {
  const showCost = monthlyRate !== null && monthlyRate > 0;
  const models = [
    { key: "random_forest", label: "Random Forest", effort: predictions.random_forest },
    { key: "xgboost", label: "XGBoost", effort: predictions.xgboost },
    { key: "linear_regression", label: "Linear Regression", effort: predictions.linear_regression },
    { key: "ensemble", label: "Ensemble (used)", effort: predictions.ensemble },
  ];

  return (
    <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-700">
          <ChartBar size={20} weight="duotone" />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">Model Comparison</p>
          <p className="text-xs text-muted">
            Ensemble combines all models using inverse-RMSE weighting
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-line/50">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line/40 bg-background">
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Model
              </th>
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Effort (PM)
              </th>
              {showCost && (
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Cost (INR)
              </th>
              )}
            </tr>
          </thead>
          <tbody>
            {models.map((model) => {
              const isBest = model.key === predictions.best_model.toLowerCase().replace(/\s+/g, "_")
                || (model.key === "random_forest" && predictions.best_model === "RandomForest")
                || (model.key === "xgboost" && predictions.best_model === "XGBoost")
                || (model.key === "linear_regression" && predictions.best_model === "LinearRegression");
              const isEnsemble = model.key === "ensemble";

              return (
                <tr
                  key={model.key}
                  className={`border-b border-line/30 last:border-b-0 ${
                    isEnsemble
                      ? "bg-primary/5 font-semibold"
                      : isBest
                        ? "bg-emerald-50/50"
                        : ""
                  }`}
                >
                  <td className="px-4 py-2.5 text-foreground">
                    <span className="flex items-center gap-2">
                      {model.label}
                      {isBest && !isEnsemble && (
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
                          Best
                        </span>
                      )}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right text-foreground tabular-nums">
                    {model.effort.toFixed(1)}
                  </td>
                  {showCost && (
                  <td className="px-4 py-2.5 text-right text-foreground tabular-nums">
                    {formatINR(model.effort * (monthlyRate ?? 0))}
                  </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RoleBreakdownCard({
  roles,
  totalCost,
}: {
  roles: RoleCostBreakdown[];
  totalCost: number;
}) {

  return (
    <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-orange-50 text-orange-700">
          <Users size={20} weight="duotone" />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">Team Role Breakdown</p>
          <p className="text-xs text-muted">
            Cost distribution based on specified team composition
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-line/50">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line/40 bg-background">
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Role
              </th>
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Allocation
              </th>
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted hidden sm:table-cell">
                Rate (mo)
              </th>
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Cost
              </th>
            </tr>
          </thead>
          <tbody>
            {roles.map((role, idx) => (
              <tr key={idx} className="border-b border-line/30 last:border-b-0">
                <td className="px-4 py-2.5 text-foreground">{role.role_name}</td>
                <td className="px-4 py-2.5 text-right text-foreground">
                  <span className="inline-flex items-center gap-1.5">
                    {role.percentage}%
                    <span className="text-muted text-xs">({role.effort_months.toFixed(1)} PM)</span>
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right text-muted tabular-nums hidden sm:table-cell">
                  {formatINR(role.monthly_rate_inr)}
                </td>
                <td className="px-4 py-2.5 text-right text-foreground tabular-nums font-medium">
                  {formatINR(role.cost_inr)}
                </td>
              </tr>
            ))}
            <tr className="bg-muted/5 font-semibold border-t-2 border-line/50">
              <td colSpan={3} className="px-4 py-3 text-right">Total:</td>
              <td className="px-4 py-3 text-right tabular-nums text-primary">{formatINR(totalCost)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PhaseBreakdownCard({ phases }: { phases: PhaseBreakdown[] }) {
  const colors = ["bg-emerald-400", "bg-blue-400", "bg-indigo-400", "bg-violet-400", "bg-pink-400", "bg-rose-400"];
  const showCost = phases.length > 0 && phases[0].cost_inr !== null;

  return (
    <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700">
          <ChartPieSlice size={20} weight="duotone" />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">SDLC Phase Breakdown</p>
          <p className="text-xs text-muted">
            Estimated effort and cost distribution across project lifecycle
          </p>
        </div>
      </div>

      {/* Stacked Bar Chart */}
      <div className="mb-6 flex h-4 w-full overflow-hidden rounded-full">
        {phases.map((phase, idx) => (
          <div
            key={idx}
            style={{ width: `${phase.percentage}%` }}
            className={`h-full ${colors[idx % colors.length]}`}
            title={`${phase.phase_name}: ${phase.percentage}%`}
          />
        ))}
      </div>

      <div className="overflow-hidden rounded-xl border border-line/50">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line/40 bg-background">
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Phase
              </th>
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Effort (PM)
              </th>
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted hidden sm:table-cell">
                %
              </th>
              {showCost && (
              <th className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                Cost
              </th>
              )}
            </tr>
          </thead>
          <tbody>
            {phases.map((phase, idx) => (
              <tr key={idx} className="border-b border-line/30 last:border-b-0">
                <td className="px-4 py-2.5 text-foreground flex items-center gap-2">
                  <div className={`h-2 w-2 rounded-full ${colors[idx % colors.length]}`} />
                  {phase.phase_name}
                </td>
                <td className="px-4 py-2.5 text-right text-foreground tabular-nums">
                  {phase.effort_months.toFixed(1)}
                </td>
                <td className="px-4 py-2.5 text-right text-muted tabular-nums hidden sm:table-cell">
                  {phase.percentage}%
                </td>
                {showCost && (
                <td className="px-4 py-2.5 text-right text-foreground tabular-nums">
                  {formatINR(phase.cost_inr ?? 0)}
                </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RiskAssessmentCard({ risks }: { risks: RiskFactor[] }) {
  return (
    <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-rose-50 text-rose-700">
          <ShieldWarning size={20} weight="duotone" />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">Project Risk Assessment</p>
          <p className="text-xs text-muted">
            Identified risk factors and their potential financial impact
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {risks.map((risk, idx) => (
          <div key={idx} className="rounded-xl border border-line/40 bg-background p-4">
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-sm font-bold text-foreground">{risk.risk_name}</h4>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                risk.impact_level === "High" ? "bg-rose-100 text-rose-700" :
                risk.impact_level === "Medium" ? "bg-amber-100 text-amber-700" :
                "bg-emerald-100 text-emerald-700"
              }`}>
                {risk.impact_level} Impact
              </span>
            </div>
            <p className="text-xs text-muted mb-3 line-clamp-2" title={risk.mitigation}>
              <span className="font-semibold">Mitigation:</span> {risk.mitigation}
            </p>
            {risk.potential_cost_impact_inr !== null && (
            <div className="flex items-center justify-between mt-auto border-t border-line/30 pt-2">
              <span className="text-[10px] text-muted uppercase tracking-widest">Potential Cost</span>
              <span className="text-sm font-bold text-foreground tabular-nums">
                + {formatINR(risk.potential_cost_impact_inr)}
              </span>
            </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ExplainabilityWaterfallCard({ steps }: { steps: ExplainabilityStep[] }) {
  const totalEffort = steps.reduce((sum, step) => sum + step.effort_change_months, 0);

  return (
    <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700">
          <Function size={20} weight="duotone" />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">Effort Explainability (Waterfall)</p>
          <p className="text-xs text-muted">
            Step-by-step breakdown of how the final effort was calculated
          </p>
        </div>
      </div>

      <div className="space-y-3 relative before:absolute before:inset-y-4 before:left-4 before:w-0.5 before:bg-line/40">
        {steps.map((step, idx) => (
          <div key={idx} className="relative flex items-center gap-4 pl-10">
            <div className={`absolute left-2.5 h-3 w-3 rounded-full border-2 border-background shadow-sm ${
              step.is_base ? "bg-blue-500" : "bg-emerald-500"
            }`} />
            
            <div className="flex-1 rounded-xl border border-line/40 bg-background p-3 flex justify-between items-center">
              <div>
                <p className="text-sm font-bold text-foreground">{step.step_name}</p>
                <p className="text-xs text-muted">{step.description}</p>
              </div>
              <div className={`text-sm font-bold tabular-nums whitespace-nowrap pl-4 ${
                step.is_base ? "text-foreground" : "text-emerald-600"
              }`}>
                {step.is_base ? "" : "+ "}{step.effort_change_months.toFixed(1)} PM
              </div>
            </div>
          </div>
        ))}

        {/* Total line */}
        <div className="relative flex items-center gap-4 pl-10 pt-2">
           <div className="absolute left-2.5 h-3 w-3 rounded-full border-2 border-background bg-foreground shadow-sm" />
           <div className="flex-1 rounded-xl border-2 border-line/80 bg-muted/5 p-3 flex justify-between items-center">
              <p className="text-sm font-bold text-foreground uppercase tracking-widest">Final Effort</p>
              <div className="text-lg font-black tabular-nums text-foreground">
                {totalEffort.toFixed(1)} PM
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function ResultsPage() {
  const router = useRouter();

  // Phase
  const [phase, setPhase] = useState<"loading" | "results">("loading");

  // Loading animation state
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [currentTyped, setCurrentTyped] = useState("");
  const [stored, setStored] = useState<StoredEstimation | null>(null);
  const [savedScenarios, setSavedScenarios] = useState<Array<{ name: string; date: string; result: FinalPredictionResponse }>>([]);
  const [showSaveInput, setShowSaveInput] = useState(false);
  const [scenarioName, setScenarioName] = useState("");
  const barRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("estimation_result");
    if (!raw) {
      router.replace("/estimate");
      return;
    }
    try {
      const data = JSON.parse(raw) as StoredEstimation;
      setStored(data);
      const scenarios = localStorage.getItem("software_cost_scenarios");
      if (scenarios) setSavedScenarios(JSON.parse(scenarios));
    } catch {
      router.replace("/estimate");
    }
  }, [router]);

  // ── Kick off progress bar CSS animation ──────────────────────────────────
  useEffect(() => {
    if (phase !== "loading") return;
    // total expected duration ≈ LOADING_STEPS chars * CHAR_MS + step pauses + final pause
    const totalChars = LOADING_STEPS.reduce((s, t) => s + t.length, 0);
    const totalMs =
      totalChars * CHAR_MS +
      LOADING_STEPS.length * STEP_PAUSE_MS +
      FINAL_PAUSE_MS;

    // Start animation on next frame so transition fires
    const raf = requestAnimationFrame(() => {
      if (barRef.current) {
        barRef.current.style.transition = `width ${totalMs}ms linear`;
        barRef.current.style.width = "100%";
      }
    });
    return () => cancelAnimationFrame(raf);
  }, [phase]);

  // ── Typewriter step runner ────────────────────────────────────────────────
  useEffect(() => {
    if (phase !== "loading") return;
    let cancelled = false;

    async function runSteps() {
      for (let i = 0; i < LOADING_STEPS.length; i++) {
        if (cancelled) return;
        const text = LOADING_STEPS[i];

        // Type each character
        for (let j = 1; j <= text.length; j++) {
          if (cancelled) return;
          setCurrentTyped(text.slice(0, j));
          await new Promise<void>((r) => setTimeout(r, CHAR_MS));
        }

        // Step done — brief pause then advance
        await new Promise<void>((r) => setTimeout(r, STEP_PAUSE_MS));
        if (cancelled) return;

        setCompletedSteps((prev) => [...prev, text]);
        setCurrentTyped("");
      }

      // All steps done — final pause then reveal results
      await new Promise<void>((r) => setTimeout(r, FINAL_PAUSE_MS));
      if (!cancelled) {
        setPhase("results");
        window.scrollTo(0, 0);
      }
    }

    runSteps();
    return () => {
      cancelled = true;
    };
  }, [phase]);

  // ── Build chat context from stored result ─────────────────────────────────
  const chatContext: EstimationContext | null =
    stored
      ? {
          dataset: stored.dataset,
          effort_months: stored.result.estimated_effort.effort_months,
          confidence: stored.result.prediction_confidence,
          prediction_mode: stored.result.estimated_effort.prediction_mode,
          display_cost: stored.result.cost_breakdown?.display_cost ?? 0,
          target_currency: stored.result.cost_breakdown?.target_currency ?? "INR",
          base_cost_inr: stored.result.cost_breakdown?.base_cost_inr ?? 0,
          monthly_rate_inr: stored.result.cost_breakdown?.monthly_rate_inr ?? 0,
          exchange_rate: stored.result.cost_breakdown?.exchange_rate ?? 1,
          assumptions: stored.result.assumptions,
          warnings: stored.result.warnings,
        }
      : null;

  // ── Loading screen ────────────────────────────────────────────────────────
  if (phase === "loading") {
    return (
      <section className="flex min-h-screen items-center justify-center bg-background px-4 py-20">
        <div className="w-full max-w-lg space-y-8">
          {/* Title */}
          <div className="space-y-1.5 text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.15em] text-muted">
              Processing
            </p>
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Running ML models on your inputs
            </h2>
          </div>

          {/* Terminal-style typewriter card */}
          <div className="min-h-[200px] rounded-2xl border border-line/60 bg-[#0f1117] p-6 font-mono text-sm shadow-lg">
            {completedSteps.map((step, i) => (
              <p key={i} className="mb-1.5 text-emerald-400/70">
                <span className="mr-2 text-slate-600">$</span>
                {step}
              </p>
            ))}
            {currentTyped && (
              <p className="mb-1.5 text-emerald-300">
                <span className="mr-2 text-slate-600">$</span>
                {currentTyped}
                <span
                  className="ml-px inline-block w-[2px] bg-emerald-300"
                  style={{ animation: "blink-cursor 0.8s step-end infinite" }}
                >
                  &nbsp;
                </span>
              </p>
            )}
          </div>

          {/* Progress bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-muted">
              <span>Computing estimate…</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-line/40">
              <div
                ref={barRef}
                className="h-full rounded-full bg-primary"
                style={{ width: "0%" }}
              />
            </div>
          </div>
        </div>

        {/* Blink keyframe */}
        <style>{`
          @keyframes blink-cursor {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
          }
        `}</style>
      </section>
    );
  }

  // ── Results screen ────────────────────────────────────────────────────────
  if (!stored) return null;

  const { result } = stored;
  const effortMonths = result.estimated_effort.effort_months;
  const hasCostAnalysis = result.cost_breakdown !== null;
  const costINR = result.cost_breakdown?.base_cost_inr ?? 0;
  const displayCost = result.cost_breakdown?.display_cost ?? 0;
  const targetCurrency = result.cost_breakdown?.target_currency ?? "INR";
  const confidence = Math.round(result.prediction_confidence * 100);
  const monthlyRate = result.cost_breakdown?.monthly_rate_inr ?? 0;
  const costToShow = targetCurrency === "INR" ? costINR : displayCost;

  const { duration, teamCard, raw } = humanizeEffort(effortMonths);

  return (
    <section className="min-h-screen bg-background px-4 pb-16 pt-32 sm:px-6">
      <div className="mx-auto max-w-2xl space-y-5">
        {/* Back link */}
        <button
          type="button"
          onClick={() => router.push("/estimate")}
          className="flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-foreground"
        >
          <ArrowLeft size={15} />
          Back to estimator
        </button>

        {/* Header */}
        <header className="rounded-2xl border border-line/60 bg-card p-6 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
              Estimation Complete
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
              Your project estimate is ready
            </h1>
            <div className="mt-3 flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                {confidence}% confidence
              </span>
              <span className="text-xs text-muted">Based on historical project data</span>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0 print:hidden mt-4 sm:mt-0">
            {showSaveInput ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  autoFocus
                  placeholder="e.g. Enterprise Team Setup"
                  value={scenarioName}
                  onChange={(e) => setScenarioName(e.target.value)}
                  className="rounded-lg border border-line bg-background px-3 py-1.5 text-sm outline-none focus:border-primary"
                />
                <button
                  type="button"
                  onClick={() => {
                    if (scenarioName.trim()) {
                      const newScenario = { name: scenarioName.trim(), date: new Date().toISOString(), result };
                      const updated = [...savedScenarios, newScenario];
                      setSavedScenarios(updated);
                      localStorage.setItem("software_cost_scenarios", JSON.stringify(updated));
                      setShowSaveInput(false);
                      setScenarioName("");
                    }
                  }}
                  className="rounded-lg bg-emerald-500 px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-600"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => setShowSaveInput(false)}
                  className="rounded-lg px-2 py-1.5 text-sm font-semibold text-muted hover:bg-muted/10 hover:text-foreground"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowSaveInput(true)}
                className="flex w-full sm:w-auto items-center justify-center gap-1.5 rounded-lg border border-line bg-background px-3 py-2 text-sm font-semibold text-foreground transition-colors hover:bg-muted/10 shadow-sm"
              >
                <FloppyDisk size={16} />
                Save Scenario
              </button>
            )}
            {!showSaveInput && (
              <button
                type="button"
                onClick={() => window.print()}
                className="flex w-full sm:w-auto items-center justify-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary/90 shadow-sm"
              >
                <Printer size={16} />
                Export PDF
              </button>
            )}
          </div>
        </header>

        {/* Hero effort card */}
        <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
          <div className="flex items-start gap-4">
            <span className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <UsersThree size={26} weight="duotone" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">
                Total Work Required
              </p>
              {/* Human-readable headline */}
              <p className="mt-1.5 text-4xl font-semibold tracking-tight text-foreground">
                ~{duration}
              </p>
              <p className="mt-1 text-sm text-muted">
                with a team of 5 people — that's{" "}
                <span className="font-medium text-foreground">{raw}</span> of total effort
              </p>

              {/* What person-months means */}
              <div className="mt-4 rounded-xl border border-line/50 bg-background px-4 py-3">
                <p className="flex items-center gap-1.5 text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-muted">
                  <Info size={12} />
                  What does this mean?
                </p>
                <p className="mt-1 text-xs text-muted leading-5">
                  <strong className="text-foreground">{raw}</strong> means if one person worked alone it would
                  take {raw.replace("-", " ")}. The larger your team, the faster the delivery.
                </p>
              </div>

              {/* Team-size breakdown grid */}
              <div className="mt-4 grid grid-cols-4 gap-2">
                {teamCard.map(({ size, months }) => (
                  <div
                    key={size}
                    className="rounded-lg border border-line/50 bg-background p-2.5 text-center"
                  >
                    <p className="text-[0.65rem] font-semibold uppercase tracking-[0.1em] text-muted">
                      {size} devs
                    </p>
                    <p className="mt-1 text-sm font-semibold text-foreground">{months}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Cost card */}
        {hasCostAnalysis && (
        <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
          <div className="flex items-start gap-4">
            <span className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
              <CurrencyInr size={26} weight="duotone" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">
                Estimated Project Cost
              </p>
              <p className="mt-1.5 text-4xl font-semibold tracking-tight text-foreground">
                {formatINR(costINR)}
              </p>
              <p className="mt-1 text-sm text-muted">
                Total cost in Indian Rupees
              </p>

              {/* Cost breakdown rows */}
              <div className="mt-4 divide-y divide-line/40 rounded-xl border border-line/50 bg-background">
                <div className="flex items-center justify-between px-4 py-2.5">
                  <p className="text-xs text-muted">Monthly rate per person</p>
                  <p className="text-xs font-semibold text-foreground">{formatINR(monthlyRate)}</p>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <p className="text-xs text-muted">Total effort</p>
                  <p className="text-xs font-semibold text-foreground">{raw}</p>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <p className="text-xs text-muted">Base cost (INR)</p>
                  <p className="text-xs font-semibold text-foreground">{formatINR(costINR)}</p>
                </div>
                {targetCurrency !== "INR" && (
                  <div className="flex items-center justify-between px-4 py-2.5">
                    <p className="text-xs text-muted">Equivalent ({targetCurrency})</p>
                    <p className="text-xs font-semibold text-foreground">
                      {new Intl.NumberFormat("en-IN", {
                        style: "currency",
                        currency: targetCurrency,
                        maximumFractionDigits: 0,
                      }).format(displayCost)}
                    </p>
                  </div>
                )}
              </div>

              {/* Timeline with cost */}
              <div className="mt-3 flex items-center gap-2 rounded-xl bg-primary/5 px-4 py-2.5">
                <Calendar size={15} className="flex-shrink-0 text-primary" />
                <p className="text-xs text-muted">
                  With a 5-person team:{" "}
                  <span className="font-semibold text-foreground">~{duration}</span>,
                  approx.{" "}
                  <span className="font-semibold text-foreground">
                    {formatINR(monthlyRate * 5)}/month
                  </span>{" "}
                  burn rate
                </p>
              </div>
            </div>
          </div>
        </div>
        )}

        {/* Cost Range Visualization */}
        {result.cost_range && (
          <CostRangeCard costRange={result.cost_range} />
        )}

        {/* Role Breakdown Table */}
        {result.role_breakdown && (
          <RoleBreakdownCard roles={result.role_breakdown} totalCost={costINR} />
        )}

        {/* Phase Breakdown Table */}
        {result.phase_breakdown && (
          <PhaseBreakdownCard phases={result.phase_breakdown} />
        )}

        {/* Explainability Waterfall */}
        {result.explainability_waterfall && (
          <ExplainabilityWaterfallCard steps={result.explainability_waterfall} />
        )}

        {/* Risk Assessment */}
        {result.risk_assessment && (
          <RiskAssessmentCard risks={result.risk_assessment} />
        )}

        {/* Model Comparison Table */}
        {result.model_predictions && (
          <ModelComparisonCard
            predictions={result.model_predictions}
            monthlyRate={hasCostAnalysis ? monthlyRate : null}
          />
        )}

        {/* Saved Scenarios What-If Comparison */}
        {savedScenarios.length > 0 && (
          <div className="animate-fade-in rounded-2xl border border-line/60 bg-card p-6 shadow-sm print:hidden">
            <div className="flex items-center gap-3 mb-6">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-700">
                <FloppyDisk size={20} weight="duotone" />
              </span>
              <div>
                <p className="text-sm font-semibold text-foreground">Saved Scenarios</p>
                <p className="text-xs text-muted">Compare this estimate against previously saved "What-If" scenarios.</p>
              </div>
            </div>
            
            <div className="overflow-x-auto rounded-xl border border-line/50">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-line/40 bg-background">
                    <th className="px-4 py-3 text-left font-semibold text-muted">Scenario Name</th>
                    <th className="px-4 py-3 text-right font-semibold text-muted">Saved On</th>
                    <th className="px-4 py-3 text-right font-semibold text-muted">Total Effort</th>
                    <th className="px-4 py-3 text-right font-semibold text-muted">Total Cost (INR)</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Current */}
                  <tr className="border-b border-line/30 bg-primary/5 font-semibold">
                    <td className="px-4 py-3 text-foreground flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-primary" /> Current Estimate
                    </td>
                    <td className="px-4 py-3 text-right text-muted tabular-nums">Now</td>
                    <td className="px-4 py-3 text-right text-foreground tabular-nums">{result.estimated_effort.effort_months.toFixed(1)} PM</td>
                    <td className="px-4 py-3 text-right text-foreground tabular-nums">{result.cost_breakdown ? formatINR(result.cost_breakdown.base_cost_inr) : "—"}</td>
                  </tr>
                  
                  {/* Saved */}
                  {savedScenarios.map((sc, idx) => (
                    <tr key={idx} className="border-b border-line/30 last:border-b-0">
                      <td className="px-4 py-3 text-foreground">{sc.name}</td>
                      <td className="px-4 py-3 text-right text-muted tabular-nums">
                        {new Date(sc.date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right text-foreground tabular-nums">
                        {sc.result.estimated_effort.effort_months.toFixed(1)} PM
                      </td>
                      <td className="px-4 py-3 text-right text-foreground tabular-nums">
                        {sc.result.cost_breakdown ? formatINR(sc.result.cost_breakdown.base_cost_inr) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex justify-end">
               <button
                type="button"
                onClick={() => {
                  setSavedScenarios([]);
                  localStorage.removeItem("software_cost_scenarios");
                }}
                className="text-xs font-semibold text-rose-500 hover:text-rose-600 transition-colors"
               >
                 Clear all saved scenarios
               </button>
            </div>
          </div>
        )}

        {/* Warnings (if any) */}
        {result.warnings.length > 0 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800 print:hidden">
            {result.warnings[0]}
          </div>
        )}

        {/* AI Chatbot */}
        {chatContext && (
          <div className="animate-fade-in overflow-hidden rounded-2xl border border-line/60 bg-card shadow-sm">
            <div className="flex items-center gap-3 border-b border-line/40 px-6 pb-4 pt-5">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Brain size={20} weight="duotone" />
              </span>
              <div>
                <p className="text-sm font-semibold text-foreground">Ask the AI</p>
                <p className="text-xs text-muted">
                  Get a plain-English explanation, cost breakdown, or hiring advice
                </p>
              </div>
            </div>

            <ChatPanel
              context={chatContext}
              suggestedQuestions={SUGGESTED_QUESTIONS}
            />
          </div>
        )}
      </div>
    </section>
  );
}
