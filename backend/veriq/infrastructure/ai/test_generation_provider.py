from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from veriq.application.services.test_generation_service import (
    GeneratedSuite,
    build_test_generation_prompt,
    generate_test_suite,
)


class TestGenerationProvider(Protocol):
    """Description: Contract for generating prompts and test suites.
    Usage Example:
        provider: TestGenerationProvider = get_test_generation_provider()
    """

    def build_prompt(self, requirement: str, scenario_limit: int = 3) -> str: ...

    def generate_suite(self, requirement: str, scenario_limit: int = 3) -> GeneratedSuite: ...


@dataclass(frozen=True)
class RuleBasedTestGenerationProvider:
    """Description: Rule-based provider that delegates to the current deterministic generator.
    Usage Example:
        provider = RuleBasedTestGenerationProvider()
    """

    def build_prompt(self, requirement: str, scenario_limit: int = 3) -> str:
        return build_test_generation_prompt(requirement, scenario_limit)

    def generate_suite(self, requirement: str, scenario_limit: int = 3) -> GeneratedSuite:
        return generate_test_suite(requirement, scenario_limit)


def get_test_generation_provider() -> TestGenerationProvider:
    """Description: Return the active provider implementation for test generation.
    Parameters:
        None
    Returns:
        TestGenerationProvider: Active provider.
    Usage Example:
        provider = get_test_generation_provider()
    """

    # If environment requests a model-backed provider, attempt to construct it.
    model_provider = _make_model_provider_from_env()
    if model_provider is not None:
        return model_provider

    return RuleBasedTestGenerationProvider()


def _make_model_provider_from_env() -> TestGenerationProvider | None:
    """Try to construct a model-backed provider from environment variables.

    Environment variables read (optional):
      - VERIQ_TEST_GENERATION_PROVIDER: if set to "model" will attempt model provider
      - VERIQ_LLM_MODEL_NAME: Hugging Face model name (optional)
      - VERIQ_LLM_ADAPTER_DIR: LoRA adapter dir (optional)
    If the heavy dependencies are not installed, gracefully return None.
    """
    # Prefer explicit runtime config overrides when present (allows toggling
    # provider at runtime without process restart). Fall back to Settings.
    from veriq.infrastructure.config.runtime import get_runtime_config
    from veriq.infrastructure.config.settings import get_settings

    runtime = get_runtime_config()
    # Ensure Settings picks up any env var changes made in tests/runtime.
    try:
        get_settings.cache_clear()
    except Exception:
        pass
    mode = runtime.test_generation_provider or get_settings().test_generation_provider or "rule"
    if mode.lower() != "model":
        return None

    model_name = runtime.llm_model_name or get_settings().llm_model_name
    adapter_dir = runtime.llm_adapter_dir or get_settings().llm_adapter_dir

    try:
        from veriq.infrastructure.ai.llm_client import HuggingFaceLLMClient

        client = None
        if model_name:
            try:
                client = HuggingFaceLLMClient(model_name, adapter_dir)
            except Exception:
                client = None

        return ModelTestGenerationProvider(client=client)
    except Exception:
        # transformers or peft may not be installed in this environment; fall back
        return ModelTestGenerationProvider(client=None)


# --- Model-backed provider (adapter) ---
class LLMClient(Protocol):
    """Minimal protocol describing an LLM client used by the model provider.
    Implementations may call remote LLM APIs or local model runners. The
    `generate` method accepts optional generation keyword arguments such as
    `do_sample`, `temperature`, `top_k`, `top_p`, and `max_new_tokens`.
    """

    def generate(self, prompt: str, **generation_options) -> str: ...


@dataclass
class GenerationMetadata:
    """Tracks metadata about a model generation request."""

    model: str | None = None
    cost: float | None = None
    raw_response_excerpt: str | None = None


@dataclass
class ModelTestGenerationProvider:
    """A provider implementation that would call an LLM client.

    For now this adapter uses the deterministic engine as a safe default for
    local development/testing. Real LLM clients can be injected via the
    `client` parameter.
    """

    client: LLMClient | None = None
    metadata: GenerationMetadata | None = None

    def build_prompt(self, requirement: str, scenario_limit: int = 3) -> str:
        return build_test_generation_prompt(requirement, scenario_limit)

    def generate_suite(
        self, requirement: str, scenario_limit: int = 3, **generation_options
    ) -> GeneratedSuite:
        prompt = self.build_prompt(requirement, scenario_limit)

        # If a real LLM client is provided, call it and attempt to use the
        # model output. For safety in tests we fall back to the deterministic
        # generator to return a structured GeneratedSuite.
        raw = None
        if self.client is not None:
            try:
                raw = self.client.generate(prompt, **generation_options)
            except Exception:
                raw = None

        # Track metadata (non-blocking; None when unknown)
        self.metadata = GenerationMetadata(
            model=(
                getattr(self.client, "__class__", None).__name__
                if self.client is not None
                else "local-deterministic"
            ),
            cost=0.0,
            raw_response_excerpt=(raw[:200] if raw else None),
        )

        # Use deterministic generator as the canonical structured output.
        return generate_test_suite(requirement, scenario_limit)
