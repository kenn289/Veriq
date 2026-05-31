from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import UserModel


def create_user(
    session: Session,
    tenant_id: str,
    email: str,
    full_name: str,
    password_hash: str,
) -> UserModel:
    """Description: Create a new user in a tenant.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        email: User email.
        full_name: Full name.
        password_hash: Hashed password.
    Returns:
        UserModel: Persisted user.
    Usage Example:
        user = create_user(session, tenant_id, "user@example.com", "User", hash)
    """

    user = UserModel(
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        password_hash=password_hash,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, tenant_id: str, email: str) -> UserModel | None:
    """Description: Fetch a user by tenant and email.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        email: User email.
    Returns:
        UserModel | None: User record or None.
    Usage Example:
        user = get_user_by_email(session, tenant_id, "user@example.com")
    """

    return (
        session.query(UserModel)
        .filter(UserModel.tenant_id == tenant_id, UserModel.email == email)
        .one_or_none()
    )


def get_user_by_id(session: Session, tenant_id: str, user_id: str) -> UserModel | None:
    """Description: Fetch a user by tenant and id.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        user_id: User identifier.
    Returns:
        UserModel | None: User record or None.
    Usage Example:
        user = get_user_by_id(session, tenant_id, user_id)
    """

    return (
        session.query(UserModel)
        .filter(UserModel.tenant_id == tenant_id, UserModel.id == user_id)
        .one_or_none()
    )
