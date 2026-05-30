from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TestCase:
    """Description: Domain model for test case.
    Usage Example:
        test = TestCase(name="Login", workspace_id="...", priority=1)
    """

    name: str
    workspace_id: str
    description: Optional[str] = None
    slug: Optional[str] = None
    status: str = "active"
    priority: int = 3
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
