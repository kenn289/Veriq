from fastapi.testclient import TestClient

from veriq.infrastructure.config.runtime import get_runtime_config
from veriq.main import app


def test_runtime_config_get_and_update():
    client = TestClient(app)

    # Read default
    r = client.get("/api/v1/ai/config")
    assert r.status_code == 200
    body = r.json()
    assert body["test_generation_provider"] in ("rule", "model")

    # Update provider to model and set a dummy model name
    r2 = client.post(
        "/api/v1/ai/config",
        json={
            "test_generation_provider": "model",
            "llm_model_name": "distilgpt2",
            "llm_adapter_dir": None,
        },
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["test_generation_provider"] == "model"

    # Ensure runtime config reflects change
    runtime = get_runtime_config()
    assert runtime.test_generation_provider == "model"
    assert runtime.llm_model_name == "distilgpt2"
