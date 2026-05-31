from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from veriq.domain.models.membership import WorkspaceMembership
from veriq.domain.models.organization import Organization
from veriq.domain.models.project import Project
from veriq.domain.models.workspace import Workspace
from veriq.infrastructure.repositories import (
    organization_repository as org_repo,
)
from veriq.infrastructure.repositories import (
    test_case_repository as tc_repo,
)
from veriq.infrastructure.repositories import (
    test_result_repository as tr_result_repo,
)
from veriq.infrastructure.repositories import (
    test_run_repository as tr_repo,
)
from veriq.infrastructure.repositories import (
    test_step_repository as ts_repo,
)


def _register_admin_and_get_headers(
    client: TestClient,
) -> tuple[dict[str, str], str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "tenant_name": "Coverage Tenant",
            "tenant_slug": "coverage-tenant",
            "organization_name": "Coverage Org",
            "workspace_name": "Coverage Workspace",
            "email": "coverage@example.com",
            "full_name": "Coverage User",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "coverage-tenant",
            "email": "coverage@example.com",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    payload = register_response.json()
    return headers, payload["organization_id"], payload["workspace_id"]


def test_domain_models_can_be_instantiated() -> None:
    org = Organization(id="org-1", tenant_id="tenant-1", name="QA", slug="qa")
    workspace = Workspace(
        id="workspace-1",
        organization_id="org-1",
        name="Core",
        slug="core",
    )
    project = Project(
        id="project-1", workspace_id="workspace-1", name="Web", slug="web"
    )
    membership = WorkspaceMembership(
        id="membership-1",
        workspace_id="workspace-1",
        user_id="user-1",
        role_id="role-1",
    )

    assert org.slug == "qa"
    assert workspace.organization_id == "org-1"
    assert project.workspace_id == "workspace-1"
    assert membership.role_id == "role-1"


def test_organization_and_workspace_routes_cover_happy_and_conflict_paths(
    db_session: Session, client: TestClient
) -> None:
    headers, organization_id, _ = _register_admin_and_get_headers(client)

    org_list = client.get("/api/v1/organizations", headers=headers)
    assert org_list.status_code == 200
    assert len(org_list.json()) == 1

    create_response = client.post(
        "/api/v1/organizations",
        json={"name": "Coverage Team"},
        headers=headers,
    )
    assert create_response.status_code == 201
    assert create_response.json()["slug"] == "coverage-team"

    conflict_response = client.post(
        "/api/v1/organizations",
        json={"name": "Coverage Team", "slug": "coverage-team"},
        headers=headers,
    )
    assert conflict_response.status_code == 409

    workspace = client.post(
        f"/api/v1/workspaces/organizations/{organization_id}",
        json={"name": "Platform", "slug": "platform"},
        headers=headers,
    )
    assert workspace.status_code == 201

    workspace_list = client.get("/api/v1/workspaces", headers=headers)
    assert workspace_list.status_code == 200
    assert workspace_list.json()


def test_test_case_and_test_run_routes_cover_main_branches(
    db_session: Session, client: TestClient
) -> None:
    headers, _, workspace_id = _register_admin_and_get_headers(client)

    test_case_response = client.post(
        "/api/v1/api/v1/test_cases",
        params={"workspace_id": workspace_id},
        json={"name": "Login Test", "priority": 2},
        headers=headers,
    )
    assert test_case_response.status_code == 201
    test_case_id = test_case_response.json()["id"]

    duplicate_response = client.post(
        "/api/v1/api/v1/test_cases",
        params={"workspace_id": workspace_id},
        json={"name": "Login Test", "priority": 2},
        headers=headers,
    )
    assert duplicate_response.status_code == 400

    list_cases_response = client.get(
        "/api/v1/api/v1/test_cases",
        params={"workspace_id": workspace_id},
        headers=headers,
    )
    assert list_cases_response.status_code == 200
    assert len(list_cases_response.json()) == 1

    get_case_response = client.get(
        f"/api/v1/api/v1/test_cases/{test_case_id}", headers=headers
    )
    assert get_case_response.status_code == 200

    add_step_response = client.post(
        f"/api/v1/api/v1/test_cases/{test_case_id}/steps",
        json={"action": "navigate", "target": "/login"},
        headers=headers,
    )
    assert add_step_response.status_code == 201

    steps_response = client.get(
        f"/api/v1/api/v1/test_cases/{test_case_id}/steps",
        headers=headers,
    )
    assert steps_response.status_code == 200
    assert len(steps_response.json()) == 1

    test_run_response = client.post(
        "/api/v1/api/v1/test_runs",
        params={"workspace_id": workspace_id},
        json={"name": "Nightly Run"},
        headers=headers,
    )
    assert test_run_response.status_code == 201
    test_run_id = test_run_response.json()["id"]

    list_runs_response = client.get(
        "/api/v1/api/v1/test_runs",
        params={"workspace_id": workspace_id},
        headers=headers,
    )
    assert list_runs_response.status_code == 200
    assert len(list_runs_response.json()) == 1

    start_response = client.post(
        f"/api/v1/api/v1/test_runs/{test_run_id}/start", headers=headers
    )
    assert start_response.status_code == 200
    assert start_response.json()["status"] == "in_progress"

    result_response = client.post(
        f"/api/v1/api/v1/test_runs/{test_run_id}/results",
        json={
            "test_case_id": test_case_id,
            "status": "passed",
            "duration_seconds": 12,
        },
        headers=headers,
    )
    assert result_response.status_code == 201

    summary_response = client.get(
        f"/api/v1/api/v1/test_runs/{test_run_id}/summary",
        headers=headers,
    )
    assert summary_response.status_code == 200
    assert summary_response.json()["passed"] == 1

    detail_response = client.get(
        f"/api/v1/api/v1/test_runs/{test_run_id}", headers=headers
    )
    assert detail_response.status_code == 200
    assert len(detail_response.json()["results"]) == 1

    complete_response = client.post(
        f"/api/v1/api/v1/test_runs/{test_run_id}/complete",
        params={"duration_seconds": 99},
        headers=headers,
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"


def test_repository_not_found_branches(db_session: Session) -> None:
    assert org_repo.get_organization(db_session, "missing") is None
    assert org_repo.get_organization_by_slug(db_session, "tenant", "slug") is None
    assert tc_repo.get_test_case(db_session, "missing") is None
    assert tc_repo.get_test_case_by_slug(db_session, "workspace", "slug") is None
    assert ts_repo.get_test_step(db_session, "missing") is None
    assert tr_repo.get_test_run(db_session, "missing") is None
    assert tr_result_repo.get_test_result(db_session, "missing") is None

    assert tc_repo.delete_test_case(db_session, "missing") is False
    assert ts_repo.delete_test_step(db_session, "missing") is False
    assert tr_repo.delete_test_run(db_session, "missing") is False
    assert tr_result_repo.delete_test_result(db_session, "missing") is False
