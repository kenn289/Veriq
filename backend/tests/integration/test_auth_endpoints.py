from __future__ import annotations


def test_register_login_flow(client) -> None:
    """Description: Validate registration and login endpoints.
    Parameters:
        client: FastAPI test client.
    Returns:
        None
    Usage Example:
        test_register_login_flow(client)
    """

    register_payload = {
        "tenant_name": "Acme",
        "tenant_slug": "acme",
        "organization_name": "QA",
        "workspace_name": "Core",
        "email": "admin@acme.com",
        "full_name": "Admin",
        "password": "strongpassword",
    }

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_payload = {
        "tenant_slug": "acme",
        "email": "admin@acme.com",
        "password": "strongpassword",
    }
    login_response = client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    auth_headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@acme.com"

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "QA Team", "slug": "qa-team"},
        headers=auth_headers,
    )
    assert org_response.status_code == 201
    organization_id = org_response.json()["id"]

    org_list = client.get("/api/v1/organizations", headers=auth_headers)
    assert org_list.status_code == 200

    workspace_response = client.post(
        f"/api/v1/workspaces/organizations/{organization_id}",
        json={"name": "Platform", "slug": "platform"},
        headers=auth_headers,
    )
    assert workspace_response.status_code == 201
    workspace_id = workspace_response.json()["id"]

    workspace_list = client.get("/api/v1/workspaces", headers=auth_headers)
    assert workspace_list.status_code == 200

    project_response = client.post(
        f"/api/v1/projects/workspaces/{workspace_id}",
        json={"name": "Web", "slug": "web"},
        headers=auth_headers,
    )
    assert project_response.status_code == 201

    projects_list = client.get(
        f"/api/v1/projects/workspaces/{workspace_id}",
        headers=auth_headers,
    )
    assert projects_list.status_code == 200
