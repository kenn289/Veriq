"""Test runs routes — execute tests and manage test runs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from veriq.api.dependencies.auth import get_current_user
from veriq.api.dependencies.db import get_session
from veriq.infrastructure.db.models import UserModel
from veriq.infrastructure.execution import ExecutionEngine, ExecutionResult, ExecutionStatus

router = APIRouter(prefix="/test_runs", tags=["test_runs"])


class ExecuteTestRequest(BaseModel):
    """Request to execute tests."""
    test_code: str
    target_framework: str = "playwright-ts"
    test_name: str = "generated_tests"


class ExecutionResultResponse(BaseModel):
    """Response with execution results."""
    test_id: str
    status: str
    duration_seconds: float
    passed_count: int
    failed_count: int
    error_count: int
    stdout: str | None = None
    stderr: str | None = None


@router.post("/execute", response_model=ExecutionResultResponse)
def execute_tests(
    request: ExecuteTestRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> ExecutionResultResponse:
    """Description: Execute generated test code.
    
    Parameters:
        request: Execution request with test code and framework
        session: Database session
        current_user: Authenticated user
        
    Returns:
        ExecutionResultResponse: Test execution results
        
    Usage Example:
        POST /api/v1/test_runs/execute
        {
            "test_code": "test code here",
            "target_framework": "playwright-ts",
            "test_name": "my_test"
        }
    """
    engine = ExecutionEngine()
    
    try:
        if request.target_framework == "playwright-ts":
            result = engine.execute_playwright_ts(
                test_code=request.test_code,
                test_name=request.test_name,
            )
        elif request.target_framework == "pytest-playwright":
            result = engine.execute_pytest_playwright(
                test_code=request.test_code,
                test_name=request.test_name,
            )
        else:
            raise ValueError(f"Unsupported target framework: {request.target_framework}")
        
        return ExecutionResultResponse(
            test_id=result.test_id,
            status=result.status.value,
            duration_seconds=result.duration_seconds,
            passed_count=result.passed_count,
            failed_count=result.failed_count,
            error_count=result.error_count,
            stdout=result.stdout[:1000] if result.stdout else None,
            stderr=result.stderr[:1000] if result.stderr else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
