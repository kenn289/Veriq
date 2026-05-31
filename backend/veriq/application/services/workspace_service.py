from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.application.utils.slug import slugify
from veriq.infrastructure.db.models import WorkspaceModel
from veriq.infrastructure.repositories import workspace_repository


def create_workspace(
    session: Session, organization_id: str, name: str, slug: str | None
) -> WorkspaceModel:
    """Description: Create a workspace under an organization.
    Parameters:
        session: Database session.
        organization_id: Organization identifier.
        name: Workspace name.
        slug: Optional slug override.
    Returns:
        WorkspaceModel: Persisted workspace.
    Usage Example:
        ws_id = create_workspace(session, org_id, "Core", None)
    """

    resolved_slug = slug or slugify(name)
    workspace = workspace_repository.create_workspace(
        session, organization_id, name, resolved_slug
    )
    return workspace


def list_workspaces(session: Session, organization_id: str) -> list[WorkspaceModel]:
    """Description: List workspace identifiers for an organization.
    Parameters:
        session: Database session.
        organization_id: Organization identifier.
    Returns:
        list[WorkspaceModel]: Workspace records.
    Usage Example:
        ws_ids = list_workspaces(session, org_id)
    """

    return workspace_repository.list_workspaces_by_org(session, organization_id)


def list_user_workspaces(session: Session, user_id: str) -> list[WorkspaceModel]:
    """Description: List workspace identifiers for a user.
    Parameters:
        session: Database session.
        user_id: User identifier.
    Returns:
        list[WorkspaceModel]: Workspace records.
    Usage Example:
        ws_ids = list_user_workspaces(session, user_id)
    """

    return workspace_repository.list_workspaces_for_user(session, user_id)
