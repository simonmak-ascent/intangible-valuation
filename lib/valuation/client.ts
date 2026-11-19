import type { ValuationResult, ApiError } from "./types";

// The calculator talks to the Python engine at /api/valuation, served by its own container behind
// the ALB. It used to post to /v1/valuation/<method>, which is a Next route that server-side fetched
// `${origin}/api/index.py` — a path Next does not serve — so every calculation returned a 404 HTML
// page rendered as the result. /v1/valuation/[method] no longer exists.
const API_BASE = "/api/valuation";

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  // An ALB 502/504 is an HTML page, not JSON. Without this the raw "Unexpected token '<'" reaches
  // the user as the calculation result — the same failure this module was fixed for.
  let data: unknown;
  try {
    data = await res.json();
  } catch {
    throw new Error(`API error: ${res.status} — the engine did not return JSON`);
  }

  if (!res.ok) {
    // A 4xx/5xx body of JSON null or a bare scalar is still an error — do not crash on it and turn
    // a TypeError into the result the user sees.
    const error = (data && typeof data === "object" ? data : {}) as ApiError;
    throw new Error(error.message || error.error || `API error: ${res.status}`);
  }

  return data as T;
}

export async function calculateValuation(
  method: string,
  params: Record<string, unknown>
): Promise<ValuationResult> {
  return apiFetch<ValuationResult>(`${API_BASE}/${method}`, {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export { API_BASE };
