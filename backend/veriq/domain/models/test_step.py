from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TestStep:
    """Description: Domain model for test step.
    Usage Example:
        step = TestStep(test_case_id="...", action="click", order=1)
    """

    test_case_id: str
    action: str
    order: int
    target: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
