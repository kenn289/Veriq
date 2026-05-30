from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessToken:
    """Description: Access token response data.
    Usage Example:
        token = AccessToken(token="...", token_type="bearer", expires_in=3600)
    """

    token: str
    token_type: str
    expires_in: int
