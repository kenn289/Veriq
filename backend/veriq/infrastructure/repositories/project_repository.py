from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import ProjectModel


def create_project(
    session: Session, workspace_id: str, name: str, slug: str
) -> ProjectModel:
    """Description: Create a project under a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
        name: Project name.
        slug: Project slug.
    Returns:
        ProjectModel: Persisted project.
    Usage Example:
        project = create_project(session, ws_id, "Web", "web")
    """

    project = ProjectModel(workspace_id=workspace_id, name=name, slug=slug)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def list_projects(session: Session, workspace_id: str) -> list[ProjectModel]:
    """Description: List projects for a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
    Returns:
        list[ProjectModel]: Project records.
    Usage Example:
        projects = list_projects(session, ws_id)
    """

    return (
        session.query(ProjectModel)
        .filter(ProjectModel.workspace_id == workspace_id)
        .all()
    )


def get_project_by_slug(
    session: Session, workspace_id: str, slug: str
) -> ProjectModel | None:
    """Description: Fetch a project by workspace and slug.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
        slug: Project slug.
    Returns:
        ProjectModel | None: Project record or None.
    Usage Example:
        project = get_project_by_slug(session, ws_id, "web")
    """

    return (
        session.query(ProjectModel)
        .filter(ProjectModel.workspace_id == workspace_id, ProjectModel.slug == slug)
        .one_or_none()
    )
