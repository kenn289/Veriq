from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import TestRunModel


def create_test_run(
    session: Session,
    workspace_id: str,
    name: str,
    status: str = "pending",
) -> TestRunModel:
    """Description: Create a new test run.
    Parameters:
        session: Database session.
        workspace_id: Parent workspace ID.
        name: Test run name.
        status: Initial status (default: pending).
    Returns:
        TestRunModel: Created test run.
    Usage Example:
        run = create_test_run(session, workspace_id, "Nightly Run")
    """

    test_run = TestRunModel(
        workspace_id=workspace_id,
        name=name,
        status=status,
    )
    session.add(test_run)
    session.flush()
    return test_run


def get_test_run(session: Session, test_run_id: str) -> Optional[TestRunModel]:
    """Description: Get a test run by ID.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        TestRunModel or None: Test run if found.
    Usage Example:
        run = get_test_run(session, test_run_id)
    """

    return session.query(TestRunModel).filter(TestRunModel.id == test_run_id).one_or_none()


def list_test_runs(session: Session, workspace_id: str) -> list[TestRunModel]:
    """Description: List all test runs in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
    Returns:
        list[TestRunModel]: Test runs in workspace.
    Usage Example:
        runs = list_test_runs(session, workspace_id)
    """

    return (
        session.query(TestRunModel)
        .filter(TestRunModel.workspace_id == workspace_id)
        .order_by(TestRunModel.created_at.desc())
        .all()
    )


def update_test_run_status(
    session: Session,
    test_run_id: str,
    status: str,
    total_count: int = 0,
    passed_count: int = 0,
    failed_count: int = 0,
    error_count: int = 0,
    duration_seconds: int = 0,
    started_at: Optional[object] = None,
    completed_at: Optional[object] = None,
) -> Optional[TestRunModel]:
    """Description: Update test run status and counts.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
        status: New status.
        total_count: Total tests (optional).
        passed_count: Tests passed (optional).
        failed_count: Tests failed (optional).
        error_count: Tests with errors (optional).
        duration_seconds: Total duration (optional).
        started_at: Start timestamp (optional).
        completed_at: Completion timestamp (optional).
    Returns:
        TestRunModel or None: Updated test run or None if not found.
    Usage Example:
        run = update_test_run_status(session, run_id, "completed", passed_count=10)
    """

    test_run = get_test_run(session, test_run_id)
    if test_run is None:
        return None

    test_run.status = status
    if total_count > 0:
        test_run.total_count = total_count
    if passed_count > 0:
        test_run.passed_count = passed_count
    if failed_count > 0:
        test_run.failed_count = failed_count
    if error_count > 0:
        test_run.error_count = error_count
    if duration_seconds > 0:
        test_run.duration_seconds = duration_seconds

    if started_at is not None:
        test_run.started_at = started_at
    if completed_at is not None:
        test_run.completed_at = completed_at

    session.flush()
    return test_run


def delete_test_run(session: Session, test_run_id: str) -> bool:
    """Description: Delete a test run.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        bool: True if deleted, False if not found.
    Usage Example:
        deleted = delete_test_run(session, test_run_id)
    """

    test_run = get_test_run(session, test_run_id)
    if test_run is None:
        return False

    session.delete(test_run)
    session.flush()
    return True
