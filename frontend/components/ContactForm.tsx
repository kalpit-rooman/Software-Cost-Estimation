"use client";

import { FormEvent, useState } from "react";

const contactReasons = [
  "General inquiry",
  "Bug report",
  "Feature request",
  "Academic collaboration",
  "Other",
];

type FormState = {
  name: string;
  email: string;
  reason: string;
  message: string;
};

const INITIAL_FORM: FormState = {
  name: "",
  email: "",
  reason: contactReasons[0],
  message: "",
};

export default function ContactForm() {
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  function handleField(field: keyof FormState, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 900));
    setSubmitting(false);
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center text-center gap-5 py-8 animate-fade-in-up">
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </span>
        <h3 className="font-serif text-2xl text-foreground">
          Thanks, {form.name.split(" ")[0] || "there"}!
        </h3>
        <p className="text-sm text-muted max-w-sm">
          Your message has been received. We&apos;ll follow up via email if needed.
        </p>
        <button
          onClick={() => { setSubmitted(false); setForm(INITIAL_FORM); }}
          className="btn-secondary mt-2"
        >
          Send another
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-5 sm:grid-cols-2">
        <label className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Full name *</span>
          <input type="text" required value={form.name}
            onChange={(e) => handleField("name", e.target.value)}
            placeholder="Your name" className="input-field" />
        </label>
        <label className="space-y-2">
          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Email *</span>
          <input type="email" required value={form.email}
            onChange={(e) => handleField("email", e.target.value)}
            placeholder="you@example.com" className="input-field" />
        </label>
      </div>

      <label className="block space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Reason</span>
        <select value={form.reason} onChange={(e) => handleField("reason", e.target.value)} className="input-field">
          {contactReasons.map((r) => (<option key={r} value={r}>{r}</option>))}
        </select>
      </label>

      <label className="block space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Message *</span>
        <textarea required value={form.message}
          onChange={(e) => handleField("message", e.target.value)}
          placeholder="Describe your question or feedback…"
          className="input-field min-h-[160px] resize-y" />
      </label>

      <div className="flex flex-wrap items-center gap-4 pt-2">
        <button type="submit" disabled={submitting} className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
          {submitting ? "Sending…" : "Send Message"}
        </button>
        <p className="text-xs text-muted">Fields marked * are required.</p>
      </div>
    </form>
  );
}
