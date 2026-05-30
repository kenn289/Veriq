from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from veriq.api.dependencies.db import get_session
from veriq.infrastructure.db.models import UserModel
from veriq.infrastructure.repositories import (
    membership_repository,
    role_access_repository,
    tenant_access_repository,
    user_repository,
)
from veriq.infrastructure.security.jwt import decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserModel:
    """Description: Resolve the current user from the Authorization header.
    Parameters:
        session: Database session.
        credentials: HTTP bearer credentials.
    Returns:
        UserModel: Authenticated user.
    Usage Example:
        user = Depends(get_current_user)
    """

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = user_repository.get_user_by_id(session, payload.tenant_id, payload.sub)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user


def require_workspace_roles(roles: list[str]) -> Callable:
    """Description: Dependency factory that enforces workspace roles.
    Parameters:
        roles: List of role names to authorize.
    Returns:
        Callable: Dependency function.
    Usage Example:
        dependency = require_workspace_roles(["Admin", "QA Lead"])
    """

    def _dependency(
        workspace_id: str,
        session: Session = Depends(get_session),
        user=Depends(get_current_user),
    ) -> None:
        if not role_access_repository.user_has_role_in_workspace(
            session, workspace_id, user.id, roles
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return _dependency


def require_tenant_roles(roles: list[str]) -> Callable:
    """Description: Dependency factory that enforces tenant-level roles.
    Parameters:
        roles: List of role names to authorize.
    Returns:
        Callable: Dependency function.
    Usage Example:
        dependency = require_tenant_roles(["Admin"])
    """

    def _dependency(
        session: Session = Depends(get_session),
        user=Depends(get_current_user),
    ) -> None:
        if not tenant_access_repository.user_has_role_in_tenant(
            session, user.tenant_id, user.id, roles
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return _dependency


def get_user_memberships(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    """Description: Return workspace memberships for the current user.
    Parameters:
        session: Database session.
        user: Current user.
    Returns:
        list[WorkspaceMembershipModel]: User memberships.
    Usage Example:
        memberships = Depends(get_user_memberships)
    """

    return membership_repository.list_memberships_for_user(session, user.id)
