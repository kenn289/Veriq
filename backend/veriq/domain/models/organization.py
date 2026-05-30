from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Organization:
    """Description: Organization entity within a tenant.
    Usage Example:
        org = Organization(id="...", tenant_id="...", name="QA", slug="qa")
    """

    id: str
    tenant_id: str
    name: str
    slug: str
