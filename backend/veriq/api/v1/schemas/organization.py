from __future__ import annotations

from pydantic import BaseModel, Field


class OrganizationCreateRequest(BaseModel):
    """Description: Organization creation request payload.
    Usage Example:
        payload = OrganizationCreateRequest(name="QA", slug="qa")
    """

    name: str = Field(..., min_length=2, max_length=200)
    slug: str | None = Field(default=None, max_length=200)


class OrganizationResponse(BaseModel):
    """Description: Organization response payload.
    Usage Example:
        response = OrganizationResponse(id="...", name="QA", slug="qa")
    """

    id: str
    name: str
    slug: str
