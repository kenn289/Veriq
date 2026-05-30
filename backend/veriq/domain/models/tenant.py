from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tenant:
    """Description: Tenant entity for multi-tenant isolation.
    Usage Example:
        tenant = Tenant(id="...", name="Acme", slug="acme")
    """

    id: str
    name: str
    slug: str
