from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import WorkspaceMembershipModel


def create_membership(
    session: Session, workspace_id: str, user_id: str, role_id: str
) -> WorkspaceMembershipModel:
    """Description: Create a workspace membership with role assignment.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
        user_id: User identifier.
        role_id: Role identifier.
    Returns:
        WorkspaceMembershipModel: Persisted membership.
    Usage Example:
        membership = create_membership(session, ws_id, user_id, role_id)
    """

    membership = WorkspaceMembershipModel(
        workspace_id=workspace_id, user_id=user_id, role_id=role_id
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def get_membership(
    session: Session, workspace_id: str, user_id: str
) -> WorkspaceMembershipModel | None:
    """Description: Fetch membership for a user in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
        user_id: User identifier.
    Returns:
        WorkspaceMembershipModel | None: Membership record or None.
    Usage Example:
        membership = get_membership(session, ws_id, user_id)
    """

    return (
        session.query(WorkspaceMembershipModel)
        .filter(
            WorkspaceMembershipModel.workspace_id == workspace_id,
            WorkspaceMembershipModel.user_id == user_id,
        )
        .one_or_none()
    )


def list_memberships_for_user(session: Session, user_id: str) -> list[WorkspaceMembershipModel]:
    """Description: List workspace memberships for a user.
    Parameters:
        session: Database session.
        user_id: User identifier.
    Returns:
        list[WorkspaceMembershipModel]: Membership records.
    Usage Example:
        memberships = list_memberships_for_user(session, user_id)
    """

    return (
        session.query(WorkspaceMembershipModel)
        .filter(WorkspaceMembershipModel.user_id == user_id)
        .all()
    )
