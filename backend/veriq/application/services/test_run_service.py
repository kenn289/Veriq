from __future__ import annotations

from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from veriq.infrastructure.repositories import test_run_repository as tr_repo
from veriq.infrastructure.repositories import test_result_repository as trs_repo
from veriq.infrastructure.db.models import TestRunModel, TestResultModel


def create_test_run(
    session: Session,
    workspace_id: str,
    name: str,
) -> TestRunModel:
    """Description: Create a new test run.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
        name: Test run name (e.g., 'Nightly Run').
    Returns:
        TestRunModel: Created test run in pending state.
    Usage Example:
        run = create_test_run(session, workspace_id, "Nightly Run")
    """

    return tr_repo.create_test_run(
        session=session,
        workspace_id=workspace_id,
        name=name,
        status="pending",
    )


def start_test_run(session: Session, test_run_id: str) -> Optional[TestRunModel]:
    """Description: Start executing a test run.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        TestRunModel or None: Updated test run with in_progress status.
    Usage Example:
        run = start_test_run(session, test_run_id)
    """

    now = datetime.now(timezone.utc)
    return tr_repo.update_test_run_status(
        session=session,
        test_run_id=test_run_id,
        status="in_progress",
        started_at=now,
    )


def complete_test_run(
    session: Session,
    test_run_id: str,
    duration_seconds: int,
) -> Optional[TestRunModel]:
    """Description: Mark a test run as completed.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
        duration_seconds: Total execution time.
    Returns:
        TestRunModel or None: Updated test run.
    Usage Example:
        run = complete_test_run(session, test_run_id, 3600)
    """

    # Get summary of results
    summary = trs_repo.get_run_summary(session, test_run_id)

    now = datetime.now(timezone.utc)
    return tr_repo.update_test_run_status(
        session=session,
        test_run_id=test_run_id,
        status="completed",
        total_count=summary["total"],
        passed_count=summary["passed"],
        failed_count=summary["failed"],
        error_count=summary["error"],
        duration_seconds=duration_seconds,
        completed_at=now,
    )


def report_test_result(
    session: Session,
    test_run_id: str,
    test_case_id: str,
    status: str,
    duration_seconds: int = 0,
    error_message: Optional[str] = None,
    error_stack_trace: Optional[str] = None,
    failure_step_id: Optional[str] = None,
    failure_screenshot: Optional[str] = None,
    attempts: int = 1,
) -> TestResultModel:
    """Description: Report a test result for a test case in a run.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
        test_case_id: Test case ID.
        status: Result status (passed, failed, error, skipped).
        duration_seconds: Execution time.
        error_message: Failure message (optional).
        error_stack_trace: Stack trace (optional).
        failure_step_id: Which step failed (optional).
        failure_screenshot: Screenshot URL (optional).
        attempts: Retry count (default: 1).
    Returns:
        TestResultModel: Created test result.
    Usage Example:
        result = report_test_result(session, run_id, tc_id, "passed", 45)
    """

    result = trs_repo.create_test_result(
        session=session,
        test_run_id=test_run_id,
        test_case_id=test_case_id,
        status=status,
        duration_seconds=duration_seconds,
        error_message=error_message,
        error_stack_trace=error_stack_trace,
        failure_step_id=failure_step_id,
        failure_screenshot=failure_screenshot,
        attempts=attempts,
    )

    return result


def get_run_summary(session: Session, test_run_id: str) -> dict:
    """Description: Get statistics for a test run.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        dict: Summary with counts and statistics.
    Usage Example:
        summary = get_run_summary(session, test_run_id)
    """

    return trs_repo.get_run_summary(session, test_run_id)


def list_test_runs_by_workspace(
    session: Session, workspace_id: str
) -> list[TestRunModel]:
    """Description: List all test runs in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
    Returns:
        list[TestRunModel]: Test runs sorted by newest first.
    Usage Example:
        runs = list_test_runs_by_workspace(session, workspace_id)
    """

    return tr_repo.list_test_runs(session, workspace_id)


def get_test_run_with_results(
    session: Session, test_run_id: str
) -> Optional[tuple[TestRunModel, list[TestResultModel]]]:
    """Description: Get test run with all its results.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        tuple of (TestRunModel, list[TestResultModel]) or None if not found.
    Usage Example:
        run, results = get_test_run_with_results(session, test_run_id)
    """

    test_run = tr_repo.get_test_run(session, test_run_id)
    if test_run is None:
        return None

    results = trs_repo.list_test_results(session, test_run_id)
    return test_run, results
