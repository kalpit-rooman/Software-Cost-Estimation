/**
 * Admin API helpers (Phase 9).
 *
 * All admin calls require a bearer token stored in sessionStorage so it
 * is cleared when the tab is closed.
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

const TOKEN_KEY = "admin_token";

// ---------------------------------------------------------------------------
// Token management (sessionStorage – cleared on tab close)
// ---------------------------------------------------------------------------

export function getAdminToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setAdminToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearAdminToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// Admin state types (mirror backend AdminStateResponse)
// ---------------------------------------------------------------------------

export type AdminState = {
  prediction_mode: "ai" | "model";
  ai_provider: string;
  ai_profile: "conservative" | "balanced" | "optimistic";
  monthly_rate_inr: number;
  default_currency: string;
};

export type AdminStateUpdate = Partial<AdminState>;

export type AdminDiagnostics = AdminState & {
  status: string;
  model_service_loaded: boolean;
};

// ---------------------------------------------------------------------------
// Fetch helpers
// ---------------------------------------------------------------------------

async function adminFetch<T>(
  path: string,
  token: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers ?? {}),
    },
  });
  if (res.status === 401) throw new Error("AUTH_FAILED");
  if (res.status === 503) throw new Error("ADMIN_NOT_CONFIGURED");
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function fetchAdminState(token: string): Promise<AdminState> {
  return adminFetch<AdminState>("/admin/state", token);
}

export async function patchAdminState(
  token: string,
  update: AdminStateUpdate,
): Promise<AdminState> {
  return adminFetch<AdminState>("/admin/state", token, {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}

export async function fetchAdminDiagnostics(token: string): Promise<AdminDiagnostics> {
  return adminFetch<AdminDiagnostics>("/admin/diagnostics", token);
}
