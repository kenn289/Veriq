import React, { useState } from "react";
import api from "@/lib/api";

export default function TestPlanPage() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [target, setTarget] = useState("playwright-ts");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const workspaceId = api.getWorkspaceId();

  async function onGenerate() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.generateTestPlan(prompt);
      setResult(res);
    } catch (err: any) {
      setError(err?.message || "Failed to generate");
    } finally {
      setLoading(false);
    }
  }

  async function onGenerateCode() {
    if (!result) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.generateCode(result, workspaceId, target);
      if (res?.download_url) {
        // show persistent download link instead of immediate redirect
        setDownloadUrl(res.download_url);
      } else if (res instanceof Blob) {
        const url = window.URL.createObjectURL(res);
        const a = document.createElement("a");
        a.href = url;
        a.download = "generated_tests.zip";
        a.click();
        window.URL.revokeObjectURL(url);
      } else if (res) {
        // server might return blob as object
        const blob = new Blob([JSON.stringify(res)], { type: "application/json" });
        const url = window.URL.createObjectURL(blob);
        window.open(url, "_blank");
      }
    } catch (err: any) {
      setError(err?.message || "Failed to generate code");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold">Test Plan Generator</h1>
      <div className="mt-4 grid gap-3">
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Describe user flows..." className="h-40 w-full rounded-md border px-3 py-2"></textarea>
        <div className="flex gap-2 items-center">
          <button className="btn" onClick={onGenerate} disabled={loading}>
            {loading ? "Generating..." : "Generate"}
          </button>
          <select value={target} onChange={(e) => setTarget(e.target.value)} className="rounded-md border px-2 py-1">
            <option value="playwright-ts">Playwright (TypeScript)</option>
            <option value="pytest-playwright">Playwright (Python / pytest)</option>
          </select>
          <button className="btn" onClick={onGenerateCode} disabled={loading || !result}>
            {loading ? "Working..." : "Generate Code"}
          </button>
        </div>
        {error && <div className="text-red-400">{error}</div>}
        {result && (
          <pre className="mt-3 max-h-96 overflow-auto rounded-md bg-black/20 p-3">{JSON.stringify(result, null, 2)}</pre>
        )}
        {downloadUrl && (
          <div className="mt-3">
            <div>Generated artifact: <a className="text-blue-600 underline" href={downloadUrl} target="_blank" rel="noreferrer">Download ZIP</a></div>
          </div>
        )}
      </div>
    </div>
  );
}
