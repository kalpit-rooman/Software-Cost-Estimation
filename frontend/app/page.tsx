import type { Metadata } from "next";
import Link from "next/link";
import Features from "@/components/Features";

export const metadata: Metadata = {
  title: "Home",
  description:
    "Predict software development effort and cost using ML models trained on COCOMO-81, Desharnais, and China datasets.",
};

const stats = [
  { value: "3", label: "ML Models", sub: "RF · XGBoost · LR" },
  { value: "3", label: "Datasets", sub: "COCOMO · Desharnais · China" },
  { value: "643", label: "Projects Trained", sub: "Real-world data" },
  { value: "<5s", label: "Estimation Time", sub: "Instant results" },
];

const datasets = [
  {
    tag: "COCOMO-81",
    label: "Large, code-heavy systems",
    hint: "Lines of code, cost drivers, schedule constraints",
    icon: "🏗️",
    color: "bg-primary/10 text-primary",
  },
  {
    tag: "Desharnais",
    label: "Business applications",
    hint: "Function points, transactions, team experience",
    icon: "📊",
    color: "bg-secondary/10 text-secondary",
  },
  {
    tag: "China",
    label: "Medium enterprise systems",
    hint: "AFP, transaction volume, integrations",
    icon: "🏢",
    color: "bg-teal/20 text-teal",
  },
];

export default function HomePage() {
  return (
    <>
      {/* ── Hero ─────────────────────────────────────────────── */}
      <section className="relative section-wash overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-primary/[0.04] blur-3xl" />
          <div className="absolute bottom-[-30%] left-[-10%] w-[500px] h-[500px] rounded-full bg-teal/[0.06] blur-3xl" />
          <div className="absolute top-[20%] left-[50%] w-[300px] h-[300px] rounded-full bg-gold/[0.05] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 pb-20 pt-32 lg:px-10 lg:pt-40 lg:pb-28">
          <div className="max-w-4xl animate-fade-in-up">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 mb-8">
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                ML-Powered Estimation
              </span>
            </div>

            <h1 className="font-serif text-[clamp(2.8rem,6.5vw,5.5rem)] leading-[1.05] tracking-[-0.035em] text-foreground">
              Predict software cost
              <br />
              <span className="text-primary">with real data.</span>
            </h1>

            <p className="mt-7 max-w-2xl text-lg leading-8 text-muted sm:text-xl animate-fade-in-up delay-100">
              Pick your project type, fill in a short brief, and get a calibrated 
              effort and cost estimate in seconds — driven by ensemble ML models
              trained on industry-standard datasets.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4 animate-fade-in-up delay-200">
              <Link href="/estimate" className="btn-primary">
                Start Estimating
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </Link>
              <Link href="/#features" className="btn-secondary">
                Explore Features
              </Link>
            </div>
          </div>

          {/* Stats strip */}
          <div className="mt-16 grid grid-cols-2 gap-4 sm:grid-cols-4 animate-fade-in-up delay-300">
            {stats.map((s) => (
              <div key={s.label} className="card-elevated rounded-xl px-5 py-5">
                <p className="font-serif text-3xl tracking-editorial text-primary">{s.value}</p>
                <p className="mt-1 text-sm font-semibold text-foreground">{s.label}</p>
                <p className="text-xs text-muted">{s.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Datasets ─────────────────────────────────────────── */}
      <section className="border-y border-line/40 bg-card">
        <div className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
          <div className="text-center mb-14">
            <p className="editorial-kicker">Estimation Paths</p>
            <h2 className="mt-3 font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
              One tool, three estimation models
            </h2>
            <p className="mt-4 max-w-2xl mx-auto text-base text-muted leading-7">
              Select your project type and we route your inputs to the right ML pipeline.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-3">
            {datasets.map((d) => (
              <Link
                key={d.tag}
                href="/estimate"
                className="group card-elevated rounded-2xl p-7 transition-all duration-300 hover:shadow-[0_8px_32px_rgba(44,76,59,0.1)] hover:-translate-y-1"
              >
                <span className={`inline-flex h-12 w-12 items-center justify-center rounded-xl text-xl ${d.color}`}>
                  {d.icon}
                </span>
                <p className="mt-5 text-xs font-semibold uppercase tracking-[0.2em] text-gold">
                  {d.tag}
                </p>
                <h3 className="mt-2 font-serif text-xl tracking-editorial text-foreground group-hover:text-primary transition-colors">
                  {d.label}
                </h3>
                <p className="mt-2 text-sm leading-6 text-muted">{d.hint}</p>
                <div className="mt-5 flex items-center gap-1.5 text-sm font-medium text-primary opacity-0 translate-x-[-4px] transition-all duration-300 group-hover:opacity-100 group-hover:translate-x-0">
                  <span>Get estimate</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────── */}
      <Features />

      {/* ── About ─────────────────────────────────────────────── */}
      <section id="about" className="bg-background">
        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-10">
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="editorial-kicker">About the project</p>
              <h2 className="mt-4 font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
                A decision tool, not just a utility screen.
              </h2>
              <p className="mt-6 text-lg leading-8 text-muted">
                SoftEstimate frames machine learning output as something to
                inspect, compare, and trust deliberately — built for software 
                cost estimation workflows that need real analytical depth.
              </p>
              <div className="mt-8 space-y-4">
                {[
                  "Three dataset pipelines with ensemble ML models",
                  "Adaptive inputs scoped to each estimation method",
                  "Confidence, assumptions, and warnings surfaced transparently",
                  "AI-powered chatbot for post-estimation Q&A",
                ].map((item) => (
                  <div key={item} className="flex items-start gap-3">
                    <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><polyline points="20 6 9 17 4 12"/></svg>
                    </span>
                    <span className="text-sm leading-6 text-foreground">{item}</span>
                  </div>
                ))}
              </div>
              <Link href="/estimate" className="btn-primary mt-10">
                Try the Estimator
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "Frontend", value: "Next.js 15 + Tailwind", icon: "⚡" },
                { label: "Backend", value: "FastAPI + Python", icon: "🐍" },
                { label: "ML Stack", value: "RF · XGBoost · LR", icon: "🧠" },
                { label: "Chatbot", value: "Groq + LLaMA 3.3", icon: "💬" },
              ].map((item) => (
                <div key={item.label} className="card-elevated rounded-xl p-5 text-center">
                  <span className="text-2xl">{item.icon}</span>
                  <p className="mt-3 text-xs font-semibold uppercase tracking-[0.2em] text-muted">{item.label}</p>
                  <p className="mt-1 text-sm font-medium text-foreground">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA Banner ────────────────────────────────────────── */}
      <section className="bg-primary">
        <div className="mx-auto max-w-7xl px-6 py-16 lg:px-10">
          <div className="flex flex-col items-center text-center gap-6">
            <h2 className="font-serif text-3xl tracking-editorial text-white sm:text-4xl">
              Ready to estimate your next project?
            </h2>
            <p className="max-w-xl text-base text-white/70 leading-7">
              Pick a project type, fill in a brief, and get a calibrated ML estimate 
              with cost breakdown, assumptions, and an AI assistant to answer your questions.
            </p>
            <Link href="/estimate" className="btn-gold">
              Get Your Estimate
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}