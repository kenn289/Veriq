from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from veriq.infrastructure.db.base import Base


def _utcnow() -> datetime:
    """Description: Provide a timezone-aware UTC timestamp.
    Parameters:
        None
    Returns:
        datetime: Current UTC time.
    Usage Example:
        timestamp = _utcnow()
    """

    return datetime.now(UTC)


class TimestampMixin:
    """Description: Timestamp columns for ORM models.
    Usage Example:
        class MyModel(TimestampMixin, Base):
            ...
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )


class TenantModel(TimestampMixin, Base):
    """Description: Tenant ORM model.
    Usage Example:
        tenant = TenantModel(name="Acme", slug="acme")
    """

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    organizations: Mapped[list[OrganizationModel]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    users: Mapped[list[UserModel]] = relationship(back_populates="tenant")


class OrganizationModel(TimestampMixin, Base):
    """Description: Organization ORM model.
    Usage Example:
        org = OrganizationModel(name="QA", slug="qa", tenant_id=tenant_id)
    """

    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_org_tenant_slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)

    tenant: Mapped[TenantModel] = relationship(back_populates="organizations")
    workspaces: Mapped[list[WorkspaceModel]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class WorkspaceModel(TimestampMixin, Base):
    """Description: Workspace ORM model.
    Usage Example:
        workspace = WorkspaceModel(name="Core", slug="core", organization_id=org_id)
    """

    __tablename__ = "workspaces"
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_workspace_org_slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)

    organization: Mapped[OrganizationModel] = relationship(back_populates="workspaces")
    projects: Mapped[list[ProjectModel]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    memberships: Mapped[list[WorkspaceMembershipModel]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list[TestCaseModel]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    test_runs: Mapped[list[TestRunModel]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )


class ProjectModel(TimestampMixin, Base):
    """Description: Project ORM model.
    Usage Example:
        project = ProjectModel(name="Web", slug="web", workspace_id=workspace_id)
    """

    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("workspace_id", "slug", name="uq_project_workspace_slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)

    workspace: Mapped[WorkspaceModel] = relationship(back_populates="projects")


class UserModel(TimestampMixin, Base):
    """Description: User ORM model.
    Usage Example:
        user = UserModel(email="user@example.com", full_name="User", tenant_id=tenant_id)
    """

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped[TenantModel] = relationship(back_populates="users")
    memberships: Mapped[list[WorkspaceMembershipModel]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RoleModel(Base):
    """Description: Role ORM model.
    Usage Example:
        role = RoleModel(name="Admin", description="Workspace admin")
    """

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    memberships: Mapped[list[WorkspaceMembershipModel]] = relationship(back_populates="role")


class WorkspaceMembershipModel(Base):
    """Description: Workspace membership ORM model.
    Usage Example:
        membership = WorkspaceMembershipModel(workspace_id=ws_id, user_id=user_id, role_id=role_id)
    """

    __tablename__ = "workspace_memberships"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("roles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    workspace: Mapped[WorkspaceModel] = relationship(back_populates="memberships")
    user: Mapped[UserModel] = relationship(back_populates="memberships")
    role: Mapped[RoleModel] = relationship(back_populates="memberships")


class TestCaseModel(TimestampMixin, Base):
    """Description: Test case ORM model.
    Usage Example:
        test = TestCaseModel(name="Login", workspace_id=workspace_id, priority=1)
    """

    __tablename__ = "test_cases"
    __table_args__ = (UniqueConstraint("workspace_id", "slug", name="uq_test_case_workspace_slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    priority: Mapped[int] = mapped_column(default=3, nullable=False)

    workspace: Mapped[WorkspaceModel] = relationship(back_populates="test_cases")
    steps: Mapped[list[TestStepModel]] = relationship(
        back_populates="test_case", cascade="all, delete-orphan"
    )
    results: Mapped[list[TestResultModel]] = relationship(
        back_populates="test_case", cascade="all, delete-orphan"
    )


class TestStepModel(TimestampMixin, Base):
    """Description: Test step ORM model.
    Usage Example:
        step = TestStepModel(test_case_id=tc_id, action="click", order=1)
    """

    __tablename__ = "test_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    test_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_cases.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target: Mapped[str | None] = mapped_column(String(500), nullable=True)
    value: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(nullable=False)

    test_case: Mapped[TestCaseModel] = relationship(back_populates="steps")
    results: Mapped[list[TestResultModel]] = relationship(back_populates="failure_step")


class TestRunModel(TimestampMixin, Base):
    """Description: Test run ORM model.
    Usage Example:
        run = TestRunModel(workspace_id=workspace_id, name="Nightly")
    """

    __tablename__ = "test_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    total_count: Mapped[int] = mapped_column(default=0, nullable=False)
    passed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(default=0, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[WorkspaceModel] = relationship(back_populates="test_runs")
    results: Mapped[list[TestResultModel]] = relationship(
        back_populates="test_run", cascade="all, delete-orphan"
    )


class TestResultModel(TimestampMixin, Base):
    """Description: Test result ORM model.
    Usage Example:
        result = TestResultModel(test_run_id=run_id, test_case_id=tc_id, status="passed")
    """

    __tablename__ = "test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    test_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_cases.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_step_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("test_steps.id"), nullable=True
    )
    failure_screenshot: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attempts: Mapped[int] = mapped_column(default=1, nullable=False)

    test_run: Mapped[TestRunModel] = relationship(back_populates="results")
    test_case: Mapped[TestCaseModel] = relationship(back_populates="results")
    failure_step: Mapped[TestStepModel | None] = relationship(
        foreign_keys=[failure_step_id], back_populates="results"
    )
