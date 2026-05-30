from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    """Description: Project entity within a workspace.
    Usage Example:
        project = Project(id="...", workspace_id="...", name="Web", slug="web")
    """

    id: str
    workspace_id: str
    name: str
    slug: str
