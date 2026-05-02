import Link from "next/link";

const features = [
  {
    num: "01",
    title: "User-driven dataset selection",
    description:
      "Choose between large code-heavy systems (COCOMO), business apps (Desharnais), or medium enterprise (China). No internal routing jargon.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
    ),
  },
  {
    num: "02",
    title: "Adaptive input forms",
    description:
      "Each project type collects only the fields that matter — KLOC for COCOMO, function points for Desharnais, AFP for China. Short and focused.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"/></svg>
    ),
  },
  {
    num: "03",
    title: "Calibrated ensemble output",
    description:
      "Three models (Random Forest, XGBoost, Linear Regression) ensembled per dataset. You get effort in person-months plus a full cost breakdown.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
    ),
  },
  {
    num: "04",
    title: "AI-powered Q&A assistant",
    description:
      "After estimation, ask our Groq-powered chatbot anything — why effort is high, how to reduce cost, or what the assumptions mean.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/></svg>
    ),
  },
];

export default function Features() {
  return (
    <section id="features" className="bg-background">
      <div className="mx-auto max-w-7xl px-6 py-24 lg:px-10">
        <div className="text-center mb-16">
          <p className="editorial-kicker">Features</p>
          <h2 className="mt-3 font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
            Designed for clarity and precision
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-base leading-7 text-muted">
            Every feature is built to give you accurate, understandable estimates 
            without overwhelming detail.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          {features.map((f) => (
            <div
              key={f.num}
              className="group card-elevated rounded-2xl p-8 transition-all duration-300 hover:shadow-[0_8px_32px_rgba(44,76,59,0.08)]"
            >
              <div className="flex items-start justify-between">
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/8 text-primary transition-colors group-hover:bg-primary/12">
                  {f.icon}
                </span>
                <span className="text-xs font-bold text-line">{f.num}</span>
              </div>
              <h3 className="mt-5 font-serif text-xl tracking-editorial text-foreground">
                {f.title}
              </h3>
              <p className="mt-3 text-sm leading-7 text-muted">
                {f.description}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Link href="/estimate" className="btn-primary">
            Start Estimating
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </Link>
        </div>
      </div>
    </section>
  );
}