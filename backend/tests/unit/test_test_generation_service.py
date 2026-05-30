from __future__ import annotations

from veriq.application.services.test_generation_service import (
    build_test_generation_prompt,
    generate_test_suite,
    get_test_generation_engine,
)
from veriq.infrastructure.ai.test_generation_provider import (
    RuleBasedTestGenerationProvider,
    get_test_generation_provider,
)


def test_build_test_generation_prompt_includes_guidance() -> None:
    prompt = build_test_generation_prompt("Users can log in with email and password", scenario_limit=2)

    assert "senior QA architect" in prompt
    assert "Requirement: Users can log in with email and password" in prompt
    assert "Detected focus: authentication" in prompt
    assert "Scenario limit: 2" in prompt
    assert "happy path" in prompt


def test_generate_test_suite_for_login_requirement() -> None:
    suite = generate_test_suite("Users can log in with email and password", scenario_limit=3)

    assert suite.focus == "authentication"
    assert len(suite.scenarios) == 3
    assert suite.scenarios[0].name == "Successful authentication"
    assert suite.scenarios[0].steps[0].target == "/login"
    assert "negative" in suite.scenarios[1].tags


def test_generate_test_suite_defaults_to_generic_workflow() -> None:
    suite = generate_test_suite("The dashboard should support a saved view workflow", scenario_limit=2)

    assert suite.focus == "generic workflow"
    assert len(suite.scenarios) == 2
    assert suite.scenarios[0].tags == ["regression", "smoke", "ui"]


def test_rule_based_engine_uses_same_prompt_and_generation() -> None:
    engine = get_test_generation_engine()

    prompt = engine.build_prompt("Users can log in with email and password", scenario_limit=2)
    suite = engine.generate_suite("Users can log in with email and password", scenario_limit=2)

    assert "Scenario limit: 2" in prompt
    assert suite.focus == "authentication"
    assert len(suite.scenarios) == 2


def test_rule_based_provider_delegates_to_generator() -> None:
    provider = get_test_generation_provider()

    assert isinstance(provider, RuleBasedTestGenerationProvider)
    prompt = provider.build_prompt("Users can log in with email and password", scenario_limit=1)
    suite = provider.generate_suite("Users can log in with email and password", scenario_limit=1)

    assert "Detected focus: authentication" in prompt
    assert suite.focus == "authentication"
    assert len(suite.scenarios) == 1