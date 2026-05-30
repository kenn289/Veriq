from veriq.infrastructure.ai import test_generation_provider as provider_mod
from veriq.infrastructure.ai.test_generation_provider import (
    ModelTestGenerationProvider,
    RuleBasedTestGenerationProvider,
    get_test_generation_provider,
)


def test_default_provider_is_rule_based(monkeypatch) -> None:
    monkeypatch.delenv("VERIQ_TEST_GENERATION_PROVIDER", raising=False)
    p = get_test_generation_provider()
    assert isinstance(p, RuleBasedTestGenerationProvider)


def test_env_model_provider_selected(monkeypatch) -> None:
    monkeypatch.setenv("VERIQ_TEST_GENERATION_PROVIDER", "model")
    # Ensure we can call selection; client may be None and that's acceptable
    p = provider_mod.get_test_generation_provider()
    assert isinstance(p, ModelTestGenerationProvider)
