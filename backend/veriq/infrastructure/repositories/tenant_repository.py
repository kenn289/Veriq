from __future__ import annotations

from sqlalchemy.orm import Session

from veriq.infrastructure.db.models import TenantModel


def create_tenant(session: Session, name: str, slug: str) -> TenantModel:
    """Description: Create a tenant record.
    Parameters:
        session: Database session.
        name: Tenant name.
        slug: Tenant slug.
    Returns:
        TenantModel: Persisted tenant.
    Usage Example:
        tenant = create_tenant(session, "Acme", "acme")
    """

    tenant = TenantModel(name=name, slug=slug)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


def get_tenant_by_slug(session: Session, slug: str) -> TenantModel | None:
    """Description: Fetch a tenant by slug.
    Parameters:
        session: Database session.
        slug: Tenant slug.
    Returns:
        TenantModel | None: Tenant record or None.
    Usage Example:
        tenant = get_tenant_by_slug(session, "acme")
    """

    return session.query(TenantModel).filter(TenantModel.slug == slug).one_or_none()
