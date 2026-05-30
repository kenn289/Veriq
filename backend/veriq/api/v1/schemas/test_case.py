from __future__ import annotations

from pydantic import BaseModel, Field


class TestCaseCreateRequest(BaseModel):
    """Description: Request schema for creating a test case.
    Usage Example:
        req = TestCaseCreateRequest(name="Login", priority=1)
    """

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    priority: int = Field(3, ge=1, le=5)


class TestStepCreateRequest(BaseModel):
    """Description: Request schema for adding a test step.
    Usage Example:
        step = TestStepCreateRequest(action="click", target="button.login")
    """

    action: str = Field(..., min_length=1, max_length=100)
    target: str | None = Field(None, max_length=500)
    value: str | None = Field(None, max_length=1000)
    description: str | None = Field(None, max_length=5000)


class TestStepResponse(BaseModel):
    """Description: Response schema for test step.
    Usage Example:
        resp = TestStepResponse.model_validate(step_obj)
    """

    id: str
    action: str
    target: str | None
    value: str | None
    description: str | None
    order: int


class TestCaseResponse(BaseModel):
    """Description: Response schema for test case.
    Usage Example:
        resp = TestCaseResponse.model_validate(test_case_obj)
    """

    id: str
    workspace_id: str
    name: str
    description: str | None
    slug: str
    status: str
    priority: int
    created_at: str
    updated_at: str


class TestCaseDetailResponse(BaseModel):
    """Description: Response schema for test case with steps.
    Usage Example:
        resp = TestCaseDetailResponse.model_validate(test_case_with_steps)
    """

    id: str
    workspace_id: str
    name: str
    description: str | None
    slug: str
    status: str
    priority: int
    steps: list[TestStepResponse]
    created_at: str
    updated_at: str
