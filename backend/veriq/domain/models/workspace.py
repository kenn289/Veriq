from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Workspace:
    """Description: Workspace entity under an organization.
    Usage Example:
        workspace = Workspace(id="...", organization_id="...", name="Core", slug="core")
    """

    id: str
    organization_id: str
    name: str
    slug: str
