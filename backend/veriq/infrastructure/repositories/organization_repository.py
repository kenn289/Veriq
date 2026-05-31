from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import OrganizationModel


def create_organization(
    session: Session, tenant_id: str, name: str, slug: str
) -> OrganizationModel:
    """Description: Create an organization under a tenant.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        name: Organization name.
        slug: Organization slug.
    Returns:
        OrganizationModel: Persisted organization.
    Usage Example:
        org = create_organization(session, tenant_id, "QA", "qa")
    """

    organization = OrganizationModel(tenant_id=tenant_id, name=name, slug=slug)
    session.add(organization)
    session.commit()
    session.refresh(organization)
    return organization


def list_organizations(session: Session, tenant_id: str) -> list[OrganizationModel]:
    """Description: List organizations for a tenant.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
    Returns:
        list[OrganizationModel]: Organizations belonging to the tenant.
    Usage Example:
        orgs = list_organizations(session, tenant_id)
    """

    return (
        session.query(OrganizationModel)
        .filter(OrganizationModel.tenant_id == tenant_id)
        .all()
    )


def get_organization(
    session: Session, organization_id: str
) -> OrganizationModel | None:
    """Description: Fetch an organization by id.
    Parameters:
        session: Database session.
        organization_id: Organization identifier.
    Returns:
        OrganizationModel | None: Organization record or None.
    Usage Example:
        org = get_organization(session, org_id)
    """

    return (
        session.query(OrganizationModel)
        .filter(OrganizationModel.id == organization_id)
        .one_or_none()
    )


def get_organization_by_slug(
    session: Session, tenant_id: str, slug: str
) -> OrganizationModel | None:
    """Description: Fetch an organization by tenant and slug.
    Parameters:
        session: Database session.
        tenant_id: Tenant identifier.
        slug: Organization slug.
    Returns:
        OrganizationModel | None: Organization record or None.
    Usage Example:
        org = get_organization_by_slug(session, tenant_id, "qa")
    """

    return (
        session.query(OrganizationModel)
        .filter(
            OrganizationModel.tenant_id == tenant_id, OrganizationModel.slug == slug
        )
        .one_or_none()
    )
