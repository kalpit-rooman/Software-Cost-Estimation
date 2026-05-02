import Link from "next/link";

const footerLinks = [
  { label: "Home", href: "/" },
  { label: "Estimate", href: "/estimate" },
  { label: "Contact", href: "/contact" },
  { label: "Admin", href: "/admin" },
];

const techStack = ["Next.js 15", "FastAPI", "Random Forest", "XGBoost", "COCOMO · Desharnais · China"];

export default function Footer() {
  return (
    <footer className="bg-foreground text-white/70">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-10">
        <div className="grid gap-12 lg:grid-cols-[1.4fr_0.8fr_0.8fr]">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2.5">
              <img src="/icon.png" alt="SoftEstimate Logo" className="h-9 w-9 object-contain" />
              <span className="font-serif text-xl text-white">SoftEstimate</span>
            </div>
            <p className="mt-5 max-w-md text-sm leading-7 text-white/50">
              An ML-powered software effort and cost estimation tool trained on
              three industry datasets — COCOMO-81, Desharnais, and China.
            </p>
          </div>

          {/* Links */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/40">
              Pages
            </p>
            <ul className="mt-5 space-y-3">
              {footerLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-white/60 transition-colors hover:text-gold"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Tech */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/40">
              Tech Stack
            </p>
            <ul className="mt-5 space-y-3">
              {techStack.map((item) => (
                <li key={item} className="text-sm text-white/50">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-8 sm:flex-row">
          <p className="text-xs text-white/30">
            © {new Date().getFullYear()} SoftEstimate. Built for academic and professional cost estimation.
          </p>
          <div className="flex items-center gap-1 text-xs text-white/30">
            <span className="h-1.5 w-1.5 rounded-full bg-primary" />
            <span>All systems operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
}