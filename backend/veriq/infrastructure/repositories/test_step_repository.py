from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import TestStepModel


def create_test_step(
    session: Session,
    test_case_id: str,
    action: str,
    order: int,
    target: str | None = None,
    value: str | None = None,
    description: str | None = None,
) -> TestStepModel:
    """Description: Create a new test step.
    Parameters:
        session: Database session.
        test_case_id: Parent test case ID.
        action: Action type (click, input, assert, navigate, etc.).
        order: Execution order.
        target: Element selector or identifier.
        value: Input value or expected output.
        description: Step description.
    Returns:
        TestStepModel: Created test step.
    Usage Example:
        step = create_test_step(session, tc_id, "click", 1, "button.login")
    """

    step = TestStepModel(
        test_case_id=test_case_id,
        action=action,
        order=order,
        target=target,
        value=value,
        description=description,
    )
    session.add(step)
    session.flush()
    return step


def get_test_step(session: Session, step_id: str) -> TestStepModel | None:
    """Description: Get a test step by ID.
    Parameters:
        session: Database session.
        step_id: Test step ID.
    Returns:
        TestStepModel or None: Test step if found.
    Usage Example:
        step = get_test_step(session, step_id)
    """

    return session.query(TestStepModel).filter(TestStepModel.id == step_id).one_or_none()


def list_test_steps(session: Session, test_case_id: str) -> list[TestStepModel]:
    """Description: List all steps for a test case.
    Parameters:
        session: Database session.
        test_case_id: Test case ID.
    Returns:
        list[TestStepModel]: Steps in order.
    Usage Example:
        steps = list_test_steps(session, test_case_id)
    """

    return (
        session.query(TestStepModel)
        .filter(TestStepModel.test_case_id == test_case_id)
        .order_by(TestStepModel.order)
        .all()
    )


def update_test_step(
    session: Session,
    step_id: str,
    action: str | None = None,
    order: int | None = None,
    target: str | None = None,
    value: str | None = None,
    description: str | None = None,
) -> TestStepModel | None:
    """Description: Update a test step.
    Parameters:
        session: Database session.
        step_id: Test step ID.
        action: New action (optional).
        order: New order (optional).
        target: New target (optional).
        value: New value (optional).
        description: New description (optional).
    Returns:
        TestStepModel or None: Updated step or None if not found.
    Usage Example:
        step = update_test_step(session, step_id, action="input")
    """

    step = get_test_step(session, step_id)
    if step is None:
        return None

    if action is not None:
        step.action = action
    if order is not None:
        step.order = order
    if target is not None:
        step.target = target
    if value is not None:
        step.value = value
    if description is not None:
        step.description = description

    session.flush()
    return step


def delete_test_step(session: Session, step_id: str) -> bool:
    """Description: Delete a test step.
    Parameters:
        session: Database session.
        step_id: Test step ID.
    Returns:
        bool: True if deleted, False if not found.
    Usage Example:
        deleted = delete_test_step(session, step_id)
    """

    step = get_test_step(session, step_id)
    if step is None:
        return False

    session.delete(step)
    session.flush()
    return True
