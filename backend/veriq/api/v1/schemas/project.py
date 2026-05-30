from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    """Description: Project creation request payload.
    Usage Example:
        payload = ProjectCreateRequest(name="Web", slug="web")
    """

    name: str = Field(..., min_length=2, max_length=200)
    slug: str | None = Field(default=None, max_length=200)


class ProjectResponse(BaseModel):
    """Description: Project response payload.
    Usage Example:
        response = ProjectResponse(id="...", name="Web", slug="web", workspace_id="...")
    """

    id: str
    name: str
    slug: str
    workspace_id: str
