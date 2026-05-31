from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import WorkspaceMembershipModel, WorkspaceModel


def create_workspace(
    session: Session, organization_id: str, name: str, slug: str
) -> WorkspaceModel:
    """Description: Create a workspace under an organization.
    Parameters:
        session: Database session.
        organization_id: Organization identifier.
        name: Workspace name.
        slug: Workspace slug.
    Returns:
        WorkspaceModel: Persisted workspace.
    Usage Example:
        workspace = create_workspace(session, org_id, "Core", "core")
    """

    workspace = WorkspaceModel(organization_id=organization_id, name=name, slug=slug)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


def list_workspaces_by_org(
    session: Session, organization_id: str
) -> list[WorkspaceModel]:
    """Description: List workspaces for an organization.
    Parameters:
        session: Database session.
        organization_id: Organization identifier.
    Returns:
        list[WorkspaceModel]: Workspace records.
    Usage Example:
        workspaces = list_workspaces_by_org(session, org_id)
    """

    return (
        session.query(WorkspaceModel)
        .filter(WorkspaceModel.organization_id == organization_id)
        .all()
    )


def list_workspaces_for_user(session: Session, user_id: str) -> list[WorkspaceModel]:
    """Description: List workspaces where a user has membership.
    Parameters:
        session: Database session.
        user_id: User identifier.
    Returns:
        list[WorkspaceModel]: Workspace records.
    Usage Example:
        workspaces = list_workspaces_for_user(session, user_id)
    """

    return (
        session.query(WorkspaceModel)
        .join(WorkspaceMembershipModel)
        .filter(WorkspaceMembershipModel.user_id == user_id)
        .all()
    )


def get_workspace(session: Session, workspace_id: str) -> WorkspaceModel | None:
    """Description: Fetch a workspace by id.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
    Returns:
        WorkspaceModel | None: Workspace record or None.
    Usage Example:
        workspace = get_workspace(session, workspace_id)
    """

    return (
        session.query(WorkspaceModel)
        .filter(WorkspaceModel.id == workspace_id)
        .one_or_none()
    )


def get_workspace_by_slug(
    session: Session, organization_id: str, slug: str
) -> WorkspaceModel | None:
    """Description: Fetch a workspace by organization and slug.
    Parameters:
        session: Database session.
        organization_id: Organization identifier.
        slug: Workspace slug.
    Returns:
        WorkspaceModel | None: Workspace record or None.
    Usage Example:
        workspace = get_workspace_by_slug(session, org_id, "core")
    """

    return (
        session.query(WorkspaceModel)
        .filter(
            WorkspaceModel.organization_id == organization_id,
            WorkspaceModel.slug == slug,
        )
        .one_or_none()
    )
