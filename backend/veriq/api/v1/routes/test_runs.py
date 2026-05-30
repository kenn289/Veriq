from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from veriq.api.dependencies.auth import get_current_user
from veriq.api.dependencies.db import get_session
from veriq.api.v1.schemas.test_run import (
    TestRunCreateRequest,
    TestRunDetailResponse,
    TestRunResponse,
    TestResultReportRequest,
    TestResultResponse,
    TestRunSummaryResponse,
)
from veriq.application.services import test_run_service
from veriq.infrastructure.repositories import test_run_repository as tr_repo
from veriq.infrastructure.repositories import test_result_repository as trs_repo
from veriq.infrastructure.db.models import UserModel

router = APIRouter(prefix="/api/v1/test_runs", tags=["test_runs"])


@router.post("", response_model=TestRunResponse, status_code=201)
def create_test_run(
    request: TestRunCreateRequest,
    workspace_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestRunResponse:
    """Description: Create a new test run.
    Parameters:
        request: Test run creation request.
        workspace_id: Workspace ID (query param).
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestRunResponse: Created test run.
    Usage Example:
        POST /api/v1/test_runs?workspace_id=ws123
        {"name": "Nightly Run"}
    """

    try:
        test_run = test_run_service.create_test_run(
            session=session,
            workspace_id=workspace_id,
            name=request.name,
        )
        session.commit()

        return TestRunResponse(
            id=test_run.id,
            workspace_id=test_run.workspace_id,
            name=test_run.name,
            status=test_run.status,
            total_count=test_run.total_count,
            passed_count=test_run.passed_count,
            failed_count=test_run.failed_count,
            error_count=test_run.error_count,
            duration_seconds=test_run.duration_seconds,
            started_at=test_run.started_at.isoformat()
            if test_run.started_at
            else None,
            completed_at=test_run.completed_at.isoformat()
            if test_run.completed_at
            else None,
            created_at=test_run.created_at.isoformat(),
            updated_at=test_run.updated_at.isoformat(),
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[TestRunResponse])
def list_test_runs(
    workspace_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> list[TestRunResponse]:
    """Description: List all test runs in a workspace.
    Parameters:
        workspace_id: Workspace ID (query param).
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        list[TestRunResponse]: Test runs sorted by newest.
    Usage Example:
        GET /api/v1/test_runs?workspace_id=ws123
    """

    test_runs = test_run_service.list_test_runs_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )

    return [
        TestRunResponse(
            id=tr.id,
            workspace_id=tr.workspace_id,
            name=tr.name,
            status=tr.status,
            total_count=tr.total_count,
            passed_count=tr.passed_count,
            failed_count=tr.failed_count,
            error_count=tr.error_count,
            duration_seconds=tr.duration_seconds,
            started_at=tr.started_at.isoformat() if tr.started_at else None,
            completed_at=tr.completed_at.isoformat() if tr.completed_at else None,
            created_at=tr.created_at.isoformat(),
            updated_at=tr.updated_at.isoformat(),
        )
        for tr in test_runs
    ]


@router.get("/{test_run_id}", response_model=TestRunDetailResponse)
def get_test_run(
    test_run_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestRunDetailResponse:
    """Description: Get a test run with all its results.
    Parameters:
        test_run_id: Test run ID.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestRunDetailResponse: Test run with results.
    Usage Example:
        GET /api/v1/test_runs/run123
    """

    result = test_run_service.get_test_run_with_results(
        session=session,
        test_run_id=test_run_id,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    test_run, results = result

    return TestRunDetailResponse(
        id=test_run.id,
        workspace_id=test_run.workspace_id,
        name=test_run.name,
        status=test_run.status,
        total_count=test_run.total_count,
        passed_count=test_run.passed_count,
        failed_count=test_run.failed_count,
        error_count=test_run.error_count,
        duration_seconds=test_run.duration_seconds,
        started_at=test_run.started_at.isoformat()
        if test_run.started_at
        else None,
        completed_at=test_run.completed_at.isoformat()
        if test_run.completed_at
        else None,
        results=[
            TestResultResponse(
                id=r.id,
                test_run_id=r.test_run_id,
                test_case_id=r.test_case_id,
                status=r.status,
                duration_seconds=r.duration_seconds,
                error_message=r.error_message,
                attempts=r.attempts,
                created_at=r.created_at.isoformat(),
            )
            for r in results
        ],
        created_at=test_run.created_at.isoformat(),
        updated_at=test_run.updated_at.isoformat(),
    )


@router.post("/{test_run_id}/results", response_model=TestResultResponse, status_code=201)
def report_result(
    test_run_id: str,
    request: TestResultReportRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestResultResponse:
    """Description: Report a test result for a test in a run.
    Parameters:
        test_run_id: Test run ID.
        request: Test result report request.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestResultResponse: Created test result.
    Usage Example:
        POST /api/v1/test_runs/run123/results
        {"test_case_id": "tc123", "status": "passed", "duration_seconds": 45}
    """

    # Verify test run exists
    test_run = tr_repo.get_test_run(session, test_run_id)
    if test_run is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    try:
        result = test_run_service.report_test_result(
            session=session,
            test_run_id=test_run_id,
            test_case_id=request.test_case_id,
            status=request.status,
            duration_seconds=request.duration_seconds,
            error_message=request.error_message,
            error_stack_trace=request.error_stack_trace,
            failure_step_id=request.failure_step_id,
            failure_screenshot=request.failure_screenshot,
        )
        session.commit()

        return TestResultResponse(
            id=result.id,
            test_run_id=result.test_run_id,
            test_case_id=result.test_case_id,
            status=result.status,
            duration_seconds=result.duration_seconds,
            error_message=result.error_message,
            attempts=result.attempts,
            created_at=result.created_at.isoformat(),
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_run_id}/summary", response_model=TestRunSummaryResponse)
def get_run_summary(
    test_run_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestRunSummaryResponse:
    """Description: Get summary statistics for a test run.
    Parameters:
        test_run_id: Test run ID.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestRunSummaryResponse: Summary with counts.
    Usage Example:
        GET /api/v1/test_runs/run123/summary
    """

    summary = test_run_service.get_run_summary(
        session=session,
        test_run_id=test_run_id,
    )

    return TestRunSummaryResponse(**summary)


@router.post("/{test_run_id}/start", response_model=TestRunResponse)
def start_run(
    test_run_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestRunResponse:
    """Description: Start executing a test run.
    Parameters:
        test_run_id: Test run ID.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestRunResponse: Updated test run in progress.
    Usage Example:
        POST /api/v1/test_runs/run123/start
    """

    test_run = test_run_service.start_test_run(
        session=session,
        test_run_id=test_run_id,
    )

    if test_run is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    session.commit()

    return TestRunResponse(
        id=test_run.id,
        workspace_id=test_run.workspace_id,
        name=test_run.name,
        status=test_run.status,
        total_count=test_run.total_count,
        passed_count=test_run.passed_count,
        failed_count=test_run.failed_count,
        error_count=test_run.error_count,
        duration_seconds=test_run.duration_seconds,
        started_at=test_run.started_at.isoformat()
        if test_run.started_at
        else None,
        completed_at=test_run.completed_at.isoformat()
        if test_run.completed_at
        else None,
        created_at=test_run.created_at.isoformat(),
        updated_at=test_run.updated_at.isoformat(),
    )


@router.post("/{test_run_id}/complete", response_model=TestRunResponse)
def complete_run(
    test_run_id: str,
    duration_seconds: int,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestRunResponse:
    """Description: Mark a test run as completed.
    Parameters:
        test_run_id: Test run ID.
        duration_seconds: Total execution time (query param).
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestRunResponse: Updated test run completed.
    Usage Example:
        POST /api/v1/test_runs/run123/complete?duration_seconds=3600
    """

    test_run = test_run_service.complete_test_run(
        session=session,
        test_run_id=test_run_id,
        duration_seconds=duration_seconds,
    )

    if test_run is None:
        raise HTTPException(status_code=404, detail="Test run not found")

    session.commit()

    return TestRunResponse(
        id=test_run.id,
        workspace_id=test_run.workspace_id,
        name=test_run.name,
        status=test_run.status,
        total_count=test_run.total_count,
        passed_count=test_run.passed_count,
        failed_count=test_run.failed_count,
        error_count=test_run.error_count,
        duration_seconds=test_run.duration_seconds,
        started_at=test_run.started_at.isoformat()
        if test_run.started_at
        else None,
        completed_at=test_run.completed_at.isoformat()
        if test_run.completed_at
        else None,
        created_at=test_run.created_at.isoformat(),
        updated_at=test_run.updated_at.isoformat(),
    )
