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
from veriq.infrastructure.ai.code_generation import generate_zip_from_plan, persist_artifact
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import Query
import io
from pydantic import BaseModel
from pathlib import Path
import os

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



class CodeGenerationRequest(BaseModel):
    plan: TestGenerationResponse


@router.post("/generate-code")
def generate_code(payload: CodeGenerationRequest, workspace_id: str | None = Query(None), target: str | None = Query("playwright-ts")):
    """Generate runnable test artifacts (zip) from a structured test plan.
    Optional query params:
      - workspace_id: persist artifacts under this workspace id
      - target: codegen target: `playwright-ts` or `pytest-playwright`
    Returns JSON with `download_url` when persisted, otherwise streams zip directly.
    """
    blob = generate_zip_from_plan(payload.plan, target=target or "playwright-ts")
    if workspace_id:
        path = persist_artifact(workspace_id, blob)
        # build API url relative to router: /api/v1/ai/generated/{workspace_id}/{filename}
        filename = Path(path).name
        download_url = f"/api/v1/ai/generated/{workspace_id}/{filename}"
        return {"download_url": download_url}
    return StreamingResponse(io.BytesIO(blob), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=generated_tests.zip"})



@router.get("/generated/{workspace_id}/{filename}")
def serve_generated(workspace_id: str, filename: str):
    base = Path(os.getcwd()) / "automation" / "generated" / workspace_id
    target = base / filename
    if not target.exists():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(str(target), media_type="application/zip", filename=filename)


class MultiAgentGenerationRequest(BaseModel):
    """Request for multi-agent test generation."""
    requirement: str
    target_framework: str = "playwright-ts"
    scenario_limit: int = 3


class MultiAgentGenerationResponse(BaseModel):
    """Response from multi-agent test generation."""
    test_plan: dict
    test_cases: list[dict]
    framework_code: dict
    phases_executed: list[str]


@router.post("/orchestrate-test-generation", response_model=MultiAgentGenerationResponse)
def orchestrate_test_generation(payload: MultiAgentGenerationRequest) -> MultiAgentGenerationResponse:
    """Description: Orchestrate multi-agent test generation pipeline.
    
    This endpoint runs the full test generation workflow:
    1. Planner Agent: Analyzes requirement and creates strategy
    2. Designer Agent: Designs detailed test cases
    3. Framework Agent: Generates runnable code
    
    Parameters:
        payload: Test generation request with requirement
        
    Returns:
        MultiAgentGenerationResponse: Full pipeline output
        
    Usage Example:
        POST /api/v1/ai/orchestrate-test-generation
        {
            "requirement": "Users can log in with email and password",
            "target_framework": "playwright-ts",
            "scenario_limit": 3
        }
    """
    from veriq.infrastructure.ai.agents import CoordinatorAgent
    
    coordinator = CoordinatorAgent()
    
    # Run orchestration synchronously
    result = coordinator.orchestrate_test_generation_sync(
        requirement=payload.requirement,
        target_framework=payload.target_framework,
        scenario_limit=payload.scenario_limit,
    )
    
    return MultiAgentGenerationResponse(
        test_plan=result.test_plan,
        test_cases=result.test_cases,
        framework_code=result.framework_code,
        phases_executed=result.phases_executed,
    )
