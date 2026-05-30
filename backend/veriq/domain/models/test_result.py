from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TestResult:
    """Description: Domain model for test result.
    Usage Example:
        result = TestResult(test_run_id="...", status="passed")
    """

    test_run_id: str
    test_case_id: str
    status: str
    duration_seconds: int = 0
    error_message: Optional[str] = None
    error_stack_trace: Optional[str] = None
    failure_step_id: Optional[str] = None
    failure_screenshot: Optional[str] = None
    attempts: int = 1
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
