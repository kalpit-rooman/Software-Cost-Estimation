const supportingFeatures = [
  {
    index: "01",
    title: "Multiple ML Models",
    description: "Review Random Forest, XGBoost, and Linear Regression outputs side by side before acting on a recommendation.",
  },
  {
    index: "02",
    title: "Ensemble Prediction",
    description: "Use the combined estimate as the lead signal while still keeping every underlying model visible for inspection.",
  },
  {
    index: "03",
    title: "Dataset-Based Estimation",
    description: "Switch between China, COCOMO-81, and Desharnais contexts without changing the demo flow.",
  },
  {
    index: "04",
    title: "Real-time Results",
    description: "Fetch predictions from the live FastAPI service and display the recommendation immediately in the interface.",
  },
];

const leadPoints = [
  "Model outputs stay visible instead of being collapsed into a single black-box number.",
  "The ensemble estimate becomes the headline, but the supporting evidence remains on the page.",
  "Dataset selection changes the inference lens without forcing a different interaction pattern.",
];

const footerNotes = [
  {
    label: "Live API",
    value: "GET /datasets · POST /predict",
  },
  {
    label: "Type-safe client",
    value: "Typed request and response helpers in the frontend service layer",
  },
  {
    label: "Responsive layout",
    value: "Editorial composition scales down without losing navigation or demo access",
  },
];

export default function Features() {
  return (
    <section id="features" className="border-b border-line/80 bg-card/30">
      <div className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div className="max-w-2xl">
            <p className="editorial-kicker">Features</p>
            <h2 className="mt-4 font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
              Designed for fast comparison and clear decisions.
            </h2>
          </div>
          <p className="max-w-xl text-base leading-8 text-muted sm:text-lg">
            The experience stays spare and legible, with enough detail to compare model behavior without overwhelming the user.
          </p>
        </div>

        <div className="mt-12 grid gap-px border border-line bg-line lg:grid-cols-[1.14fr_0.86fr]">
          <article className="paper-panel bg-background px-6 py-8 sm:px-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <p className="editorial-kicker">Lead capability</p>
              <p className="text-xs uppercase tracking-[0.24em] text-muted">01</p>
            </div>

            <h3 className="mt-5 max-w-3xl font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
              The homepage reads like a brief, then hands off to a working estimator.
            </h3>

            <p className="mt-6 max-w-3xl text-base leading-8 text-muted sm:text-lg">
              The redesign shifts the page away from a symmetrical product template and toward a clearer editorial sequence: context first, system signals second, live demo third.
            </p>

            <div className="mt-8 grid gap-px border border-line bg-line sm:grid-cols-3">
              {leadPoints.map((point) => (
                <div key={point} className="bg-card px-5 py-5 text-sm leading-7 text-muted">
                  {point}
                </div>
              ))}
            </div>
          </article>

          <div className="grid gap-px bg-line">
            {supportingFeatures.map((feature) => (
              <article key={feature.index} className="bg-background px-6 py-7">
                <p className="text-xs uppercase tracking-[0.24em] text-muted">{feature.index}</p>
                <h3 className="mt-5 font-serif text-3xl tracking-editorial text-foreground">{feature.title}</h3>
                <p className="mt-4 text-sm leading-7 text-muted">{feature.description}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="mt-px grid gap-px border-x border-b border-line bg-line md:grid-cols-3">
          {footerNotes.map((note) => (
            <div key={note.label} className="bg-card px-5 py-5">
              <p className="text-xs uppercase tracking-[0.24em] text-muted">{note.label}</p>
              <p className="mt-3 text-sm leading-7 text-muted">{note.value}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}