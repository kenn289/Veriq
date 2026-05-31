from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from veriq.api.dependencies.auth import (
    get_current_user,
    require_tenant_roles,
    require_workspace_roles,
)
from veriq.api.dependencies.db import get_session
from veriq.api.v1.schemas.workspace import WorkspaceCreateRequest, WorkspaceResponse
from veriq.application.services.workspace_service import (
    create_workspace,
    list_user_workspaces,
)
from veriq.application.utils.slug import slugify
from veriq.infrastructure.repositories import (
    membership_repository,
    role_repository,
    workspace_repository,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
def get_workspaces(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
) -> list[WorkspaceResponse]:
    """Description: List workspaces for the current user.
    Parameters:
        session: Database session.
        user: Authenticated user.
    Returns:
        list[WorkspaceResponse]: Workspace list.
    Usage Example:
        workspaces = get_workspaces(session, user)
    Request Schema:
        None
    Response Schema:
        list[WorkspaceResponse]
    Examples:
        [{"id": "...", "name": "Core", "slug": "core", "organization_id": "..."}]
    Error Cases:
        - 401: Unauthorized
    """

    workspaces = list_user_workspaces(session, user.id)
    return [
        WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            slug=workspace.slug,
            organization_id=workspace.organization_id,
        )
        for workspace in workspaces
    ]


@router.post(
    "/organizations/{organization_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_tenant_roles(["Admin", "QA Lead", "Manager"]))],
)
def create_org_workspace(
    organization_id: str,
    payload: WorkspaceCreateRequest,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
) -> WorkspaceResponse:
    """Description: Create a workspace within an organization.
    Parameters:
        organization_id: Organization identifier.
        payload: Workspace payload.
        session: Database session.
        user: Authenticated user.
    Returns:
        WorkspaceResponse: Created workspace.
    Usage Example:
        workspace = create_org_workspace(org_id, payload, session, user)
    Request Schema:
        WorkspaceCreateRequest
    Response Schema:
        WorkspaceResponse
    Examples:
        {"id": "...", "name": "Core", "slug": "core", "organization_id": "..."}
    Error Cases:
        - 401: Unauthorized
        - 403: Forbidden
        - 409: Workspace slug exists
    """

    resolved_slug = payload.slug or slugify(payload.name)
    if workspace_repository.get_workspace_by_slug(
        session, organization_id, resolved_slug
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Workspace slug exists"
        )

    workspace = create_workspace(session, organization_id, payload.name, resolved_slug)
    admin_role = role_repository.get_role_by_name(session, "Admin")
    if admin_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Role missing"
        )

    membership_repository.create_membership(
        session, workspace.id, user.id, admin_role.id
    )
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        organization_id=workspace.organization_id,
    )


@router.get(
    "/{workspace_id}/detail",
    response_model=WorkspaceResponse,
    dependencies=[
        Depends(
            require_workspace_roles(
                ["Admin", "QA Lead", "Developer", "Manager", "Viewer"]
            )
        )
    ],
)
def get_workspace_detail(
    workspace_id: str,
    session: Session = Depends(get_session),
) -> WorkspaceResponse:
    """Description: Fetch a workspace by id.
    Parameters:
        workspace_id: Workspace identifier.
        session: Database session.
    Returns:
        WorkspaceResponse: Workspace payload.
    Usage Example:
        workspace = get_workspace_detail(workspace_id, session)
    Request Schema:
        None
    Response Schema:
        WorkspaceResponse
    Examples:
        {"id": "...", "name": "Core", "slug": "core", "organization_id": "..."}
    Error Cases:
        - 401: Unauthorized
        - 403: Forbidden
        - 404: Not found
    """

    workspace = workspace_repository.get_workspace(session, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        organization_id=workspace.organization_id,
    )
