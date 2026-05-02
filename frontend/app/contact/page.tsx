import type { Metadata } from "next";
import ContactForm from "@/components/ContactForm";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Get in touch with the SoftEstimate team — questions about methodology, datasets, or collaboration.",
};

const teamInfo = [
  { label: "Project type", value: "Academic / Research — Software Cost Estimation", icon: "📚" },
  { label: "Tech stack", value: "Next.js · FastAPI · scikit-learn · XGBoost", icon: "⚡" },
  { label: "Datasets", value: "COCOMO-81 · Desharnais · China", icon: "📊" },
];

export default function ContactPage() {
  return (
    <section className="bg-background">
      <div className="mx-auto max-w-7xl px-6 pt-40 pb-24 lg:px-10">
        {/* Header */}
        <div className="mb-14 max-w-2xl">
          <p className="editorial-kicker">Contact</p>
          <h1 className="mt-4 font-serif text-5xl tracking-editorial text-foreground sm:text-6xl">
            Get in touch
          </h1>
          <p className="mt-5 text-lg leading-8 text-muted">
            Have a question about the estimation methodology, a dataset, or
            want to collaborate? Fill in the form below.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          {/* Left — form */}
          <div className="card-elevated rounded-2xl p-8 sm:p-10">
            <ContactForm />
          </div>

          {/* Right — info */}
          <div className="space-y-5">
            <div className="card-elevated rounded-2xl p-7">
              <p className="editorial-kicker">About the project</p>
              <p className="mt-3 text-sm leading-7 text-muted">
                SoftEstimate is an ML-powered software effort estimation tool
                built on three industry-standard datasets. It uses ensemble
                models to produce calibrated effort estimates in person-months.
              </p>
            </div>

            {teamInfo.map((item) => (
              <div key={item.label} className="card-elevated rounded-2xl p-6 flex items-start gap-4">
                <span className="text-xl">{item.icon}</span>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted">{item.label}</p>
                  <p className="mt-1 text-sm font-medium text-foreground">{item.value}</p>
                </div>
              </div>
            ))}

            <div className="card-elevated rounded-2xl p-7 bg-primary text-white">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/60">Next action</p>
              <Link
                href="/estimate"
                className="mt-3 inline-flex items-center gap-2 font-serif text-xl text-white transition-colors hover:text-gold"
              >
                Try the estimator →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
