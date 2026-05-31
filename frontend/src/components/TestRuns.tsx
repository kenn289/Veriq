import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import api from "@/lib/api";

type TestResult = {
  id: string;
  test_run_id: string;
  test_case_id: string;
  status: string;
  duration_seconds: number;
  error_message?: string | null;
  failure_screenshot?: string | null;
  attempts: number;
  created_at: string;
};

type TestRun = {
  id: string;
  name: string;
  status: string;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  results?: TestResult[];
};

export default function TestRuns({ workspaceId }: { workspaceId?: string }) {
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<TestRun | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [startingRunId, setStartingRunId] = useState<string | null>(null);

  function formatError(e: unknown): string {
    if (e instanceof Error) return e.message;
    return "Request failed";
  }

  async function load() {
    if (!workspaceId) {
      setRuns([]);
      setSelected(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await api.listTestRuns(workspaceId);
      setRuns(data || []);
    } catch (e) {
      setError(formatError(e));
      console.error("Failed to load runs", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [workspaceId]);

  async function handleCreate() {
    if (!name || !workspaceId) return;
    setLoading(true);
    setError(null);
    setNotice(null);
    try {
      const created = await api.createTestRun(name, workspaceId);
      setName("");
      setNotice(`Created test run: ${created?.name || "Untitled"}`);
      await load();
    } catch (e) {
      setError(formatError(e));
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function openDetails(id: string) {
    setError(null);
    setNotice(null);
    try {
      const detail = await api.getTestRun(id);
      setSelected(detail);
      if (!detail.results || detail.results.length === 0) {
        setNotice("This run has no test results yet. Add test cases to this workspace, then run again.");
      }
    } catch (e) {
      setError(formatError(e));
      console.error("Failed to load details", e);
    }
  }

  async function handleStart(id: string) {
    if (!workspaceId) return;
    setError(null);
    setNotice(null);
    setStartingRunId(id);
    try {
      await api.startTestRun(id);
      setNotice("Run started. Tracking progress...");
      // optimistic update
      setRuns((r) => r.map((x) => (x.id === id ? { ...x, status: "in_progress" } : x)));

      // poll run details until completed
      const interval = setInterval(async () => {
        try {
          const detail = await api.getTestRun(id);
          // update list and selected view
          setRuns((rs) => rs.map((x) => (x.id === id ? { ...x, status: detail.status } : x)));
          if (selected && selected.id === id) setSelected(detail);
          if (detail.status && detail.status !== "in_progress") {
            clearInterval(interval);
            load();
            setSelected(detail);
            if (!detail.results || detail.results.length === 0) {
              setNotice("Run completed, but no test cases were found in this workspace.");
            } else {
              setNotice(`Run completed with ${detail.results.length} result(s).`);
            }
            setStartingRunId(null);
          }
        } catch (e) {
          setError(formatError(e));
          clearInterval(interval);
          load();
          setStartingRunId(null);
        }
      }, 2000);
    } catch (e) {
      setError(formatError(e));
      console.error(e);
      setStartingRunId(null);
    }
  }

  return (
    <div className="mt-8 rounded-xl border border-paper/10 bg-paper/5 p-6">
      <h3 className="font-display text-lg">Test Runs</h3>
      <p className="mt-2 text-xs text-paper/60">
        API workspace: <span className="text-paper/80">{workspaceId || "Not selected"}</span>
      </p>
      {!workspaceId ? (
        <div className="mt-3 rounded-md border border-amber-400/40 bg-amber-500/10 p-3 text-sm text-amber-100">
          Select a workspace after login to create and run tests.
        </div>
      ) : null}
      {error ? (
        <div className="mt-3 rounded-md border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}
      {notice ? (
        <div className="mt-3 rounded-md border border-emerald-400/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
          {notice}
        </div>
      ) : null}
      <div className="mt-4 flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New test run name"
          className="rounded-md px-3 py-2 bg-ink/5 border border-paper/8 flex-1"
          disabled={!workspaceId}
        />
        <Button onClick={handleCreate} disabled={loading || !name || !workspaceId}>
          Create
        </Button>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div>
          {loading ? (
            <div>Loading...</div>
          ) : runs.length === 0 ? (
            <div className="text-sm text-paper/70">No runs found.</div>
          ) : (
            runs.map((r) => (
              <div key={r.id} className="flex items-center justify-between gap-4 rounded-md border border-paper/6 p-3">
                <div>
                  <div className="font-medium">{r.name}</div>
                  <div className="text-xs text-paper/60">{new Date(r.created_at).toLocaleString()}</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-sm text-paper/70">{r.status}</div>
                  <Button
                    variant="outline"
                    onClick={() => handleStart(r.id)}
                    disabled={r.status === "in_progress" || startingRunId === r.id}
                  >
                    {startingRunId === r.id ? "Starting..." : "Start"}
                  </Button>
                  <Button variant="outline" onClick={() => openDetails(r.id)}>
                    Details
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>

        <div>
          {selected ? (
            <div className="rounded-md border border-paper/6 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-medium">{selected.name}</div>
                  <div className="text-xs text-paper/60">Status: {selected.status}</div>
                </div>
                <div>
                  <Button variant="outline" onClick={() => setSelected(null)}>
                    Close
                  </Button>
                </div>
              </div>

              <div className="mt-4 space-y-3">
                {(selected.results || []).length === 0 ? (
                  <div className="rounded-md border border-paper/8 p-3 text-sm text-paper/60">
                    No results for this run yet. Create test cases in this workspace, then click Start.
                  </div>
                ) : null}
                {(selected.results || []).map((res) => (
                  <div key={res.id} className="rounded-md border border-paper/8 p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{res.test_case_id}</div>
                        <div className="text-xs text-paper/60">{res.status} — {res.attempts} attempts</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {res.failure_screenshot ? (
                          <div className="flex items-center gap-2">
                            <a href={res.failure_screenshot} target="_blank" rel="noreferrer">
                              <img src={res.failure_screenshot} alt="screenshot" className="w-24 h-auto rounded-md border" />
                            </a>
                            <a href={res.failure_screenshot} target="_blank" rel="noreferrer" className="text-sm text-mint/90">
                              Open
                            </a>
                            <a href={res.failure_screenshot} download className="text-sm text-paper/70">
                              Download
                            </a>
                          </div>
                        ) : null}
                        {res.error_message ? <div className="text-xs text-paper/60">{res.error_message}</div> : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-sm text-paper/60">Select a run to view results.</div>
          )}
        </div>
      </div>
    </div>
  );
}
