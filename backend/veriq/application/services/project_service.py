from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.application.utils.slug import slugify
from veriq.infrastructure.db.models import ProjectModel
from veriq.infrastructure.repositories import project_repository


def create_project(
    session: Session, workspace_id: str, name: str, slug: str | None
) -> ProjectModel:
    """Description: Create a project under a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
        name: Project name.
        slug: Optional slug override.
    Returns:
        ProjectModel: Persisted project.
    Usage Example:
        project_id = create_project(session, ws_id, "Web", None)
    """

    resolved_slug = slug or slugify(name)
    project = project_repository.create_project(session, workspace_id, name, resolved_slug)
    return project


def list_projects(session: Session, workspace_id: str) -> list[ProjectModel]:
    """Description: List project identifiers for a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
    Returns:
        list[ProjectModel]: Project records.
    Usage Example:
        project_ids = list_projects(session, ws_id)
    """

    return project_repository.list_projects(session, workspace_id)
