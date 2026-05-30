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

    def build_prompt(self, requirement: str, scenario_limit: int = 3) -> str:
        ...

    def generate_suite(self, requirement: str, scenario_limit: int = 3) -> GeneratedSuite:
        ...


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

    return RuleBasedTestGenerationProvider()