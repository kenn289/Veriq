from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from veriq.api.dependencies.auth import get_current_user, require_tenant_roles
from veriq.api.dependencies.db import get_session
from veriq.api.v1.schemas.organization import OrganizationCreateRequest, OrganizationResponse
from veriq.application.services.organization_service import (
    create_organization,
    list_organizations,
)
from veriq.application.utils.slug import slugify
from veriq.infrastructure.repositories import organization_repository

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationResponse])
def get_organizations(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
) -> list[OrganizationResponse]:
    """Description: List organizations for the current tenant.
    Parameters:
        session: Database session.
        user: Authenticated user.
    Returns:
        list[OrganizationResponse]: Organization list.
    Usage Example:
        organizations = get_organizations(session, user)
    Request Schema:
        None
    Response Schema:
        list[OrganizationResponse]
    Examples:
        [{"id": "...", "name": "QA", "slug": "qa"}]
    Error Cases:
        - 401: Unauthorized
    """

    organizations = list_organizations(session, user.tenant_id)
    return [OrganizationResponse(id=org.id, name=org.name, slug=org.slug) for org in organizations]


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_tenant_roles(["Admin", "QA Lead", "Manager"]))],
)
def create_org(
    payload: OrganizationCreateRequest,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
) -> OrganizationResponse:
    """Description: Create a new organization within the tenant.
    Parameters:
        payload: Organization payload.
        session: Database session.
        user: Authenticated user.
    Returns:
        OrganizationResponse: Created organization.
    Usage Example:
        organization = create_org(payload, session, user)
    Request Schema:
        OrganizationCreateRequest
    Response Schema:
        OrganizationResponse
    Examples:
        {"id": "...", "name": "QA", "slug": "qa"}
    Error Cases:
        - 401: Unauthorized
        - 403: Forbidden
        - 409: Organization slug exists
    """

    resolved_slug = payload.slug or slugify(payload.name)
    if organization_repository.get_organization_by_slug(session, user.tenant_id, resolved_slug):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization slug exists")

    organization = create_organization(session, user.tenant_id, payload.name, resolved_slug)
    return OrganizationResponse(id=organization.id, name=organization.name, slug=organization.slug)
