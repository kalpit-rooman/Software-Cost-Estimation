import type { Metadata } from "next";
import Link from "next/link";
import HowItWorks from "@/components/HowItWorks";
import {
  ChartLine,
  Database,
  Sliders,
  Brain,
  ChartBar,
  Lightning,
  ArrowLeft,
  ArrowRight,
  Check,
  ChatCircleText,
} from "@phosphor-icons/react/dist/ssr";

export const metadata: Metadata = {
  title: "Features",
  description:
    "Explore every feature of SoftEstimate — intelligent ML predictions, minimal inputs, AI explanations, and instant results for software cost estimation.",
};

/* ── FeatureCard ─────────────────────────────────────────── */
function FeatureCard({
  icon,
  title,
  description,
  visual,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  visual: React.ReactNode;
}) {
  return (
    <div className="group rounded-2xl bg-white border border-line/50 shadow-sm overflow-hidden
                    transition-all duration-400 hover:-translate-y-1
                    hover:shadow-[0_12px_40px_rgba(44,76,59,0.09)] hover:border-primary/20">
      {/* Visual preview */}
      <div className="relative h-44 bg-[#f3efe6] flex items-center justify-center overflow-hidden border-b border-line/40">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.03] to-transparent" />
        {visual}
      </div>
      {/* Text */}
      <div className="p-6">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary
                          transition-all group-hover:bg-primary group-hover:text-white">
            {icon}
          </div>
          <h3 className="font-bold text-foreground text-base">{title}</h3>
        </div>
        <p className="text-sm text-muted leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

/* ── InputChip ───────────────────────────────────────────── */
function InputChip({ label, value, pct }: { label: string; value: string; pct: number }) {
  return (
    <div className="group rounded-2xl bg-white border border-line/50 shadow-sm p-5 transition-all duration-300
                    hover:border-primary/30 hover:shadow-[0_8px_24px_rgba(44,76,59,0.08)] hover:-translate-y-0.5">
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm font-semibold text-foreground">{label}</span>
        <span className="text-xs font-bold text-primary">{value}</span>
      </div>
      <div className="h-1.5 w-full bg-line/40 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

/* ── Feature Visuals ─────────────────────────────────────── */
function PredictionVisual() {
  return (
    <div className="w-40 bg-white rounded-xl border border-primary/15 shadow-md p-4 text-center transition-transform duration-500 group-hover:scale-105">
      <div className="text-[9px] font-bold uppercase tracking-widest text-muted mb-1">Effort</div>
      <div className="text-3xl font-serif text-primary">12.4<span className="text-sm text-muted">mo</span></div>
      <div className="mt-3 flex items-end gap-1 h-8 justify-center">
        {[30, 55, 40, 80, 60, 100].map((h, i) => (
          <div key={i} className="w-3 rounded-t-sm" style={{ height: `${h}%`, backgroundColor: i === 5 ? "rgb(44 76 59)" : `rgba(44,76,59,${0.12 + i * 0.1})` }} />
        ))}
      </div>
    </div>
  );
}

function MultiProjectVisual() {
  return (
    <div className="flex gap-3 items-end">
      {[
        { label: "Large System", h: "h-20", active: false },
        { label: "Business App", h: "h-28", active: true },
        { label: "Enterprise", h: "h-16", active: false },
      ].map((c) => (
        <div key={c.label} className={`${c.h} w-20 rounded-xl border flex flex-col items-center justify-center p-2 text-center transition-all duration-500 group-hover:scale-105 ${c.active ? "bg-white border-primary/30 shadow-lg" : "bg-white/60 border-line/50 opacity-70"}`}>
          <div className={`w-4 h-4 rounded-full mb-2 ${c.active ? "bg-primary" : "bg-muted/20"}`} />
          <span className="text-[9px] font-bold text-muted leading-tight">{c.label}</span>
        </div>
      ))}
    </div>
  );
}

function SliderVisual() {
  return (
    <div className="w-44 bg-white rounded-xl border border-line/60 shadow-md p-4 space-y-3 transition-transform duration-500 group-hover:scale-105">
      {[{ w: "70%" }, { w: "45%" }, { w: "85%" }].map((s, i) => (
        <div key={i}>
          <div className="h-1 w-full bg-muted/10 rounded-full relative">
            <div className="absolute top-0 left-0 h-full bg-primary rounded-full" style={{ width: s.w }} />
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 bg-white border-2 border-primary rounded-full shadow" style={{ left: s.w }} />
          </div>
        </div>
      ))}
      <div className="h-6 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
        <span className="text-[9px] font-bold text-primary">Calculate</span>
      </div>
    </div>
  );
}

function AIVisual() {
  return (
    <div className="w-52 bg-white rounded-xl border border-line/60 shadow-md p-4 space-y-2 transition-transform duration-500 group-hover:scale-105">
      <div className="flex gap-2">
        <div className="w-6 h-6 rounded-full bg-primary/10 shrink-0" />
        <div className="flex-1 space-y-1">
          <div className="h-2 w-3/4 bg-muted/15 rounded" />
          <div className="h-2 w-full bg-muted/10 rounded" />
          <div className="h-2 w-2/3 bg-muted/10 rounded" />
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <div className="flex-1 max-w-[65%] space-y-1">
          <div className="h-2 w-full bg-primary/15 rounded" />
          <div className="h-2 w-3/4 bg-primary/10 rounded" />
        </div>
        <div className="w-6 h-6 rounded-full bg-primary shrink-0" />
      </div>
    </div>
  );
}

function DataVisual() {
  return (
    <div className="flex items-end gap-2 h-20 transition-transform duration-500 group-hover:scale-105">
      {[45, 65, 50, 90, 70, 85, 100].map((h, i) => (
        <div key={i} className="w-5 rounded-t-md transition-all duration-500"
          style={{ height: `${h}%`, backgroundColor: `rgba(44,76,59,${0.2 + i * 0.1})` }} />
      ))}
    </div>
  );
}

function PerformanceVisual() {
  return (
    <div className="flex flex-col items-center gap-2 transition-transform duration-500 group-hover:scale-105">
      <div className="flex items-center gap-2 bg-white rounded-xl border border-primary/15 shadow-md px-5 py-3">
        <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
        <span className="text-sm font-bold text-primary">Result ready in</span>
        <span className="text-xl font-serif text-foreground">&lt;5s</span>
      </div>
      <div className="h-1 w-36 bg-line/40 rounded-full overflow-hidden">
        <div className="h-full bg-primary rounded-full w-[15%] transition-all duration-1000 group-hover:w-[100%]" />
      </div>
    </div>
  );
}

/* ── Page ────────────────────────────────────────────────── */
export default function FeaturesPage() {
  return (
    <div className="bg-[#f3efe6] min-h-screen">

      {/* ── Hero ──────────────────────────────────────────── */}
      <section className="relative overflow-hidden pt-32 pb-20 lg:pt-40 lg:pb-28">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-[-15%] right-[-8%] w-[500px] h-[500px] rounded-full bg-primary/[0.05] blur-3xl" />
          <div className="absolute bottom-[-10%] left-[-5%] w-[400px] h-[400px] rounded-full bg-teal/[0.06] blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-5xl px-6 lg:px-10 text-center">
          <p className="editorial-kicker mb-4">Product Features</p>
          <h1 className="font-serif text-[clamp(2.4rem,5vw,4.2rem)] leading-[1.1] tracking-[-0.03em] text-foreground">
            Everything You Need for<br />
            <span className="text-primary italic">Accurate Cost Estimation</span>
          </h1>
          <p className="mt-6 max-w-xl mx-auto text-lg leading-8 text-muted">
            A complete system designed to make estimation simple, fast, and data-driven.
          </p>
        </div>
      </section>

      {/* ── How It Works (reused) ─────────────────────────── */}
      <HowItWorks />

      {/* ── Core Features ─────────────────────────────────── */}
      <section className="py-24 lg:py-32 bg-background border-y border-line/40">
        <div className="mx-auto max-w-5xl px-6 lg:px-10">
          <div className="text-center mb-16">
            <p className="editorial-kicker mb-3">Core Capabilities</p>
            <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
              Built for Accuracy and Simplicity
            </h2>
            <p className="mt-4 max-w-xl mx-auto text-base text-muted leading-7">
              Each feature is carefully designed to deliver reliable estimates without overwhelming you with complexity.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={<ChartLine size={18} weight="duotone" />}
              title="Intelligent Cost Prediction"
              description="Predict project effort using trained machine learning models built on real historical data."
              visual={<PredictionVisual />}
            />
            <FeatureCard
              icon={<Database size={18} weight="duotone" />}
              title="Multi-Project Support"
              description="Estimate costs across different types of software projects with a single unified platform."
              visual={<MultiProjectVisual />}
            />
            <FeatureCard
              icon={<Sliders size={18} weight="duotone" />}
              title="Minimal Input System"
              description="Get accurate estimates with just a few simple, intuitive inputs — no technical jargon required."
              visual={<SliderVisual />}
            />
            <FeatureCard
              icon={<Brain size={18} weight="duotone" />}
              title="AI Explanation Engine"
              description="Understand your estimate with AI-powered explanations that answer your follow-up questions."
              visual={<AIVisual />}
            />
            <FeatureCard
              icon={<ChartBar size={18} weight="duotone" />}
              title="Data-Driven Models"
              description="Built on real-world industry datasets for reliable predictions you can actually trust."
              visual={<DataVisual />}
            />
            <FeatureCard
              icon={<Lightning size={18} weight="duotone" />}
              title="Optimized Performance"
              description="Fast and efficient predictions delivered in seconds with highly optimized inference models."
              visual={<PerformanceVisual />}
            />
          </div>
        </div>
      </section>

      {/* ── Input Simplicity ──────────────────────────────── */}
      <section className="py-24 lg:py-32 bg-[#f3efe6]">
        <div className="mx-auto max-w-5xl px-6 lg:px-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="editorial-kicker mb-3">Simple by Design</p>
              <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
                Simple Inputs,<br />
                <span className="text-primary italic">Powerful Results</span>
              </h2>
              <p className="mt-5 text-lg leading-8 text-muted">
                Instead of complex technical parameters, SoftEstimate uses intuitive inputs anyone can understand.
                Just describe your project in plain terms and let our models do the heavy lifting.
              </p>
              <ul className="mt-8 space-y-3">
                {[
                  "No engineering degree required",
                  "Plain-language field labels",
                  "Instant validation feedback",
                  "Smart defaults for common projects",
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-sm text-foreground">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <Check size={10} weight="bold" className="text-primary" />
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <InputChip label="Project Size" value="Medium" pct={55} />
              <InputChip label="Complexity" value="High" pct={78} />
              <InputChip label="Team Experience" value="Senior" pct={85} />
              <InputChip label="Reliability" value="Critical" pct={90} />
              <div className="col-span-2">
                <InputChip label="Data Intensity" value="Moderate" pct={45} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Output / Results ──────────────────────────────── */}
      <section className="py-24 lg:py-32 bg-white border-y border-line/40">
        <div className="mx-auto max-w-5xl px-6 lg:px-10">
          <div className="text-center mb-16">
            <p className="editorial-kicker mb-3">What You Get</p>
            <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
              Clear, Actionable Results
            </h2>
            <p className="mt-4 max-w-xl mx-auto text-base text-muted leading-7">
              Every estimate comes with a complete breakdown — so you know exactly what you're getting.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                label: "Estimated Effort",
                value: "12.4 months",
                sub: "Based on similar projects in dataset",
                color: "border-primary/20 bg-primary/[0.02]",
                badge: "bg-primary/10 text-primary",
              },
              {
                label: "Project Insights",
                value: "3 key factors",
                sub: "Size, complexity & team experience",
                color: "border-teal/20 bg-teal/[0.02]",
                badge: "bg-teal/10 text-teal",
              },
              {
                label: "AI Explanation",
                value: "Instant Q&A",
                sub: "Ask anything about your estimate",
                color: "border-gold/20 bg-gold/[0.02]",
                badge: "bg-gold/10 text-gold",
              },
            ].map((item) => (
              <div key={item.label} className={`rounded-2xl border p-6 ${item.color} transition-all duration-300 hover:-translate-y-1 hover:shadow-md`}>
                <div className={`inline-block text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-md mb-4 ${item.badge}`}>
                  {item.label}
                </div>
                <div className="font-serif text-3xl text-foreground mb-2">{item.value}</div>
                <p className="text-sm text-muted">{item.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── AI Section ────────────────────────────────────── */}
      <section className="py-24 lg:py-32 bg-[#f3efe6]">
        <div className="mx-auto max-w-5xl px-6 lg:px-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">

            {/* Chat Preview */}
            <div className="order-2 lg:order-1">
              <div className="rounded-2xl bg-white border border-line/50 shadow-sm overflow-hidden">
                {/* Title bar */}
                <div className="flex items-center gap-2 px-5 py-3.5 border-b border-line/40 bg-background">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-300" />
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-300" />
                    <div className="w-2.5 h-2.5 rounded-full bg-green-300" />
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    <ChatCircleText size={14} className="text-primary" weight="duotone" />
                    <span className="text-xs font-semibold text-muted">AI Assistant</span>
                  </div>
                </div>
                {/* Messages */}
                <div className="p-5 space-y-4">
                  <div className="flex gap-3">
                    <div className="w-7 h-7 rounded-full bg-primary/10 shrink-0 flex items-center justify-center text-primary">
                      <ChatCircleText size={14} weight="duotone" />
                    </div>
                    <div className="bg-background rounded-xl rounded-tl-none px-4 py-3 max-w-[80%]">
                      <p className="text-sm text-foreground">Your estimate is 12.4 months based on the project complexity and team size.</p>
                    </div>
                  </div>
                  <div className="flex gap-3 justify-end">
                    <div className="bg-primary/10 rounded-xl rounded-tr-none px-4 py-3 max-w-[80%]">
                      <p className="text-sm text-foreground">Why is it so high? What can I do to reduce it?</p>
                    </div>
                    <div className="w-7 h-7 rounded-full bg-primary shrink-0 flex items-center justify-center text-white text-xs font-bold">U</div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-7 h-7 rounded-full bg-primary/10 shrink-0 flex items-center justify-center text-primary">
                      <ChatCircleText size={14} weight="duotone" />
                    </div>
                    <div className="bg-background rounded-xl rounded-tl-none px-4 py-3 max-w-[80%]">
                      <p className="text-sm text-muted">Increasing team experience from Junior to Senior could reduce effort by ~20%...</p>
                      <div className="mt-2 flex gap-1">
                        <div className="h-1.5 w-2 bg-primary/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                        <div className="h-1.5 w-2 bg-primary/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="h-1.5 w-2 bg-primary/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                    </div>
                  </div>
                </div>
                {/* Input */}
                <div className="px-5 pb-5">
                  <div className="flex gap-2 items-center border border-line/50 rounded-xl px-4 py-2.5 bg-background">
                    <span className="text-sm text-muted/50 flex-1">Ask a follow-up question...</span>
                    <div className="w-6 h-6 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                      <ArrowRight size={12} weight="bold" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <p className="editorial-kicker mb-3">AI-Powered Q&A</p>
              <h2 className="font-serif text-4xl leading-tight tracking-[-0.02em] text-foreground sm:text-5xl">
                Ask Questions About<br />
                <span className="text-primary italic">Your Estimate</span>
              </h2>
              <p className="mt-5 text-lg leading-8 text-muted">
                Don't just get a number — understand it. Our built-in AI assistant helps you explore your results, question assumptions, and discover ways to optimize your project plan.
              </p>
              <div className="mt-8 grid grid-cols-2 gap-3">
                {[
                  "Why is this estimate high?",
                  "How can I reduce cost?",
                  "What affects the timeline?",
                  "Compare to similar projects",
                ].map((q) => (
                  <div key={q} className="rounded-xl border border-line/50 bg-white px-4 py-3 text-xs font-medium text-muted hover:border-primary/30 hover:text-primary transition-colors cursor-pointer">
                    "{q}"
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ── Final CTA ─────────────────────────────────────── */}
      <section className="bg-primary py-20 lg:py-28">
        <div className="mx-auto max-w-5xl px-6 lg:px-10 text-center">
          <h2 className="font-serif text-3xl text-white sm:text-4xl tracking-[-0.02em]">
            Start Estimating Your Project
          </h2>
          <p className="mt-4 max-w-xl mx-auto text-base text-white/70 leading-7">
            Pick a project type, fill in a brief, and get a calibrated ML estimate in seconds.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link href="/estimate" className="btn-gold">
              Start Estimating
              <ArrowRight size={16} weight="bold" />
            </Link>
            <Link href="/" className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border-2 border-white/30 text-white/80 text-sm font-semibold hover:border-white hover:text-white transition-all duration-300">
              <ArrowLeft size={16} weight="bold" />
              Back to Home
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
