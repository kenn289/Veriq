from __future__ import annotations

from fastapi.testclient import TestClient

from veriq.main import create_app


def test_health_endpoint() -> None:
    """Description: Validate health endpoint response.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_health_endpoint()
    """

    client = TestClient(create_app(seed_roles_on_startup=False))
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "timestamp" in payload


def test_version_endpoint() -> None:
    """Description: Validate version endpoint response.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_version_endpoint()
    """

    client = TestClient(create_app(seed_roles_on_startup=False))
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["app_name"] != ""
    assert payload["app_version"] != ""
    assert payload["environment"] != ""
