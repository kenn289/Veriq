import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button } from "@/components/ui/button";
import TestRuns from "@/components/TestRuns";

const executionData = [
  { name: "Mon", executions: 120, passRate: 97 },
  { name: "Tue", executions: 180, passRate: 95 },
  { name: "Wed", executions: 210, passRate: 96 },
  { name: "Thu", executions: 170, passRate: 94 },
  { name: "Fri", executions: 260, passRate: 98 },
  { name: "Sat", executions: 90, passRate: 99 },
  { name: "Sun", executions: 140, passRate: 97 },
];

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
  const scrollToRuns = () => {
    document.getElementById("test-runs-section")?.scrollIntoView({
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
                <span>Locator stability</span>
                <span className="text-paper">98.2%</span>
              </div>
              <div className="flex items-center justify-between">
                <span>AI defect confidence</span>
                <span className="text-paper">0.91</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Risk trend</span>
                <span className="text-paper">Improving</span>
              </div>
            </div>
          </section>
        </main>
      </div>

      <section id="test-runs-section" className="mx-auto max-w-6xl px-6 pb-20">
        <TestRuns workspaceId={import.meta.env.VITE_WORKSPACE_ID || "default"} />
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
