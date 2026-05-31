from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from veriq.api.dependencies.auth import get_current_user
from veriq.api.dependencies.db import get_session
from veriq.api.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserProfileResponse,
)
from veriq.application.services.auth_service import (
    authenticate_user,
    register_tenant_admin,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest, session: Session = Depends(get_session)
) -> RegisterResponse:
    """Description: Register a tenant and initial admin user.
    Parameters:
        payload: Registration payload.
        session: Database session.
    Returns:
        RegisterResponse: Identifiers for created entities.
    Usage Example:
        response = register(payload, session)
    Request Schema:
        RegisterRequest
    Response Schema:
        RegisterResponse
    Examples:
        {"tenant_id": "...", "organization_id": "...", "workspace_id": "...", "user_id": "..."}
    Error Cases:
        - 400: Invalid request or duplicate tenant
    """

    try:
        result = register_tenant_admin(
            session=session,
            tenant_name=payload.tenant_name,
            tenant_slug=payload.tenant_slug,
            organization_name=payload.organization_name,
            workspace_name=payload.workspace_name,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return RegisterResponse(
        tenant_id=result.tenant_id,
        organization_id=result.organization_id,
        workspace_id=result.workspace_id,
        user_id=result.user_id,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, session: Session = Depends(get_session)
) -> TokenResponse:
    """Description: Authenticate a user and issue an access token.
    Parameters:
        payload: Login payload.
        session: Database session.
    Returns:
        TokenResponse: Access token details.
    Usage Example:
        response = login(payload, session)
    Request Schema:
        LoginRequest
    Response Schema:
        TokenResponse
    Examples:
        {"access_token": "<jwt>", "token_type": "bearer", "expires_in": 3600}
    Error Cases:
        - 401: Invalid credentials
    """

    try:
        result = authenticate_user(
            session, payload.tenant_slug, payload.email, payload.password
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return TokenResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    )


@router.get("/me", response_model=UserProfileResponse)
def me(user=Depends(get_current_user)) -> UserProfileResponse:
    """Description: Return the authenticated user profile.
    Parameters:
        user: Authenticated user.
    Returns:
        UserProfileResponse: User profile data.
    Usage Example:
        profile = me(user)
    Request Schema:
        None
    Response Schema:
        UserProfileResponse
    Examples:
        {"user_id": "...", "tenant_id": "...", "email": "user@acme.com", "full_name": "User", "is_active": true}
    Error Cases:
        - 401: Unauthorized
    """

    return UserProfileResponse(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )
