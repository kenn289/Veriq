from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from veriq.api.dependencies.auth import get_current_user
from veriq.api.dependencies.db import get_session
from veriq.api.v1.schemas.test_case import (
    TestCaseCreateRequest,
    TestCaseDetailResponse,
    TestCaseResponse,
    TestStepCreateRequest,
    TestStepResponse,
)
from veriq.application.services import test_case_service
from veriq.infrastructure.db.models import UserModel
from veriq.infrastructure.repositories import test_case_repository as tc_repo
from veriq.infrastructure.repositories import test_step_repository as ts_repo

router = APIRouter(prefix="/api/v1/test_cases", tags=["test_cases"])


@router.post("", response_model=TestCaseResponse, status_code=201)
def create_test_case(
    request: TestCaseCreateRequest,
    workspace_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestCaseResponse:
    """Description: Create a new test case in a workspace.
    Parameters:
        request: Test case creation request.
        workspace_id: Workspace ID (query param).
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestCaseResponse: Created test case.
    Usage Example:
        POST /api/v1/test_cases?workspace_id=ws123
        {"name": "Login Test", "priority": 1}
    """

    try:
        test_case = test_case_service.create_test_case(
            session=session,
            workspace_id=workspace_id,
            name=request.name,
            description=request.description,
            priority=request.priority,
        )
        session.commit()

        return TestCaseResponse(
            id=test_case.id,
            workspace_id=test_case.workspace_id,
            name=test_case.name,
            description=test_case.description,
            slug=test_case.slug,
            status=test_case.status,
            priority=test_case.priority,
            created_at=test_case.created_at.isoformat(),
            updated_at=test_case.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[TestCaseResponse])
def list_test_cases(
    workspace_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> list[TestCaseResponse]:
    """Description: List all test cases in a workspace.
    Parameters:
        workspace_id: Workspace ID (query param).
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        list[TestCaseResponse]: Test cases in workspace.
    Usage Example:
        GET /api/v1/test_cases?workspace_id=ws123
    """

    test_cases = test_case_service.list_test_cases_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )

    return [
        TestCaseResponse(
            id=tc.id,
            workspace_id=tc.workspace_id,
            name=tc.name,
            description=tc.description,
            slug=tc.slug,
            status=tc.status,
            priority=tc.priority,
            created_at=tc.created_at.isoformat(),
            updated_at=tc.updated_at.isoformat(),
        )
        for tc in test_cases
    ]


@router.get("/{test_case_id}", response_model=TestCaseDetailResponse)
def get_test_case(
    test_case_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestCaseDetailResponse:
    """Description: Get a test case with all its steps.
    Parameters:
        test_case_id: Test case ID.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestCaseDetailResponse: Test case with steps.
    Usage Example:
        GET /api/v1/test_cases/tc123
    """

    result = test_case_service.get_test_case_details(
        session=session,
        test_case_id=test_case_id,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    test_case, steps = result

    return TestCaseDetailResponse(
        id=test_case.id,
        workspace_id=test_case.workspace_id,
        name=test_case.name,
        description=test_case.description,
        slug=test_case.slug,
        status=test_case.status,
        priority=test_case.priority,
        steps=[
            TestStepResponse(
                id=s.id,
                action=s.action,
                target=s.target,
                value=s.value,
                description=s.description,
                order=s.order,
            )
            for s in steps
        ],
        created_at=test_case.created_at.isoformat(),
        updated_at=test_case.updated_at.isoformat(),
    )


@router.post("/{test_case_id}/steps", response_model=TestStepResponse, status_code=201)
def add_step(
    test_case_id: str,
    request: TestStepCreateRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> TestStepResponse:
    """Description: Add a step to a test case.
    Parameters:
        test_case_id: Test case ID.
        request: Test step creation request.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        TestStepResponse: Created test step.
    Usage Example:
        POST /api/v1/test_cases/tc123/steps
        {"action": "click", "target": "button.login"}
    """

    # Verify test case exists
    test_case = tc_repo.get_test_case(session, test_case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    try:
        step = test_case_service.add_step_to_test_case(
            session=session,
            test_case_id=test_case_id,
            action=request.action,
            target=request.target,
            value=request.value,
            description=request.description,
        )
        session.commit()

        return TestStepResponse(
            id=step.id,
            action=step.action,
            target=step.target,
            value=step.value,
            description=step.description,
            order=step.order,
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_case_id}/steps", response_model=list[TestStepResponse])
def list_steps(
    test_case_id: str,
    session: Session = Depends(get_session),
    current_user: UserModel = Depends(get_current_user),
) -> list[TestStepResponse]:
    """Description: List all steps for a test case.
    Parameters:
        test_case_id: Test case ID.
        session: Database session.
        current_user: Current authenticated user.
    Returns:
        list[TestStepResponse]: Test steps in order.
    Usage Example:
        GET /api/v1/test_cases/tc123/steps
    """

    steps = ts_repo.list_test_steps(session, test_case_id)

    return [
        TestStepResponse(
            id=s.id,
            action=s.action,
            target=s.target,
            value=s.value,
            description=s.description,
            order=s.order,
        )
        for s in steps
    ]
