from __future__ import annotations


def test_generate_tests_endpoint(client) -> None:
    response = client.post(
        "/api/v1/ai/test-generation",
        json={
            "requirement": "Users can log in with email and password",
            "scenario_limit": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["focus"] == "authentication"
    assert len(payload["scenarios"]) == 2
    assert payload["scenarios"][0]["steps"][0]["target"] == "/login"


def test_generate_tests_endpoint_handles_generic_workflow(client) -> None:
    response = client.post(
        "/api/v1/ai/test-generation",
        json={
            "requirement": "The dashboard should support a saved view workflow",
            "scenario_limit": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["focus"] == "generic workflow"
    assert len(payload["scenarios"]) == 1