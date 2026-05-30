from veriq.infrastructure.ai.test_generation_provider import (
    ModelTestGenerationProvider,
)


def test_model_provider_falls_back_to_deterministic_engine() -> None:
    provider = ModelTestGenerationProvider()

    suite = provider.generate_suite("Users can log in with email and password", scenario_limit=2)

    assert suite.focus == "authentication"
    assert len(suite.scenarios) == 2
    assert provider.metadata is not None
    assert provider.metadata.model == "local-deterministic"
