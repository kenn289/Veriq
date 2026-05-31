from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import TestCaseModel


def create_test_case(
    session: Session,
    workspace_id: str,
    name: str,
    slug: str,
    description: str | None = None,
    status: str = "active",
    priority: int = 3,
) -> TestCaseModel:
    """Description: Create a new test case.
    Parameters:
        session: Database session.
        workspace_id: Parent workspace ID.
        name: Test case name.
        slug: URL slug.
        description: Optional description.
        status: Test case status (default: active).
        priority: Priority 1-5 (default: 3).
    Returns:
        TestCaseModel: Created test case.
    Usage Example:
        tc = create_test_case(session, workspace_id, "Login Test", "login-test")
    """

    test_case = TestCaseModel(
        workspace_id=workspace_id,
        name=name,
        slug=slug,
        description=description,
        status=status,
        priority=priority,
    )
    session.add(test_case)
    session.flush()
    return test_case


def get_test_case(session: Session, test_case_id: str) -> TestCaseModel | None:
    """Description: Get a test case by ID.
    Parameters:
        session: Database session.
        test_case_id: Test case ID.
    Returns:
        TestCaseModel or None: Test case if found.
    Usage Example:
        tc = get_test_case(session, test_case_id)
    """

    return (
        session.query(TestCaseModel)
        .filter(TestCaseModel.id == test_case_id)
        .one_or_none()
    )


def get_test_case_by_slug(
    session: Session, workspace_id: str, slug: str
) -> TestCaseModel | None:
    """Description: Get a test case by workspace and slug.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
        slug: Test case slug.
    Returns:
        TestCaseModel or None: Test case if found.
    Usage Example:
        tc = get_test_case_by_slug(session, workspace_id, "login-test")
    """

    return (
        session.query(TestCaseModel)
        .filter(TestCaseModel.workspace_id == workspace_id, TestCaseModel.slug == slug)
        .one_or_none()
    )


def list_test_cases(session: Session, workspace_id: str) -> list[TestCaseModel]:
    """Description: List all test cases in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace ID.
    Returns:
        list[TestCaseModel]: Test cases in workspace.
    Usage Example:
        tests = list_test_cases(session, workspace_id)
    """

    return (
        session.query(TestCaseModel)
        .filter(TestCaseModel.workspace_id == workspace_id)
        .order_by(TestCaseModel.created_at.desc())
        .all()
    )


def update_test_case(
    session: Session,
    test_case_id: str,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: int | None = None,
) -> TestCaseModel | None:
    """Description: Update a test case.
    Parameters:
        session: Database session.
        test_case_id: Test case ID.
        name: New name (optional).
        description: New description (optional).
        status: New status (optional).
        priority: New priority (optional).
    Returns:
        TestCaseModel or None: Updated test case or None if not found.
    Usage Example:
        tc = update_test_case(session, test_case_id, name="New Name")
    """

    test_case = get_test_case(session, test_case_id)
    if test_case is None:
        return None

    if name is not None:
        test_case.name = name
    if description is not None:
        test_case.description = description
    if status is not None:
        test_case.status = status
    if priority is not None:
        test_case.priority = priority

    session.flush()
    return test_case


def delete_test_case(session: Session, test_case_id: str) -> bool:
    """Description: Delete a test case.
    Parameters:
        session: Database session.
        test_case_id: Test case ID.
    Returns:
        bool: True if deleted, False if not found.
    Usage Example:
        deleted = delete_test_case(session, test_case_id)
    """

    test_case = get_test_case(session, test_case_id)
    if test_case is None:
        return False

    session.delete(test_case)
    session.flush()
    return True
