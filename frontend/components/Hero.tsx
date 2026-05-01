const previewRows = [
  { label: "Random Forest", value: "$82.4k", width: "78%" },
  { label: "XGBoost", value: "$79.1k", width: "68%" },
  { label: "Linear Regression", value: "$86.8k", width: "84%" },
  { label: "Ensemble", value: "$82.7k", width: "80%" },
];

const editorialNotes = [
  {
    title: "Readable at a glance",
    body: "The interface favors hierarchy, spacing, and thin rules over product-dashboard chrome.",
  },
  {
    title: "Connected to the backend",
    body: "The home page remains wired to live FastAPI endpoints rather than static placeholders.",
  },
];

const signalRows = [
  {
    label: "Three datasets",
    value: "China, COCOMO-81, Desharnais",
  },
  {
    label: "Prediction stack",
    value: "Random Forest, XGBoost, Linear Regression, Ensemble",
  },
  {
    label: "Interface brief",
    value: "KLOC, complexity, team experience, reliability",
  },
];

export default function Hero() {
  return (
    <section id="home" className="section-wash border-b border-line/80">
      <div className="mx-auto max-w-7xl px-6 pb-16 pt-10 lg:px-10 lg:pb-24">
        <div className="grid gap-8 border-b border-line/80 pb-8 lg:grid-cols-[0.28fr_1.06fr_0.56fr]">
          <div className="space-y-6">
            <div>
              <p className="editorial-kicker">Field notes</p>
              <p className="mt-4 text-sm leading-7 text-muted">
                A warmer, more archival home page for a production prediction tool that still needs to read clearly at speed.
              </p>
            </div>

            <div className="border-t border-line/80 pt-4">
              <p className="text-[0.68rem] uppercase tracking-[0.28em] text-muted">In this edition</p>
              <ul className="mt-4 space-y-3 text-sm leading-7 text-muted">
                <li>Live backend integration, not a static concept page.</li>
                <li>Dataset-specific estimation framed as a readable brief.</li>
                <li>Ensemble results surfaced without hiding the individual model outputs.</li>
              </ul>
            </div>
          </div>

          <div>
            <div className="flex flex-wrap items-center justify-between gap-4 text-[0.68rem] uppercase tracking-[0.28em] text-muted">
              <span>Home</span>
              <span>Single-page analytical edition</span>
            </div>

            <h1 className="mt-6 max-w-4xl font-serif text-[clamp(3.8rem,8.2vw,7.5rem)] leading-[0.88] tracking-[-0.055em] text-foreground">
              Software cost estimation,
              <br />
              presented like an editorial briefing.
            </h1>

            <p className="mt-8 max-w-2xl text-lg leading-8 text-muted sm:text-xl">
              Predict software development cost using machine learning and ensemble models, then read the outcome in a layout built for confidence rather than dashboard repetition.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <a
                href="#demo"
                className="border border-foreground bg-foreground px-6 py-3 text-sm uppercase tracking-[0.18em] text-background transition-colors hover:border-accent hover:bg-accent"
              >
                Try Demo
              </a>
              <a
                href="#features"
                className="border border-line bg-card px-6 py-3 text-sm uppercase tracking-[0.18em] text-foreground transition-colors hover:border-foreground"
              >
                Read Features
              </a>
            </div>
          </div>

          <div className="space-y-px border border-line bg-line">
            <div className="paper-panel bg-card px-5 py-5">
              <p className="editorial-kicker">Current read</p>
              <h2 className="mt-4 font-serif text-3xl tracking-editorial text-foreground">A deliberate interface for live estimation.</h2>
              <p className="mt-4 text-sm leading-7 text-muted">
                Premium editorial cues, thin borders, and a quieter palette keep the page from collapsing into the usual SaaS template language.
              </p>
            </div>

            {editorialNotes.map((note) => (
              <article key={note.title} className="bg-background px-5 py-5">
                <p className="text-[0.68rem] uppercase tracking-[0.26em] text-muted">{note.title}</p>
                <p className="mt-3 text-sm leading-7 text-muted">{note.body}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="mt-8 grid gap-px border border-line bg-line lg:grid-cols-[1.18fr_0.82fr]">
          <div className="paper-panel bg-card px-6 py-8 sm:px-8">
            <div className="grid gap-8 lg:grid-cols-[0.74fr_1.26fr] lg:items-start">
              <div>
                <p className="editorial-kicker">System view</p>
                <h2 className="mt-4 font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
                  Three datasets, one readable operating surface.
                </h2>
                <p className="mt-6 text-base leading-8 text-muted sm:text-lg">
                  The home page introduces the logic of the system before the user enters the demo: multiple baseline models, one ensemble, and dataset-specific estimation paths rendered as a single narrative.
                </p>
              </div>

              <div className="archival-diagram min-h-[330px] border border-line/80 px-5 py-6 sm:px-6">
                <div className="relative z-10">
                  <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line/80 pb-4">
                    <div>
                      <p className="text-[0.68rem] uppercase tracking-[0.28em] text-muted">Preview plate</p>
                      <p className="mt-2 font-serif text-2xl tracking-editorial text-foreground">Model comparison ledger</p>
                    </div>
                    <div className="border border-line bg-card/80 px-4 py-3 text-right">
                      <p className="text-[0.68rem] uppercase tracking-[0.24em] text-muted">Best model</p>
                      <p className="mt-2 font-serif text-2xl text-foreground">Random Forest</p>
                    </div>
                  </div>

                  <div className="mt-6 space-y-4">
                    {previewRows.map((row) => (
                      <div key={row.label} className="space-y-2">
                        <div className="flex items-center justify-between gap-4 text-sm">
                          <span className="text-foreground">{row.label}</span>
                          <span className="font-medium text-muted">{row.value}</span>
                        </div>
                        <div className="h-2.5 border border-line bg-card/70">
                          <div className="h-full bg-accent" style={{ width: row.width }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-background px-6 py-8 sm:px-8">
            <p className="editorial-kicker">Signals</p>
            <div className="mt-6 space-y-5">
              {signalRows.map((row) => (
                <div key={row.label} className="border-b border-line/80 pb-5 last:border-b-0 last:pb-0">
                  <p className="text-[0.68rem] uppercase tracking-[0.26em] text-muted">{row.label}</p>
                  <p className="mt-3 font-serif text-2xl leading-tight tracking-editorial text-foreground">{row.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}