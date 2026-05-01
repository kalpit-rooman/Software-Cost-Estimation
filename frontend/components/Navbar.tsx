const navItems = [
  { label: "Home", href: "#home" },
  { label: "Features", href: "#features" },
  { label: "Demo", href: "#demo" },
  { label: "About", href: "#about" },
  { label: "Contact", href: "#contact" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-transparent backdrop-blur-md">
      <nav className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className="flex items-center py-5">
          {/* Brand — left */}
          <a href="#home" className="shrink-0 font-serif text-2xl tracking-[-0.03em] text-foreground transition-colors hover:text-accent">
            SoftEstimate
          </a>

          {/* Nav links — center */}
          <div className="flex flex-1 items-center justify-center gap-7">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="relative pb-0.5 text-sm uppercase tracking-[0.16em] text-muted transition-colors hover:text-foreground
                  after:absolute after:bottom-0 after:left-0 after:h-px after:w-0 after:bg-foreground
                  after:transition-[width] after:duration-300 hover:after:w-full"
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* CTA — right */}
          <a
            href="#demo"
            className="shrink-0 border border-foreground px-5 py-2 text-sm uppercase tracking-[0.18em] text-foreground
              transition-all duration-300 hover:bg-foreground hover:text-background"
          >
            Demo
          </a>
        </div>
      </nav>
    </header>
  );
}