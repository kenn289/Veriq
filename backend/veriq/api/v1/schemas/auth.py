from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Description: Registration request payload.
    Usage Example:
        payload = RegisterRequest(
            tenant_name="Acme",
            tenant_slug="acme",
            organization_name="QA",
            workspace_name="Core",
            email="admin@acme.com",
            full_name="Admin",
            password="secret",
        )
    """

    tenant_name: str = Field(..., min_length=2, max_length=200)
    tenant_slug: str | None = Field(default=None, max_length=200)
    organization_name: str = Field(..., min_length=2, max_length=200)
    workspace_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8, max_length=128)


class RegisterResponse(BaseModel):
    """Description: Registration response payload.
    Usage Example:
        response = RegisterResponse(
            tenant_id="...",
            organization_id="...",
            workspace_id="...",
            user_id="...",
        )
    """

    tenant_id: str
    organization_id: str
    workspace_id: str
    user_id: str


class LoginRequest(BaseModel):
    """Description: Login request payload.
    Usage Example:
        payload = LoginRequest(tenant_slug="acme", email="admin@acme.com", password="secret")
    """

    tenant_slug: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Description: Token response payload.
    Usage Example:
        response = TokenResponse(access_token="token", token_type="bearer", expires_in=3600)
    """

    access_token: str
    token_type: str
    expires_in: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "<jwt>",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )


class UserProfileResponse(BaseModel):
    """Description: Authenticated user profile payload.
    Usage Example:
        profile = UserProfileResponse(user_id="...", tenant_id="...", email="user@acme.com")
    """

    user_id: str
    tenant_id: str
    email: EmailStr
    full_name: str
    is_active: bool
