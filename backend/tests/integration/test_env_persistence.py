from __future__ import annotations

from fastapi.testclient import TestClient


def test_env_persistence_and_get(monkeypatch, tmp_path):
    # Run the app with a clean cwd to avoid touching repo .env
    monkeypatch.chdir(tmp_path)

    from veriq.main import app

    client = TestClient(app)

    # POST to update runtime config and persist to .env
    r = client.post(
        "/api/v1/ai/config",
        json={"test_generation_provider": "model", "llm_model_name": "distilgpt2"},
    )
    assert r.status_code == 200

    env_path = tmp_path / ".env"
    assert env_path.exists(), ".env should be created by POST /api/v1/ai/config"
    content = env_path.read_text(encoding="utf-8")
    assert "VERIQ_TEST_GENERATION_PROVIDER=model" in content
    assert "VERIQ_LLM_MODEL_NAME=distilgpt2" in content

    # GET should return persisted values (the POST handler clears cached settings)
    r2 = client.get("/api/v1/ai/config")
    assert r2.status_code == 200
    body = r2.json()
    assert body["test_generation_provider"] == "model"
    assert body["llm_model_name"] == "distilgpt2"
