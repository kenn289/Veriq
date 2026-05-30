from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from veriq.api.dependencies.auth import require_workspace_roles
from veriq.api.dependencies.db import get_session
from veriq.api.v1.schemas.project import ProjectCreateRequest, ProjectResponse
from veriq.application.services.project_service import create_project, list_projects
from veriq.application.utils.slug import slugify
from veriq.infrastructure.repositories import project_repository

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "/workspaces/{workspace_id}",
    response_model=list[ProjectResponse],
    dependencies=[
        Depends(require_workspace_roles(["Admin", "QA Lead", "Developer", "Manager", "Viewer"]))
    ],
)
def get_projects(
    workspace_id: str,
    session: Session = Depends(get_session),
) -> list[ProjectResponse]:
    """Description: List projects for a workspace.
    Parameters:
        workspace_id: Workspace identifier.
        session: Database session.
    Returns:
        list[ProjectResponse]: Project list.
    Usage Example:
        projects = get_projects(workspace_id, session)
    Request Schema:
        None
    Response Schema:
        list[ProjectResponse]
    Examples:
        [{"id": "...", "name": "Web", "slug": "web", "workspace_id": "..."}]
    Error Cases:
        - 401: Unauthorized
        - 403: Forbidden
    """

    projects = list_projects(session, workspace_id)
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            slug=project.slug,
            workspace_id=project.workspace_id,
        )
        for project in projects
    ]


@router.post(
    "/workspaces/{workspace_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_workspace_roles(["Admin", "QA Lead", "Developer"]))],
)
def create_workspace_project(
    workspace_id: str,
    payload: ProjectCreateRequest,
    session: Session = Depends(get_session),
) -> ProjectResponse:
    """Description: Create a project within a workspace.
    Parameters:
        workspace_id: Workspace identifier.
        payload: Project payload.
        session: Database session.
    Returns:
        ProjectResponse: Created project.
    Usage Example:
        project = create_workspace_project(workspace_id, payload, session)
    Request Schema:
        ProjectCreateRequest
    Response Schema:
        ProjectResponse
    Examples:
        {"id": "...", "name": "Web", "slug": "web", "workspace_id": "..."}
    Error Cases:
        - 401: Unauthorized
        - 403: Forbidden
        - 409: Project slug exists
    """

    resolved_slug = payload.slug or slugify(payload.name)
    if project_repository.get_project_by_slug(session, workspace_id, resolved_slug):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project slug exists")

    project = create_project(session, workspace_id, payload.name, resolved_slug)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        slug=project.slug,
        workspace_id=project.workspace_id,
    )
