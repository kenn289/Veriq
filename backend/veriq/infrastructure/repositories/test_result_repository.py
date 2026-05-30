from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import TestResultModel


def create_test_result(
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
    """Description: Create a new test result.
    Parameters:
        session: Database session.
        test_run_id: Parent test run ID.
        test_case_id: Test case ID.
        status: Result status (passed, failed, error, skipped).
        duration_seconds: Execution time.
        error_message: Failure message (optional).
        error_stack_trace: Full stack trace (optional).
        failure_step_id: Which step failed (optional).
        failure_screenshot: Screenshot URL (optional).
        attempts: Retry count (default: 1).
    Returns:
        TestResultModel: Created test result.
    Usage Example:
        result = create_test_result(session, run_id, tc_id, "passed", 45)
    """

    result = TestResultModel(
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
    session.add(result)
    session.flush()
    return result


def get_test_result(session: Session, result_id: str) -> Optional[TestResultModel]:
    """Description: Get a test result by ID.
    Parameters:
        session: Database session.
        result_id: Test result ID.
    Returns:
        TestResultModel or None: Test result if found.
    Usage Example:
        result = get_test_result(session, result_id)
    """

    return session.query(TestResultModel).filter(TestResultModel.id == result_id).one_or_none()


def list_test_results(session: Session, test_run_id: str) -> list[TestResultModel]:
    """Description: List all results for a test run.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        list[TestResultModel]: Test results.
    Usage Example:
        results = list_test_results(session, test_run_id)
    """

    return (
        session.query(TestResultModel)
        .filter(TestResultModel.test_run_id == test_run_id)
        .order_by(TestResultModel.created_at)
        .all()
    )


def get_run_summary(session: Session, test_run_id: str) -> dict[str, int]:
    """Description: Get summary statistics for a test run.
    Parameters:
        session: Database session.
        test_run_id: Test run ID.
    Returns:
        dict: Summary with passed, failed, error, total counts.
    Usage Example:
        summary = get_run_summary(session, test_run_id)
    """

    results = list_test_results(session, test_run_id)

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r.status == "passed"),
        "failed": sum(1 for r in results if r.status == "failed"),
        "error": sum(1 for r in results if r.status == "error"),
        "skipped": sum(1 for r in results if r.status == "skipped"),
    }

    return summary


def delete_test_result(session: Session, result_id: str) -> bool:
    """Description: Delete a test result.
    Parameters:
        session: Database session.
        result_id: Test result ID.
    Returns:
        bool: True if deleted, False if not found.
    Usage Example:
        deleted = delete_test_result(session, result_id)
    """

    result = get_test_result(session, result_id)
    if result is None:
        return False

    session.delete(result)
    session.flush()
    return True
