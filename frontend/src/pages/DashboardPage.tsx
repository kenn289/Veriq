import React from "react";

export default function DashboardPage({ workspaceId }: { workspaceId?: string }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="mt-4 rounded-md border border-paper/8 p-4">
        <div className="font-medium">Execution Pulse</div>
        <div className="mt-2 text-sm text-paper/60">Workspace: {workspaceId || "Not selected"}</div>
        <div className="mt-3 text-sm text-paper/70">Live metrics coming soon.</div>
      </div>
    </div>
  );
}
