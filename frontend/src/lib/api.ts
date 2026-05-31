/* Simple API client for Veriq backend. Uses Vite env vars for configuration. */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_TOKEN = import.meta.env.VITE_API_TOKEN || "";

function headers() {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (API_TOKEN) h["Authorization"] = `Bearer ${API_TOKEN}`;
  return h;
}

async function request(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { ...headers(), ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} - ${text}`);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res.text();
}

export async function listTestRuns(workspaceId: string) {
  return request(`/api/v1/test_runs?workspace_id=${encodeURIComponent(workspaceId)}`);
}

export async function createTestRun(name: string, workspaceId: string) {
  return request(`/api/v1/test_runs?workspace_id=${encodeURIComponent(workspaceId)}`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function startTestRun(testRunId: string) {
  return request(`/api/v1/test_runs/${encodeURIComponent(testRunId)}/start`, {
    method: "POST",
  });
}

export async function getTestRun(testRunId: string) {
  return request(`/api/v1/test_runs/${encodeURIComponent(testRunId)}`);
}

export async function getRunSummary(testRunId: string) {
  return request(`/api/v1/test_runs/${encodeURIComponent(testRunId)}/summary`);
}

export default { listTestRuns, createTestRun, startTestRun, getTestRun, getRunSummary };
