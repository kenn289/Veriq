from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from veriq.application.utils.slug import slugify
from veriq.infrastructure.repositories import test_case_repository as tc_repo
from veriq.infrastructure.repositories import test_step_repository as ts_repo
from veriq.infrastructure.db.models import TestCaseModel, TestStepModel


def create_test_case(
    session: Session,
    workspace_id: str,
    name: str,
    description: Optional[str] = None,
    priority: int = 3,
) -> TestCaseModel:
    """Description: Create a new test case in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
        name: Test case name.
        description: Optional description.
        priority: Priority 1-5 (default: 3).
    Returns:
        TestCaseModel: Created test case.
    Usage Example:
        tc = create_test_case(session, workspace_id, "Login Test")
    """

    slug = slugify(name)

    # Check if slug already exists in workspace
    existing = tc_repo.get_test_case_by_slug(session, workspace_id, slug)
    if existing is not None:
        raise ValueError(
            f"Test case with slug '{slug}' already exists in this workspace"
        )

    return tc_repo.create_test_case(
        session=session,
        workspace_id=workspace_id,
        name=name,
        slug=slug,
        description=description,
        priority=priority,
    )


def add_step_to_test_case(
    session: Session,
    test_case_id: str,
    action: str,
    target: Optional[str] = None,
    value: Optional[str] = None,
    description: Optional[str] = None,
) -> TestStepModel:
    """Description: Add a step to a test case.
    Parameters:
        session: Database session.
        test_case_id: Test case ID.
        action: Action type (click, input, assert, navigate, etc.).
        target: Element selector (optional).
        value: Expected value or input (optional).
        description: Step description (optional).
    Returns:
        TestStepModel: Created test step.
    Usage Example:
        step = add_step_to_test_case(session, tc_id, "click", "button.login")
    """

    # Get current step count to determine order
    existing_steps = ts_repo.list_test_steps(session, test_case_id)
    next_order = len(existing_steps) + 1

    return ts_repo.create_test_step(
        session=session,
        test_case_id=test_case_id,
        action=action,
        order=next_order,
        target=target,
        value=value,
        description=description,
    )


def list_test_cases_by_workspace(
    session: Session, workspace_id: str
) -> list[TestCaseModel]:
    """Description: List all test cases in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
    Returns:
        list[TestCaseModel]: Test cases.
    Usage Example:
        tests = list_test_cases_by_workspace(session, workspace_id)
    """

    return tc_repo.list_test_cases(session, workspace_id)


def get_test_case_details(
    session: Session, test_case_id: str
) -> Optional[tuple[TestCaseModel, list[TestStepModel]]]:
    """Description: Get test case with all its steps.
    Parameters:
        session: Database session.
        test_case_id: Test case ID.
    Returns:
        tuple of (TestCaseModel, list[TestStepModel]) or None if not found.
    Usage Example:
        tc, steps = get_test_case_details(session, test_case_id)
    """

    test_case = tc_repo.get_test_case(session, test_case_id)
    if test_case is None:
        return None

    steps = ts_repo.list_test_steps(session, test_case_id)
    return test_case, steps
