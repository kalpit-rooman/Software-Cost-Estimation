import DemoSection from "@/components/DemoSection";
import Features from "@/components/Features";
import Footer from "@/components/Footer";
import Hero from "@/components/Hero";
import Navbar from "@/components/Navbar";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="overflow-hidden">
        <Hero />
        <Features />
        <DemoSection />
        <section id="about" className="border-y border-line/80 bg-card/20">
          <div className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
            <div className="grid gap-px border border-line bg-line lg:grid-cols-[0.88fr_1.12fr]">
              <div className="paper-panel bg-background px-6 py-8 sm:px-8">
                <p className="editorial-kicker">About</p>
                <h2 className="mt-4 max-w-md font-serif text-4xl tracking-editorial text-foreground sm:text-5xl">
                  A decision brief, not just a utility screen.
                </h2>
                <p className="mt-8 max-w-lg font-serif text-2xl leading-snug tracking-editorial text-foreground sm:text-3xl">
                  The interface frames machine learning output as something to inspect, compare, and trust deliberately.
                </p>
                <p className="mt-8 border-t border-line/80 pt-4 text-sm leading-7 text-muted">
                  Built for software-cost estimation workflows that need a premium first impression without turning the live demo into a marketing mockup.
                </p>
              </div>

              <div className="bg-card px-6 py-8 sm:px-8">
                <div className="grid gap-8 lg:grid-cols-[1fr_0.72fr] lg:items-start">
                  <div className="space-y-5 text-base leading-8 text-muted sm:text-lg">
                    <p>
                      This frontend connects a Next.js interface to a FastAPI prediction service that evaluates project effort across multiple machine learning models and produces an ensemble estimate as the primary readout.
                    </p>
                    <p>
                      Each dataset represents a different estimation context. The demo keeps the form intentionally compact, then translates those inputs into valid feature proxies so the backend can return a working prediction instead of a static mock response.
                    </p>
                    <p>
                      The result is a home page that feels closer to an analytical publication than a generic startup landing page, while still functioning as the real entry point into the estimator.
                    </p>
                  </div>

                  <div className="space-y-px border border-line bg-line">
                    <div className="bg-background px-5 py-5">
                      <p className="text-xs uppercase tracking-[0.24em] text-muted">Models</p>
                      <p className="mt-3 text-sm leading-7 text-muted">Random Forest, XGBoost, and Linear Regression contribute to the final ensemble estimate.</p>
                    </div>
                    <div className="bg-background px-5 py-5">
                      <p className="text-xs uppercase tracking-[0.24em] text-muted">Delivery</p>
                      <p className="mt-3 text-sm leading-7 text-muted">Single-page frontend, typed API service layer, and responsive sections anchored for fast navigation.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}