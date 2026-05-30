from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from veriq.infrastructure.config.settings import get_settings


@dataclass(frozen=True)
class TokenPayload:
    """Description: Parsed JWT payload for authenticated requests.
    Usage Example:
        payload = TokenPayload(sub="user_id", tenant_id="tenant_id", exp=123)
    """

    sub: str
    tenant_id: str
    exp: int


def create_access_token(subject: str, tenant_id: str) -> str:
    """Description: Create a signed JWT access token.
    Parameters:
        subject: User identifier.
        tenant_id: Tenant identifier.
    Returns:
        str: Encoded JWT token string.
    Usage Example:
        token = create_access_token(subject="user_id", tenant_id="tenant_id")
    """

    settings = get_settings()
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "tenant_id": tenant_id, "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """Description: Decode a JWT access token into its payload.
    Parameters:
        token: Encoded JWT token.
    Returns:
        TokenPayload: Parsed token payload.
    Usage Example:
        payload = decode_access_token(token)
    """

    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    subject = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    exp = payload.get("exp")
    if not subject or not tenant_id or not exp:
        raise ValueError("Invalid token payload")

    return TokenPayload(sub=subject, tenant_id=tenant_id, exp=int(exp))
