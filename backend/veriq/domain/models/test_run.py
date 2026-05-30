from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
    id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
