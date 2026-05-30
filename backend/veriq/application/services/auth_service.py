from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from veriq.application.utils.slug import slugify
from veriq.infrastructure.config.settings import get_settings
from veriq.infrastructure.repositories import (
    membership_repository,
    organization_repository,
    role_repository,
    tenant_repository,
    user_repository,
    workspace_repository,
)
from veriq.infrastructure.security.jwt import create_access_token
from veriq.infrastructure.security.passwords import hash_password, verify_password


@dataclass(frozen=True)
class RegisterResult:
    """Description: Result payload for a registration flow.
    Usage Example:
        result = RegisterResult(user_id="...", workspace_id="...")
    """

    tenant_id: str
    organization_id: str
    workspace_id: str
    user_id: str


@dataclass(frozen=True)
class AuthResult:
    """Description: Result payload for authentication.
    Usage Example:
        result = AuthResult(access_token="token", token_type="bearer", expires_in=3600)
    """

    access_token: str
    token_type: str
    expires_in: int


def register_tenant_admin(
    session: Session,
    tenant_name: str,
    tenant_slug: str | None,
    organization_name: str,
    workspace_name: str,
    email: str,
    full_name: str,
    password: str,
) -> RegisterResult:
    """Description: Register a tenant with an initial admin user.
    Parameters:
        session: Database session.
        tenant_name: Tenant name.
        tenant_slug: Tenant slug override.
        organization_name: Organization name.
        workspace_name: Workspace name.
        email: Admin email.
        full_name: Admin name.
        password: Admin password.
    Returns:
        RegisterResult: Created entity identifiers.
    Usage Example:
        result = register_tenant_admin(
            session, "Acme", None, "QA", "Core", "a@b.com", "Admin", "secret"
        )
    """

    resolved_tenant_slug = tenant_slug or slugify(tenant_name)
    if tenant_repository.get_tenant_by_slug(session, resolved_tenant_slug) is not None:
        raise ValueError("Tenant slug already exists")
    tenant = tenant_repository.create_tenant(session, tenant_name, resolved_tenant_slug)

    organization_slug = slugify(organization_name)
    organization = organization_repository.create_organization(
        session, tenant.id, organization_name, organization_slug
    )

    workspace_slug = slugify(workspace_name)
    workspace = workspace_repository.create_workspace(
        session, organization.id, workspace_name, workspace_slug
    )

    password_hash = hash_password(password)
    if user_repository.get_user_by_email(session, tenant.id, email) is not None:
        raise ValueError("User already exists")
    user = user_repository.create_user(session, tenant.id, email, full_name, password_hash)

    admin_role = role_repository.get_role_by_name(session, "Admin")
    if admin_role is None:
        raise ValueError("Admin role is not configured")

    membership_repository.create_membership(session, workspace.id, user.id, admin_role.id)

    return RegisterResult(
        tenant_id=tenant.id,
        organization_id=organization.id,
        workspace_id=workspace.id,
        user_id=user.id,
    )


def authenticate_user(session: Session, tenant_slug: str, email: str, password: str) -> AuthResult:
    """Description: Authenticate a user and return access token data.
    Parameters:
        session: Database session.
        tenant_slug: Tenant slug for scoping.
        email: User email.
        password: Plaintext password.
    Returns:
        AuthResult: Access token details.
    Usage Example:
        result = authenticate_user(session, "acme", "user@acme.com", "secret")
    """

    normalized_slug = slugify(tenant_slug)
    tenant = tenant_repository.get_tenant_by_slug(session, normalized_slug)
    if tenant is None:
        raise ValueError("Tenant not found")

    user = user_repository.get_user_by_email(session, tenant.id, email)
    if user is None or not user.is_active:
        raise ValueError("Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")

    access_token = create_access_token(subject=user.id, tenant_id=tenant.id)
    expires_in = get_settings().access_token_expire_minutes * 60
    return AuthResult(access_token=access_token, token_type="bearer", expires_in=expires_in)
