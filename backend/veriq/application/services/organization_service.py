from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.application.utils.slug import slugify
from veriq.infrastructure.db.models import OrganizationModel
from veriq.infrastructure.repositories import organization_repository


def create_organization(
    session: Session, tenant_id: str, name: str, slug: str | None
) -> OrganizationModel:
    """Description: Create an organization within a tenant.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        name: Organization name.
        slug: Optional slug override.
    Returns:
        OrganizationModel: Persisted organization.
    Usage Example:
        org_id = create_organization(session, tenant_id, "QA", None)
    """

    resolved_slug = slug or slugify(name)
    organization = organization_repository.create_organization(
        session, tenant_id, name, resolved_slug
    )
    return organization


def list_organizations(session: Session, tenant_id: str) -> list[OrganizationModel]:
    """Description: List organization identifiers for a tenant.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
    Returns:
        list[str]: Organization identifiers.
    Usage Example:
        org_ids = list_organizations(session, tenant_id)
    """

    return organization_repository.list_organizations(session, tenant_id)
