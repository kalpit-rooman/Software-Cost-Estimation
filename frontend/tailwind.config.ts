import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--background) / <alpha-value>)",
        foreground: "rgb(var(--foreground) / <alpha-value>)",
        muted:      "rgb(var(--muted) / <alpha-value>)",
        line:       "rgb(var(--line) / <alpha-value>)",
        card:       "rgb(var(--card) / <alpha-value>)",
        primary:    "rgb(var(--primary) / <alpha-value>)",
        secondary:  "rgb(var(--secondary) / <alpha-value>)",
        gold:       "rgb(var(--gold) / <alpha-value>)",
        teal:       "rgb(var(--teal) / <alpha-value>)",
        accent:     "rgb(var(--accent) / <alpha-value>)",
        accentSoft: "rgb(var(--accent-soft) / <alpha-value>)",
      },
      fontFamily: {
        sans:  ["var(--font-sans)", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
      },
      letterSpacing: {
        editorial: "-0.04em",
      },
      borderRadius: {
        xl:  "0.875rem",
        "2xl": "1.25rem",
      },
    },
  },
  plugins: [],
};

export default config;