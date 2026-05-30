from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import RoleModel, WorkspaceMembershipModel


def user_has_role_in_workspace(
    session: Session, workspace_id: str, user_id: str, roles: list[str]
) -> bool:
    """Description: Determine if a user has one of the roles in a workspace.
    Parameters:
        session: Database session.
        workspace_id: Workspace identifier.
        user_id: User identifier.
        roles: Role names to match.
    Returns:
        bool: True if user has at least one matching role.
    Usage Example:
        allowed = user_has_role_in_workspace(session, ws_id, user_id, ["Admin"])
    """

    return (
        session.query(WorkspaceMembershipModel)
        .join(RoleModel, WorkspaceMembershipModel.role_id == RoleModel.id)
        .filter(
            WorkspaceMembershipModel.workspace_id == workspace_id,
            WorkspaceMembershipModel.user_id == user_id,
            RoleModel.name.in_(roles),
        )
        .count()
        > 0
    )
