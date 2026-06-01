import { useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";

import { Button } from "@/components/ui/button";
import api from "@/lib/api";
import AuthPage from "@/pages/AuthPage";
import DashboardPage from "@/pages/DashboardPage";
import SubscriptionPage from "@/pages/SubscriptionPage";
import TestPlanPage from "@/pages/TestPlanPage";
import TestRunsPage from "@/pages/TestRunsPage";

export type Workspace = {
  id: string;
  name: string;
  slug: string;
  organization_id: string;
};

function ProtectedRoute({ isAuthed, children }: { isAuthed: boolean; children: JSX.Element }) {
  if (!isAuthed) return <Navigate to="/auth" replace />;
  return children;
}

export default function App(): JSX.Element {
  const [tenantSlug, setTenantSlug] = useState("demo5186");
  const [email, setEmail] = useState("admin+5186@demo.com");
  const [password, setPassword] = useState("DemoPass123!");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authed, setAuthed] = useState(Boolean(api.getAuthToken()));
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceId] = useState<string | undefined>(api.getWorkspaceId() || undefined);

  function formatError(e: unknown): string {
    if (e instanceof Error) return e.message;
    return "Request failed";
  }

  async function refreshWorkspaces() {
    const list = (await api.listWorkspaces()) as Workspace[];
    setWorkspaces(list || []);
    if (!workspaceId && list.length > 0) {
      setWorkspaceId(list[0].id);
      api.setWorkspaceId(list[0].id);
    }
  }

  async function handleLogin() {
    setAuthLoading(true);
    setAuthError(null);
    try {
      await api.login(tenantSlug, email, password);
      setAuthed(true);
      await refreshWorkspaces();
    } catch (e) {
      setAuthError(formatError(e));
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleRegister() {
    setAuthLoading(true);
    setAuthError(null);
    try {
      await api.registerTenantAdmin({
        tenantName: `${tenantSlug} Tenant`,
        tenantSlug,
        organizationName: "Default Org",
        workspaceName: "Default Workspace",
        email,
        fullName: "Workspace Admin",
        password,
      });
      await api.login(tenantSlug, email, password);
      setAuthed(true);
      await refreshWorkspaces();
    } catch (e) {
      setAuthError(formatError(e));
    } finally {
      setAuthLoading(false);
    }
  }

  function handleLogout() {
    api.clearSession();
    setAuthed(false);
    setAuthError(null);
    setWorkspaces([]);
    setWorkspaceId(undefined);
  }

  useEffect(() => {
    if (!authed) return;
    refreshWorkspaces().catch((e) => setAuthError(formatError(e)));
  }, [authed]);

  return (
    <div className="min-h-screen bg-ink text-paper">
      <div className="relative overflow-hidden">
        <div className="absolute -top-48 left-0 h-96 w-96 rounded-full bg-mint/30 blur-[140px]" />
        <div className="absolute right-0 top-24 h-96 w-96 rounded-full bg-amber/30 blur-[160px]" />

        <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <div>
            <div className="font-display text-xl">Veriq</div>
            <div className="text-xs uppercase tracking-[0.2em] text-paper/50">AI QA Platform</div>
          </div>
          <nav className="flex flex-wrap items-center gap-2 text-sm">
            <NavLink to="/dashboard" className="rounded-full border border-paper/15 px-4 py-2 hover:border-mint/60">
              Dashboard
            </NavLink>
            <NavLink to="/test-plan" className="rounded-full border border-paper/15 px-4 py-2 hover:border-mint/60">
              Test Plan
            </NavLink>
            <NavLink to="/test-runs" className="rounded-full border border-paper/15 px-4 py-2 hover:border-mint/60">
              Test Runs
            </NavLink>
            <NavLink to="/subscription" className="rounded-full border border-paper/15 px-4 py-2 hover:border-mint/60">
              Subscription
            </NavLink>
            {authed ? (
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            ) : (
              <NavLink to="/auth" className="rounded-full border border-paper/15 px-4 py-2 hover:border-mint/60">
                Login
              </NavLink>
            )}
          </nav>
        </header>

        <main className="relative mx-auto max-w-6xl px-6 pb-16">
          <Routes>
            <Route path="/" element={<Navigate to={authed ? "/dashboard" : "/auth"} replace />} />
            <Route
              path="/auth"
              element={
                <AuthPage
                  tenantSlug={tenantSlug}
                  email={email}
                  password={password}
                  setTenantSlug={setTenantSlug}
                  setEmail={setEmail}
                  setPassword={setPassword}
                  authLoading={authLoading}
                  authError={authError}
                  isAuthed={authed}
                  workspaces={workspaces}
                  workspaceId={workspaceId}
                  onWorkspaceChange={(value) => {
                    setWorkspaceId(value);
                    api.setWorkspaceId(value || null);
                  }}
                  onLogin={handleLogin}
                  onRegister={handleRegister}
                  onLogout={handleLogout}
                />
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute isAuthed={authed}>
                  <DashboardPage workspaceId={workspaceId} />
                </ProtectedRoute>
              }
            />
            <Route
              path="/test-plan"
              element={
                <ProtectedRoute isAuthed={authed}>
                  <TestPlanPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/test-runs"
              element={
                <ProtectedRoute isAuthed={authed}>
                  <TestRunsPage workspaceId={workspaceId} />
                </ProtectedRoute>
              }
            />
            <Route
              path="/subscription"
              element={
                <ProtectedRoute isAuthed={authed}>
                  <SubscriptionPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}
