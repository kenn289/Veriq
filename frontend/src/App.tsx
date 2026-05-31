import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Button } from "@/components/ui/button";
import TestRuns from "@/components/TestRuns";
import api from "@/lib/api";

type Workspace = {
  id: string;
  name: string;
  slug: string;
  organization_id: string;
};

type TestRun = {
  id: string;
  name: string;
  status: string;
  created_at: string;
  passed_count: number;
  failed_count: number;
  error_count: number;
};

type PulsePoint = {
  name: string;
  executions: number;
  passRate: number;
};

const capabilityList = [
  "Requirement parsing and scenario design",
  "Framework and page object generation",
  "Execution with artifact capture",
  "Self-healing locators and risk prediction",
];

/**
 * Description: Render the Veriq landing page.
 * Parameters:
 *   None
 * Returns:
 *   JSX.Element: Landing page layout.
 * Usage Example:
 *   <App />
 */
export default function App(): JSX.Element {
  const [tenantSlug, setTenantSlug] = useState("demo5186");
  const [email, setEmail] = useState("admin+5186@demo.com");
  const [password, setPassword] = useState("DemoPass123!");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceIdState] = useState<string | undefined>(
    api.getWorkspaceId() || undefined,
  );

  const [requirement, setRequirement] = useState("");
  const [scenarioLimit, setScenarioLimit] = useState(3);
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const [planResult, setPlanResult] = useState<any | null>(null);

  const [pulseRuns, setPulseRuns] = useState<TestRun[]>([]);

  const isAuthed = Boolean(api.getAuthToken());

  function formatError(e: unknown): string {
    if (e instanceof Error) return e.message;
    return "Request failed";
  }

  async function loadWorkspaces() {
    const list = (await api.listWorkspaces()) as Workspace[];
    setWorkspaces(list || []);
    if (!workspaceId && list.length > 0) {
      setWorkspaceIdState(list[0].id);
      api.setWorkspaceId(list[0].id);
    }
  }

  async function handleLogin() {
    setAuthLoading(true);
    setAuthError(null);
    try {
      await api.login(tenantSlug, email, password);
      await loadWorkspaces();
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
      await loadWorkspaces();
    } catch (e) {
      setAuthError(formatError(e));
    } finally {
      setAuthLoading(false);
    }
  }

  function handleLogout() {
    api.clearSession();
    setWorkspaces([]);
    setWorkspaceIdState(undefined);
    setPulseRuns([]);
    setPlanResult(null);
  }

  async function generatePlan() {
    if (!requirement.trim()) {
      setPlanError("Please enter a requirement before generating a plan.");
      return;
    }

    setPlanLoading(true);
    setPlanError(null);
    setPlanResult(null);
    try {
      const generated = await api.generateTestPlan(requirement.trim(), scenarioLimit);
      setPlanResult(generated);
      document.getElementById("plan-results")?.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (e) {
      setPlanError(formatError(e));
    } finally {
      setPlanLoading(false);
    }
  }

  useEffect(() => {
    if (!isAuthed) return;
    loadWorkspaces().catch((e) => setAuthError(formatError(e)));
  }, []);

  useEffect(() => {
    if (!isAuthed || !workspaceId) {
      setPulseRuns([]);
      return;
    }

    api
      .listTestRuns(workspaceId)
      .then((runs) => setPulseRuns((runs || []) as TestRun[]))
      .catch(() => setPulseRuns([]));
  }, [workspaceId, isAuthed]);

  const executionData: PulsePoint[] = useMemo(() => {
    const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const out: PulsePoint[] = labels.map((name) => ({ name, executions: 0, passRate: 0 }));

    for (const run of pulseRuns) {
      const d = new Date(run.created_at);
      const idx = (d.getDay() + 6) % 7;
      out[idx].executions += 1;
      if (run.status === "completed") {
        out[idx].passRate += 1;
      }
    }

    return out.map((x) => ({
      ...x,
      passRate: x.executions > 0 ? Math.round((x.passRate / x.executions) * 100) : 0,
    }));
  }, [pulseRuns]);

  const totalRuns = pulseRuns.length;
  const completedRuns = pulseRuns.filter((r) => r.status === "completed").length;
  const completionRate = totalRuns > 0 ? Math.round((completedRuns / totalRuns) * 100) : 0;
  const activeRuns = pulseRuns.filter((r) => r.status === "in_progress").length;

  const scrollToRuns = () => {
    if (!isAuthed) {
      setAuthError("Login first to generate test plans and run tests.");
      document.getElementById("auth-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    document.getElementById("plan-section")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  const openApiDocs = () => {
    window.open("http://localhost:8000/docs", "_blank", "noopener,noreferrer");
  };

  return (
    <div className="min-h-screen bg-ink text-paper">
      <div className="relative overflow-hidden">
        <div className="absolute -top-48 left-0 h-96 w-96 rounded-full bg-mint/30 blur-[140px]" />
        <div className="absolute right-0 top-24 h-96 w-96 rounded-full bg-amber/30 blur-[160px]" />

        <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-8 text-xs uppercase tracking-[0.3em]">
          <span className="font-display text-paper/70">Veriq</span>
          <span className="font-display text-paper/50">AI QA Platform</span>
        </header>

        <section id="auth-section" className="relative mx-auto max-w-6xl px-6 pb-6">
          <div className="rounded-2xl border border-paper/10 bg-paper/5 p-5">
            <div className="flex flex-wrap items-end gap-3">
              <div className="min-w-[180px] flex-1">
                <label className="mb-1 block text-xs text-paper/70">Tenant slug</label>
                <input
                  value={tenantSlug}
                  onChange={(e) => setTenantSlug(e.target.value)}
                  className="w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2"
                  placeholder="acme"
                />
              </div>
              <div className="min-w-[220px] flex-1">
                <label className="mb-1 block text-xs text-paper/70">Email</label>
                <input
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2"
                  placeholder="admin@acme.com"
                />
              </div>
              <div className="min-w-[180px] flex-1">
                <label className="mb-1 block text-xs text-paper/70">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2"
                  placeholder="********"
                />
              </div>
              {!isAuthed ? (
                <>
                  <Button
                    variant="outline"
                    onClick={handleRegister}
                    disabled={authLoading || !tenantSlug || !email || !password}
                  >
                    {authLoading ? "Creating..." : "Register"}
                  </Button>
                  <Button onClick={handleLogin} disabled={authLoading || !tenantSlug || !email || !password}>
                    {authLoading ? "Signing in..." : "Login"}
                  </Button>
                </>
              ) : (
                <Button variant="outline" onClick={handleLogout}>
                  Logout
                </Button>
              )}
            </div>

            {authError ? (
              <div className="mt-3 rounded-md border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-200">
                {authError}
              </div>
            ) : null}

            <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
              <span className="text-paper/70">Workspace</span>
              <select
                className="rounded-md border border-paper/10 bg-ink/40 px-3 py-2"
                value={workspaceId || ""}
                onChange={(e) => {
                  const value = e.target.value || undefined;
                  setWorkspaceIdState(value);
                  api.setWorkspaceId(value || null);
                }}
                disabled={!isAuthed || workspaces.length === 0}
              >
                <option value="">Select workspace</option>
                {workspaces.map((ws) => (
                  <option key={ws.id} value={ws.id}>
                    {ws.name} ({ws.slug})
                  </option>
                ))}
              </select>
              {!isAuthed ? <span className="text-amber-200">Login required for private account data.</span> : null}
            </div>
          </div>
        </section>

        <main className="relative mx-auto grid max-w-6xl gap-10 px-6 pb-20 md:grid-cols-[1.1fr_0.9fr]">
          <section className="animate-[floatIn_0.9s_ease-out] space-y-6">
            <p className="font-serif text-sm uppercase tracking-[0.4em] text-paper/70">
              From Natural Language to Production-Ready Test Automation
            </p>
            <h1 className="font-display text-4xl leading-tight md:text-5xl">
              Veriq orchestrates the full testing lifecycle with autonomous AI agents.
            </h1>
            <p className="text-lg text-paper/70">
              Turn a single requirement into scenarios, code, execution artifacts, and
              actionable quality intelligence without manual stitching.
            </p>
            <div className="flex flex-wrap gap-4">
              <Button variant="default" onClick={scrollToRuns}>
                Generate a test plan
              </Button>
              <Button variant="outline" onClick={openApiDocs}>
                Open API docs
              </Button>
            </div>
            <div className="grid gap-3 rounded-2xl border border-paper/10 bg-paper/5 p-5 shadow-glow">
              {capabilityList.map((item) => (
                <div key={item} className="flex items-center gap-3 text-paper/80">
                  <span className="h-2 w-2 rounded-full bg-mint" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="animate-[floatIn_1.1s_ease-out] rounded-3xl border border-paper/10 bg-paper/5 p-6 shadow-glow">
            <div className="mb-6">
              <p className="text-xs uppercase tracking-[0.3em] text-paper/60">
                Execution intelligence
              </p>
              <h2 className="font-display text-2xl">Weekly execution pulse</h2>
              <p className="mt-2 text-xs text-paper/60">
                {isAuthed && workspaceId
                  ? "Live data from your selected workspace"
                  : "Login + workspace selection required for private run metrics"}
              </p>
            </div>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={executionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="veriqMint" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" stroke="#e7e1d6" tickLine={false} axisLine={false} />
                  <YAxis hide />
                  <Tooltip
                    contentStyle={{
                      background: "#0b1416",
                      border: "1px solid rgba(243, 239, 232, 0.1)",
                      borderRadius: "12px",
                      color: "#f3efe8",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="executions"
                    stroke="#2dd4bf"
                    strokeWidth={2}
                    fill="url(#veriqMint)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 grid gap-4 text-sm text-paper/70">
              <div className="flex items-center justify-between">
                <span>Total runs (workspace)</span>
                <span className="text-paper">{totalRuns}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Completion rate</span>
                <span className="text-paper">{completionRate}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Active runs</span>
                <span className="text-paper">{activeRuns}</span>
              </div>
            </div>
          </section>
        </main>
      </div>

      <section id="plan-section" className="mx-auto max-w-6xl px-6 pb-10">
        <div className="rounded-2xl border border-paper/10 bg-paper/5 p-6">
          <h3 className="font-display text-xl">Generate Test Plan</h3>
          <p className="mt-2 text-sm text-paper/70">
            Convert a requirement into structured scenarios and executable step suggestions.
          </p>
          <textarea
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            className="mt-4 min-h-[110px] w-full rounded-md border border-paper/10 bg-ink/40 px-3 py-2"
            placeholder="Example: Users can log in, reset password, and view account dashboard."
          />
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <label className="text-sm text-paper/70">Scenario limit</label>
            <input
              type="number"
              min={1}
              max={5}
              value={scenarioLimit}
              onChange={(e) => setScenarioLimit(Number(e.target.value || 3))}
              className="w-24 rounded-md border border-paper/10 bg-ink/40 px-3 py-2"
            />
            <Button onClick={generatePlan} disabled={planLoading || !requirement.trim() || !isAuthed}>
              {planLoading ? "Generating..." : "Generate plan"}
            </Button>
            {!isAuthed ? <span className="text-xs text-amber-200">Login first to generate plans.</span> : null}
          </div>
          {planError ? (
            <div className="mt-3 rounded-md border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-200">
              {planError}
            </div>
          ) : null}
        </div>
      </section>

      {planResult ? (
        <section id="plan-results" className="mx-auto max-w-6xl px-6 pb-10">
          <div className="rounded-2xl border border-paper/10 bg-paper/5 p-6">
            <h3 className="font-display text-xl">Generated Plan</h3>
            <p className="mt-2 text-sm text-paper/70">{planResult.summary}</p>
            <div className="mt-4 space-y-3">
              {(planResult.scenarios || []).map((scenario: any, idx: number) => (
                <div key={`${scenario.name}-${idx}`} className="rounded-md border border-paper/10 p-4">
                  <div className="font-medium">{scenario.name}</div>
                  <div className="mt-1 text-sm text-paper/70">{scenario.description}</div>
                  <div className="mt-2 text-xs text-paper/60">Priority: {scenario.priority}</div>
                  <ul className="mt-3 list-disc pl-5 text-sm text-paper/80">
                    {(scenario.steps || []).map((step: any, i: number) => (
                      <li key={`${scenario.name}-step-${i}`}>
                        {step.order}. {step.action}
                        {step.target ? ` -> ${step.target}` : ""}
                        {step.value ? ` (${step.value})` : ""}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      <section id="test-runs-section" className="mx-auto max-w-6xl px-6 pb-20">
        <TestRuns workspaceId={workspaceId} />
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 pb-20 md:grid-cols-3">
        {[
          {
            title: "Autonomous planning",
            body: "Agents convert intent into strategies, test cases, and execution plans.",
          },
          {
            title: "Framework generation",
            body: "Produce production-grade scaffolds aligned with enterprise standards.",
          },
          {
            title: "Continuous healing",
            body: "Self-heal locators, classify failures, and keep suites evergreen.",
          },
        ].map((card) => (
          <div
            key={card.title}
            className="group rounded-2xl border border-paper/10 bg-paper/5 p-6 transition duration-300 hover:-translate-y-1 hover:border-mint/50"
          >
            <h3 className="font-display text-xl">{card.title}</h3>
            <p className="mt-2 text-sm text-paper/70">{card.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
