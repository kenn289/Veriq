from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import RoleModel


def get_role_by_name(session: Session, name: str) -> RoleModel | None:
    """Description: Fetch a role by name.
    Parameters:
        session: Database session.
        name: Role name.
    Returns:
        RoleModel | None: Role record or None.
    Usage Example:
        role = get_role_by_name(session, "Admin")
    """

    return session.query(RoleModel).filter(RoleModel.name == name).one_or_none()


def list_roles(session: Session) -> list[RoleModel]:
    """Description: List all roles.
    Parameters:
        session: Database session.
    Returns:
        list[RoleModel]: Role records.
    Usage Example:
        roles = list_roles(session)
    """

    return session.query(RoleModel).all()
