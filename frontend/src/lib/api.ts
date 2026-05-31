/* Runtime API client for Veriq backend with session helpers. */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOKEN_KEY = "veriq.auth.token";
const WORKSPACE_KEY = "veriq.workspace.id";

let apiToken =
  import.meta.env.VITE_API_TOKEN ||
  (typeof window !== "undefined" ? window.localStorage.getItem(TOKEN_KEY) || "" : "");

function getStoredWorkspaceId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(WORKSPACE_KEY);
}

function setStoredWorkspaceId(workspaceId: string | null): void {
  if (typeof window === "undefined") return;
  if (workspaceId) {
    window.localStorage.setItem(WORKSPACE_KEY, workspaceId);
  } else {
    window.localStorage.removeItem(WORKSPACE_KEY);
  }
}

export function setAuthToken(token: string): void {
  apiToken = token;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearSession(): void {
  apiToken = "";
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(WORKSPACE_KEY);
  }
}

export function getAuthToken(): string {
  return apiToken;
}

export function setWorkspaceId(workspaceId: string | null): void {
  setStoredWorkspaceId(workspaceId);
}

export function getWorkspaceId(): string | null {
  return getStoredWorkspaceId();
}

function headers() {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (apiToken) h["Authorization"] = `Bearer ${apiToken}`;
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

export async function login(tenantSlug: string, email: string, password: string) {
  const payload = await request("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ tenant_slug: tenantSlug, email, password }),
  });
  if (payload?.access_token) setAuthToken(payload.access_token);
  return payload;
}

export async function registerTenantAdmin(payload: {
  tenantName: string;
  tenantSlug?: string;
  organizationName: string;
  workspaceName: string;
  email: string;
  fullName: string;
  password: string;
}) {
  return request("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({
      tenant_name: payload.tenantName,
      tenant_slug: payload.tenantSlug,
      organization_name: payload.organizationName,
      workspace_name: payload.workspaceName,
      email: payload.email,
      full_name: payload.fullName,
      password: payload.password,
    }),
  });
}

export async function listWorkspaces() {
  return request("/api/v1/workspaces");
}

export async function generateTestPlan(requirement: string, scenarioLimit = 3) {
  return request("/api/v1/ai/test-generation", {
    method: "POST",
    body: JSON.stringify({ requirement, scenario_limit: scenarioLimit }),
  });
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

export default {
  setAuthToken,
  getAuthToken,
  clearSession,
  setWorkspaceId,
  getWorkspaceId,
  login,
  registerTenantAdmin,
  listWorkspaces,
  generateTestPlan,
  listTestRuns,
  createTestRun,
  startTestRun,
  getTestRun,
  getRunSummary,
};
