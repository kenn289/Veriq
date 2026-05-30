from __future__ import annotations

from pydantic import BaseModel, Field


class TestRunCreateRequest(BaseModel):
    """Description: Request schema for creating a test run.
    Usage Example:
        req = TestRunCreateRequest(name="Nightly Run")
    """

    name: str = Field(..., min_length=1, max_length=255)


class TestResultReportRequest(BaseModel):
    """Description: Request schema for reporting a test result.
    Usage Example:
        req = TestResultReportRequest(test_case_id="...", status="passed")
    """

    test_case_id: str
    status: str = Field(..., pattern="^(passed|failed|error|skipped)$")
    duration_seconds: int = Field(0, ge=0)
    error_message: str | None = Field(None, max_length=5000)
    error_stack_trace: str | None = Field(None, max_length=50000)
    failure_step_id: str | None = None
    failure_screenshot: str | None = Field(None, max_length=500)


class TestResultResponse(BaseModel):
    """Description: Response schema for test result.
    Usage Example:
        resp = TestResultResponse.model_validate(result_obj)
    """

    id: str
    test_run_id: str
    test_case_id: str
    status: str
    duration_seconds: int
    error_message: str | None
    attempts: int
    created_at: str


class TestRunResponse(BaseModel):
    """Description: Response schema for test run.
    Usage Example:
        resp = TestRunResponse.model_validate(test_run_obj)
    """

    id: str
    workspace_id: str
    name: str
    status: str
    total_count: int
    passed_count: int
    failed_count: int
    error_count: int
    duration_seconds: int
    started_at: str | None
    completed_at: str | None
    created_at: str
    updated_at: str


class TestRunDetailResponse(BaseModel):
    """Description: Response schema for test run with results.
    Usage Example:
        resp = TestRunDetailResponse.model_validate(test_run_with_results)
    """

    id: str
    workspace_id: str
    name: str
    status: str
    total_count: int
    passed_count: int
    failed_count: int
    error_count: int
    duration_seconds: int
    started_at: str | None
    completed_at: str | None
    results: list[TestResultResponse]
    created_at: str
    updated_at: str


class TestRunSummaryResponse(BaseModel):
    """Description: Response schema for test run summary.
    Usage Example:
        resp = TestRunSummaryResponse.model_validate(summary_dict)
    """

    total: int
    passed: int
    failed: int
    error: int
    skipped: int
