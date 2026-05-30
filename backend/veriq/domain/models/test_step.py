from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestStep:
    """Description: Domain model for test step.
    Usage Example:
        step = TestStep(test_case_id="...", action="click", order=1)
    """

    test_case_id: str
    action: str
    order: int
    target: str | None = None
    value: str | None = None
    description: str | None = None
    id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
