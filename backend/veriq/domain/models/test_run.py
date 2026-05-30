from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestRun:
    """Description: Domain model for test run.
    Usage Example:
        run = TestRun(workspace_id="...", name="Nightly Run")
    """

    workspace_id: str
    name: str
    status: str = "pending"
    total_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    error_count: int = 0
    duration_seconds: int = 0
    id: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
