from __future__ import annotations

from pydantic import BaseModel, Field


class WorkspaceCreateRequest(BaseModel):
    """Description: Workspace creation request payload.
    Usage Example:
        payload = WorkspaceCreateRequest(name="Core", slug="core")
    """

    name: str = Field(..., min_length=2, max_length=200)
    slug: str | None = Field(default=None, max_length=200)


class WorkspaceResponse(BaseModel):
    """Description: Workspace response payload.
    Usage Example:
        response = WorkspaceResponse(id="...", name="Core", slug="core", organization_id="...")
    """

    id: str
    name: str
    slug: str
    organization_id: str
