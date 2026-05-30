from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import RoleModel

ROLE_DEFINITIONS: dict[str, str] = {
    "Admin": "Full administrative control within a workspace.",
    "QA Lead": "Owns test strategy and review workflows.",
    "Developer": "Builds and maintains automation assets.",
    "Manager": "Tracks execution health and reports.",
    "Viewer": "Read-only access to results and dashboards.",
}


def seed_roles(session: Session) -> None:
    """Description: Insert default roles if they do not exist.
    Parameters:
        session: Active database session.
    Returns:
        None
    Usage Example:
        seed_roles(session)
    """

    existing = {
        role.name for role in session.query(RoleModel).filter(RoleModel.name.in_(ROLE_DEFINITIONS))
    }
    for name, description in ROLE_DEFINITIONS.items():
        if name in existing:
            continue
        session.add(RoleModel(name=name, description=description))
    session.commit()
