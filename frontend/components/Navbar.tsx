"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, useRef } from "react";

const navItems = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/features" },
  { label: "Estimate", href: "/estimate" },
  { label: "Contact", href: "/contact" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    // Initial check
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-in-out ${
        scrolled
          ? "bg-primary shadow-md border-b border-transparent"
          : "bg-primary border-b border-transparent"
      }`}
    >
      <nav className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className={`flex items-center justify-between transition-all duration-300 ease-in-out ${scrolled ? "py-2" : "py-6"}`}>
          {/* Brand */}
          <Link
            href="/"
            className="shrink-0 flex items-center gap-2.5 group"
          >
            <img 
              src="/icon.png" 
              alt="SoftEstimate Logo" 
              className={`object-contain transition-all duration-300 ease-in-out ${scrolled ? "h-6 w-6" : "h-10 w-10"}`} 
            />
            <span className={`font-semibold tracking-[-0.02em] text-[#f3efe6] transition-all duration-300 ease-in-out ${scrolled ? "text-lg" : "text-xl"}`}>
              SoftEstimate
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href.replace("/#", "/"));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative px-4 py-2 text-[0.85rem] font-bold tracking-wide transition-colors duration-200 group
                    ${isActive
                      ? "text-white"
                      : "text-white/80 hover:text-white"
                    }`}
                >
                  {item.label}
                  <span className={`absolute left-4 right-4 bottom-1 h-[2px] bg-white transition-transform duration-300 origin-left ${isActive ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"}`} />
                </Link>
              );
            })}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Link href="/estimate" className="border-2 border-white bg-white text-primary hover:bg-primary hover:text-white text-[0.7rem] font-bold px-4 py-2 uppercase tracking-[0.1em] transition-colors duration-300 flex items-center gap-1.5">
              Get Started
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden flex flex-col gap-1.5 p-2"
            aria-label="Toggle menu"
          >
            <span className={`block h-0.5 w-5 bg-white transition-all duration-300 ${mobileOpen ? "rotate-45 translate-y-2" : ""}`} />
            <span className={`block h-0.5 w-5 bg-white transition-all duration-300 ${mobileOpen ? "opacity-0" : ""}`} />
            <span className={`block h-0.5 w-5 bg-white transition-all duration-300 ${mobileOpen ? "-rotate-45 -translate-y-2" : ""}`} />
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden pb-6 animate-fade-in">
            <div className="flex flex-col gap-1 mt-2">
              {navItems.map((item) => {
                const isActive =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname.startsWith(item.href.replace("/#", "/"));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={`relative w-fit px-4 py-3 text-sm font-bold transition-colors group
                      ${isActive ? "text-white" : "text-white/80 hover:text-white"}`}
                  >
                    {item.label}
                    <span className={`absolute left-4 right-4 bottom-2 h-[2px] bg-white transition-transform duration-300 origin-left ${isActive ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"}`} />
                  </Link>
                );
              })}
              <Link
                href="/estimate"
                onClick={() => setMobileOpen(false)}
                className="border-2 border-white bg-white text-primary hover:bg-primary hover:text-white mt-3 text-[0.7rem] font-bold px-4 py-2 uppercase tracking-[0.1em] transition-colors duration-300 text-center"
              >
                Get Started →
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}