from __future__ import annotations

from veriq.infrastructure.security.jwt import create_access_token, decode_access_token


def test_token_roundtrip() -> None:
    """Description: Validate token encode and decode.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_token_roundtrip()
    """

    token = create_access_token(subject="user-id", tenant_id="tenant-id")
    payload = decode_access_token(token)
    assert payload.sub == "user-id"
    assert payload.tenant_id == "tenant-id"
