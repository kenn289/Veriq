from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import (
    OrganizationModel,
    RoleModel,
    WorkspaceMembershipModel,
    WorkspaceModel,
)


def user_has_role_in_tenant(
    session: Session, tenant_id: str, user_id: str, roles: list[str]
) -> bool:
    """Description: Determine if a user has one of the roles within a tenant.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        user_id: User identifier.
        roles: Role names to match.
    Returns:
        bool: True if the user has at least one role in the tenant.
    Usage Example:
        allowed = user_has_role_in_tenant(session, tenant_id, user_id, ["Admin"])
    """

    return (
        session.query(WorkspaceMembershipModel)
        .join(WorkspaceModel)
        .join(OrganizationModel)
        .join(RoleModel, WorkspaceMembershipModel.role_id == RoleModel.id)
        .filter(
            WorkspaceMembershipModel.user_id == user_id,
            OrganizationModel.tenant_id == tenant_id,
            RoleModel.name.in_(roles),
        )
        .count()
        > 0
    )
