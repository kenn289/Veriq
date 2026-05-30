from __future__ import annotations

from dataclasses import dataclass


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
    error_message: str | None = None
    error_stack_trace: str | None = None
    failure_step_id: str | None = None
    failure_screenshot: str | None = None
    attempts: int = 1
    id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
