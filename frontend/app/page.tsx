import type { Metadata } from "next";
import Link from "next/link";
import RetroComputer from "@/components/RetroComputer";
import ProblemSolution from "@/components/ProblemSolution";
import HowItWorks from "@/components/HowItWorks";

export const metadata: Metadata = {
  title: "Home",
  description:
    "Predict software development effort and cost using ML models trained on COCOMO-81, Desharnais, and China datasets.",
};

export default function HomePage() {
  return (
    <>
      {/* ── Hero ─────────────────────────────────────────────── */}
      <section className="relative bg-[#f3efe6] overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-primary/[0.04] blur-3xl" />
          <div className="absolute bottom-[-30%] left-[-10%] w-[500px] h-[500px] rounded-full bg-teal/[0.06] blur-3xl" />
          <div className="absolute top-[20%] left-[50%] w-[300px] h-[300px] rounded-full bg-gold/[0.05] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 pb-20 pt-20 lg:px-10 lg:pt-24 lg:pb-28">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="max-w-4xl animate-fade-in-up">
              <h1 className="font-serif text-[clamp(2.4rem,5.2vw,4.8rem)] leading-[1.1] tracking-[-0.03em] text-foreground">
                Predict software cost
                <br />
                <span className="text-primary italic">with real data.</span>
              </h1>

              <p className="mt-6 max-w-2xl text-base leading-7 text-muted sm:text-lg animate-fade-in-up delay-100">
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

            <div className="hidden lg:flex justify-center items-center w-full h-full animate-fade-in-up delay-300">
              <RetroComputer />
            </div>
          </div>
        </div>
      </section>

      {/* ── Problem & Solution ────────────�              <div key={item.label} className="card-elevated rounded-xl p-5 text-center">
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