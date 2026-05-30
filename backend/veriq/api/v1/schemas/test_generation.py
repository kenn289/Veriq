from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratedStepResponse(BaseModel):
    """Description: Response schema for a generated step.
    Usage Example:
        step = GeneratedStepResponse(order=1, action="navigate", target="/login")
    """

    order: int
    action: str
    target: str | None = None
    value: str | None = None
    description: str | None = None


class GeneratedScenarioResponse(BaseModel):
    """Description: Response schema for a generated scenario.
    Usage Example:
        scenario = GeneratedScenarioResponse(name="Login", description="...", priority=1)
    """

    name: str
    description: str
    priority: int
    preconditions: list[str]
    steps: list[GeneratedStepResponse]
    assertions: list[str]
    tags: list[str]


class TestGenerationRequest(BaseModel):
    """Description: Request schema for AI test generation.
    Usage Example:
        request = TestGenerationRequest(requirement="Users can log in")
    """

    requirement: str = Field(..., min_length=10, max_length=5000)
    scenario_limit: int = Field(default=3, ge=1, le=5)


class TestGenerationResponse(BaseModel):
    """Description: Response schema for generated test suites.
    Usage Example:
        response = TestGenerationResponse(requirement="...", summary="...", scenarios=[])
    """

    requirement: str
    summary: str
    focus: str
    scenarios: list[GeneratedScenarioResponse]