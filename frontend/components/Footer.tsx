export default function Footer() {
  return (
    <footer id="contact" className="bg-card/50">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-10">
        <div className="grid gap-px border border-line bg-line lg:grid-cols-[1.1fr_0.82fr_0.68fr]">
          <div className="paper-panel bg-background px-6 py-8 sm:px-8">
            <p className="font-serif text-3xl tracking-editorial text-foreground">SoftEstimate</p>
            <p className="mt-4 max-w-xl text-sm leading-7 text-muted">
              An editorially styled interface for exploring dataset-aware software effort predictions through a live FastAPI service.
            </p>
          </div>

          <div className="bg-card px-6 py-8 sm:px-8">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Tech stack</p>
            <p className="mt-4 text-sm leading-7 text-muted">Next.js · TypeScript · Tailwind CSS · FastAPI · ML ensemble models</p>
          </div>

          <div className="bg-background px-6 py-8 sm:px-8">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Next action</p>
            <a href="#demo" className="mt-4 inline-block font-serif text-2xl tracking-editorial text-foreground transition-colors hover:text-accent">
              Return to the demo
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}