"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Brain, Calendar, CurrencyInr, Info, UsersThree } from "@phosphor-icons/react";
import ChatPanel from "./ChatPanel";
import type { DatasetKey, EstimationContext, FinalPredictionResponse } from "@/lib/api";

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

// ── Component ─────────────────────────────────────────────────────────────────

export default function ResultsPage() {
  const router = useRouter();

  // Phase
  const [phase, setPhase] = useState<"loading" | "results">("loading");

  // Loading animation state
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [currentTyped, setCurrentTyped] = useState("");

  // Stored result
  const [stored, setStored] = useState<StoredEstimation | null>(null);

  // Progress bar ref — animated via CSS linear transition
  const barRef = useRef<HTMLDivElement>(null);

  // ── Read sessionStorage ───────────────────────────────────────────────────
  useEffect(() => {
    const raw = sessionStorage.getItem("estimation_result");
    if (!raw) {
      router.replace("/estimate");
      return;
    }
    try {
      setStored(JSON.parse(raw) as StoredEstimation);
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
      if (!cancelled) setPhase("results");
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
          display_cost: stored.result.cost_breakdown.display_cost,
          target_currency: stored.result.cost_breakdown.target_currency,
          base_cost_inr: stored.result.cost_breakdown.base_cost_inr,
          monthly_rate_inr: stored.result.cost_breakdown.monthly_rate_inr,
          exchange_rate: stored.result.cost_breakdown.exchange_rate,
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
  const costINR = result.cost_breakdown.base_cost_inr;
  const displayCost = result.cost_breakdown.display_cost;
  const targetCurrency = result.cost_breakdown.target_currency;
  const confidence = Math.round(result.prediction_confidence * 100);
  const monthlyRate = result.cost_breakdown.monthly_rate_inr;
  const costToShow = targetCurrency === "INR" ? costINR : displayCost;

  const { duration, teamCard, raw } = humanizeEffort(effortMonths);

  return (
    <section className="min-h-screen bg-background px-4 py-16 sm:px-6">
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
        <header className="rounded-2xl border border-line/60 bg-card p-6 shadow-sm">
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

        {/* Warnings (if any) */}
        {result.warnings.length > 0 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
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
