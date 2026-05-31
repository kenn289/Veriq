from fastapi.testclient import TestClient

from veriq.infrastructure.ai import test_generation_provider as provider_mod
from veriq.main import app


def test_api_uses_model_provider(monkeypatch, tmp_path):
    # Configure environment to pick the model provider
    monkeypatch.setenv("VERIQ_TEST_GENERATION_PROVIDER", "model")
    monkeypatch.setenv("VERIQ_LLM_MODEL_NAME", "dummy-model")

    # Fake HuggingFace client that returns a deterministic response quickly
    class FakeClient:
        def __init__(self, model_name, adapter_dir=None):
            self.model_name = model_name

        def generate(self, prompt: str, **opts):
            return "FAKE_GENERATION_RESPONSE: " + prompt[:100]

    # Construct a provider instance with our fake client and ensure the app
    # uses the same provider object so we can observe metadata after the call.
    provider_instance = provider_mod.ModelTestGenerationProvider(
        client=FakeClient("dummy-model")
    )
    # Patch the symbol imported into the route module so the endpoint uses
    # our provider instance during the request handling.
    monkeypatch.setattr(
        "veriq.api.v1.routes.test_generation.get_test_generation_provider",
        lambda: provider_instance,
    )

    client = TestClient(app)

    payload = {
        "requirement": "Users can log in with email and password",
        "scenario_limit": 2,
    }
    resp = client.post("/api/v1/ai/test-generation", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["focus"] == "authentication"
    assert len(body["scenarios"]) == 2
    # Ensure metadata was recorded on the provider instance when model path was used
    # The provider instance we injected should have metadata recorded
    assert provider_instance.metadata is not None
    assert "FAKE_GENERATION_RESPONSE" in (
        provider_instance.metadata.raw_response_excerpt or ""
    )
