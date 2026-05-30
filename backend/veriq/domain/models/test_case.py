from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestCase:
    """Description: Domain model for test case.
    Usage Example:
        test = TestCase(name="Login", workspace_id="...", priority=1)
    """

    name: str
    workspace_id: str
    description: str | None = None
    slug: str | None = None
    status: str = "active"
    priority: int = 3
    id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
