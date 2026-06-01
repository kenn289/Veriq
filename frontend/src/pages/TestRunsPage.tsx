import React from "react";
import TestRuns from "@/components/TestRuns";

export default function TestRunsPage({ workspaceId }: { workspaceId?: string }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Test Runs</h1>
      <div className="mt-4">
        <TestRuns workspaceId={workspaceId} />
      </div>
    </div>
  );
}
