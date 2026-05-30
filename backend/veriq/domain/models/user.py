from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Description: User entity scoped to a tenant.
    Usage Example:
        user = User(id="...", tenant_id="...", email="user@example.com", full_name="User")
    """

    id: str
    tenant_id: str
    email: str
    full_name: str
    is_active: bool
