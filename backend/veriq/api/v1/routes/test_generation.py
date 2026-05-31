from __future__ import annotations

from fastapi import APIRouter

from veriq.api.v1.schemas.test_generation import (
    GeneratedScenarioResponse,
    GeneratedStepResponse,
    TestGenerationRequest,
    TestGenerationResponse,
)
from veriq.infrastructure.ai.test_generation_provider import (
    get_test_generation_provider,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/test-generation", response_model=TestGenerationResponse)
def generate_tests(payload: TestGenerationRequest) -> TestGenerationResponse:
    """Description: Generate a test suite skeleton from a requirement.
    Parameters:
        payload: Test generation request.
    Returns:
        TestGenerationResponse: Structured test design output.
    Usage Example:
        response = generate_tests(payload)
    """

    provider = get_test_generation_provider()
    suite = provider.generate_suite(payload.requirement, payload.scenario_limit)
    return TestGenerationResponse(
        requirement=suite.requirement,
        summary=suite.summary,
        focus=suite.focus,
        scenarios=[
            GeneratedScenarioResponse(
                name=scenario.name,
                description=scenario.description,
                priority=scenario.priority,
                preconditions=scenario.preconditions,
                steps=[
                    GeneratedStepResponse(
                        order=step.order,
                        action=step.action,
                        target=step.target,
                        value=step.value,
                        description=step.description,
                    )
                    for step in scenario.steps
                ],
                assertions=scenario.assertions,
                tags=scenario.tags,
            )
            for scenario in suite.scenarios
        ],
    )
