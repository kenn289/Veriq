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

export default function TestRuns({ workspaceId = "default" }: { workspaceId?: string }) {
  const [runs, setRuns] = useState<TestRun[]>([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<TestRun | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await api.listTestRuns(workspaceId);
      setRuns(data || []);
    } catch (e) {
      console.error("Failed to load runs", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate() {
    if (!name) return;
    setLoading(true);
    try {
      await api.createTestRun(name, workspaceId);
      setName("");
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function openDetails(id: string) {
    try {
      const detail = await api.getTestRun(id);
      setSelected(detail);
    } catch (e) {
      console.error("Failed to load details", e);
    }
  }

  async function handleStart(id: string) {
    try {
      await api.startTestRun(id);
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
          }
        } catch (e) {
          clearInterval(interval);
          load();
        }
      }, 2000);
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div className="mt-8 rounded-xl border border-paper/10 bg-paper/5 p-6">
      <h3 className="font-display text-lg">Test Runs</h3>
      <div className="mt-4 flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New test run name"
          className="rounded-md px-3 py-2 bg-ink/5 border border-paper/8 flex-1"
        />
        <Button onClick={handleCreate} disabled={loading || !name}>
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
                  <Button variant="outline" onClick={() => handleStart(r.id)} disabled={r.status === "in_progress"}>
                    Start
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
                {(selected.results || []).map((res) => (
                  <div key={res.id} className="rounded-md border border-paper/8 p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{res.test_case_id}</div>
                        <div className="text-xs text-paper/60">{res.status} — {res.attempts} attempts</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {res.failure_screenshot ? (
                          <a href={res.failure_screenshot} target="_blank" rel="noreferrer" className="text-sm text-mint/90">
                            View screenshot
                          </a>
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
