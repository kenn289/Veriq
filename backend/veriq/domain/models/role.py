from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    """Description: Role entity for RBAC.
    Usage Example:
        role = Role(id="...", name="Admin", description="Workspace admin")
    """

    id: str
    name: str
    description: str
