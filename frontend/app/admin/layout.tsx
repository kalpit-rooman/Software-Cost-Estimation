import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Admin – Software Cost Estimator",
  robots: { index: false, follow: false },
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-line px-6 py-3 flex items-center gap-3">
        <span className="text-xs font-semibold uppercase tracking-editorial text-muted">
          Software Cost Estimator
        </span>
        <span className="text-muted opacity-40">›</span>
        <span className="text-xs font-semibold uppercase tracking-editorial text-foreground">
          Admin
        </span>
      </header>
      <main className="pb-24">{children}</main>
    </div>
  );
}
