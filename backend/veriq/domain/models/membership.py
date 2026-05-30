from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkspaceMembership:
    """Description: Membership linking a user to a workspace role.
    Usage Example:
        membership = WorkspaceMembership(
            id="...", workspace_id="...", user_id="...", role_id="..."
        )
    """

    id: str
    workspace_id: str
    user_id: str
    role_id: str
