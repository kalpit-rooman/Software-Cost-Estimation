"use client";

import { useEffect, useState } from "react";
import {
  type AdminDiagnostics,
  type AdminState,
  clearAdminToken,
  fetchAdminDiagnostics,
  fetchAdminState,
  getAdminToken,
  patchAdminState,
  setAdminToken,
} from "@/lib/adminAuth";

// ---------------------------------------------------------------------------
// Inline small UI helpers
// ---------------------------------------------------------------------------

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-semibold uppercase tracking-editorial text-muted">
        {label}
      </label>
      {children}
    </div>
  );
}

function Select({
  value,
  onChange,
  options,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { label: string; value: string }[];
  disabled?: boolean;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className="border border-line rounded px-3 py-2 bg-card text-foreground text-sm disabled:opacity-50"
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

// ---------------------------------------------------------------------------
// Login form (shown when not authenticated)
// ---------------------------------------------------------------------------

function LoginForm({ onSuccess }: { onSuccess: (token: string) => void }) {
  const [key, setKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await fetchAdminState(key);
      setAdminToken(key);
      onSuccess(key);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      if (msg === "AUTH_FAILED") setError("Invalid admin key.");
      else if (msg === "ADMIN_NOT_CONFIGURED")
        setError("Admin access is not configured on the server (ADMIN_API_KEY not set).");
      else setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="paper-panel max-w-md mx-auto mt-24 p-8 flex flex-col gap-6">
      <div>
        <p className="editorial-kicker mb-1">Admin Access</p>
        <h2 className="text-xl font-semibold text-foreground">Enter admin key</h2>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Field label="Admin API Key">
          <input
            type="password"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder="Bearer token"
            required
            className="border border-line rounded px-3 py-2 bg-card text-foreground text-sm"
          />
        </Field>
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}
        <button
          type="submit"
          disabled={loading || !key}
          className="bg-foreground text-background rounded px-4 py-2 text-sm font-semibold disabled:opacity-50"
        >
          {loading ? "Verifying…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------------
// State editor (shown when authenticated)
// ---------------------------------------------------------------------------

function StateEditor({
  token,
  initial,
  diag,
  onLogout,
}: {
  token: string;
  initial: AdminState;
  diag: AdminDiagnostics | null;
  onLogout: () => void;
}) {
  const [state, setState] = useState<AdminState>(initial);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rateInput, setRateInput] = useState(String(initial.monthly_rate_inr));

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const updated = await patchAdminState(token, {
        ...state,
        monthly_rate_inr: parseFloat(rateInput) || state.monthly_rate_inr,
      });
      setState(updated);
      setRateInput(String(updated.monthly_rate_inr));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto mt-16 flex flex-col gap-8 px-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="editorial-kicker mb-1">Runtime Configuration</p>
          <h1 className="text-2xl font-semibold text-foreground">Admin Dashboard</h1>
        </div>
        <button
          onClick={onLogout}
          className="text-sm text-muted hover:text-foreground underline"
        >
          Sign out
        </button>
      </div>

      {/* Diagnostics banner */}
      {diag && (
        <div className="paper-panel p-4 flex flex-col gap-1 text-sm">
          <p className="font-semibold text-foreground">System status: {diag.status}</p>
          <p className="text-muted">
            Model service loaded:{" "}
            <span className={diag.model_service_loaded ? "text-green-600" : "text-yellow-600"}>
              {diag.model_service_loaded ? "Yes" : "No (will use AI fallback)"}
            </span>
          </p>
        </div>
      )}

      {/* State editor form */}
      <form onSubmit={handleSave} className="paper-panel p-6 flex flex-col gap-6">
        <Field label="Prediction mode">
          <Select
            value={state.prediction_mode}
            onChange={(v) => setState((s) => ({ ...s, prediction_mode: v as AdminState["prediction_mode"] }))}
            options={[
              { label: "Model (ML ensemble)", value: "model" },
              { label: "AI (language model)", value: "ai" },
            ]}
          />
        </Field>

        <Field label="AI provider">
          <Select
            value={state.ai_provider}
            onChange={(v) => setState((s) => ({ ...s, ai_provider: v }))}
            options={[
              { label: "OpenAI", value: "openai" },
              { label: "Gemini", value: "gemini" },
              { label: "Groq", value: "groq" },
            ]}
            disabled={state.prediction_mode !== "ai"}
          />
        </Field>

        <Field label="Prompt profile">
          <Select
            value={state.ai_profile}
            onChange={(v) => setState((s) => ({ ...s, ai_profile: v as AdminState["ai_profile"] }))}
            options={[
              { label: "Conservative (lower estimates)", value: "conservative" },
              { label: "Balanced (default)", value: "balanced" },
              { label: "Optimistic (higher estimates)", value: "optimistic" },
            ]}
            disabled={state.prediction_mode !== "ai"}
          />
        </Field>

        <Field label="Monthly rate per person (INR)">
          <input
            type="number"
            min={1}
            step={1000}
            value={rateInput}
            onChange={(e) => setRateInput(e.target.value)}
            className="border border-line rounded px-3 py-2 bg-card text-foreground text-sm"
          />
        </Field>

        <Field label="Default display currency (ISO-4217)">
          <Select
            value={state.default_currency}
            onChange={(v) => setState((s) => ({ ...s, default_currency: v }))}
            options={["INR", "USD", "EUR", "GBP", "AUD", "CAD", "JPY", "SGD", "AED"].map((c) => ({
              label: c,
              value: c,
            }))}
          />
        </Field>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={saving}
            className="bg-foreground text-background rounded px-5 py-2 text-sm font-semibold disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save changes"}
          </button>
          {saved && <span className="text-sm text-green-600">Saved ✓</span>}
        </div>
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export default function AdminDashboard() {
  const [token, setToken] = useState<string | null>(null);
  const [adminState, setAdminState] = useState<AdminState | null>(null);
  const [diag, setDiag] = useState<AdminDiagnostics | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore token from sessionStorage on mount
  useEffect(() => {
    const stored = getAdminToken();
    if (!stored) {
      setLoading(false);
      return;
    }
    // Validate stored token against backend
    Promise.all([fetchAdminState(stored), fetchAdminDiagnostics(stored)])
      .then(([s, d]) => {
        setToken(stored);
        setAdminState(s);
        setDiag(d);
      })
      .catch(() => {
        // Token expired / invalid – clear and show login
        clearAdminToken();
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleLogin(t: string) {
    const [s, d] = await Promise.all([fetchAdminState(t), fetchAdminDiagnostics(t)]);
    setToken(t);
    setAdminState(s);
    setDiag(d);
  }

  function handleLogout() {
    clearAdminToken();
    setToken(null);
    setAdminState(null);
    setDiag(null);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted text-sm">Loading…</p>
      </div>
    );
  }

  if (!token || !adminState) {
    return <LoginForm onSuccess={handleLogin} />;
  }

  return (
    <StateEditor
      token={token}
      initial={adminState}
      diag={diag}
      onLogout={handleLogout}
    />
  );
}
