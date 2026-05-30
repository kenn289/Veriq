from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedStep:
    """Description: Generated test step for a scenario.
    Usage Example:
        step = GeneratedStep(order=1, action="navigate", target="/login")
    """

    order: int
    action: str
    target: str | None = None
    value: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class GeneratedScenario:
    """Description: Generated test scenario with steps and assertions.
    Usage Example:
        scenario = GeneratedScenario(name="Successful login", description="...", priority=1)
    """

    name: str
    description: str
    priority: int
    preconditions: list[str]
    steps: list[GeneratedStep]
    assertions: list[str]
    tags: list[str]


@dataclass(frozen=True)
class GeneratedSuite:
    """Description: Generated suite response for a requirement.
    Usage Example:
        suite = GeneratedSuite(requirement="Login works", summary="...", scenarios=[])
    """

    requirement: str
    summary: str
    focus: str
    scenarios: list[GeneratedScenario]


@dataclass(frozen=True)
class RuleBasedTestGenerationEngine:
    """Description: Deterministic engine that can later be swapped for a model-backed provider.
    Usage Example:
        engine = RuleBasedTestGenerationEngine()
        suite = engine.generate_suite("Users can log in")
    """

    def build_prompt(self, requirement: str, scenario_limit: int = 3) -> str:
        return build_test_generation_prompt(requirement, scenario_limit)

    def generate_suite(self, requirement: str, scenario_limit: int = 3) -> GeneratedSuite:
        return _generate_rule_based_suite(requirement, scenario_limit)


def get_test_generation_engine() -> RuleBasedTestGenerationEngine:
    """Description: Return the active test generation engine implementation.
    Parameters:
        None
    Returns:
        RuleBasedTestGenerationEngine: Active engine instance.
    Usage Example:
        engine = get_test_generation_engine()
    """

    return RuleBasedTestGenerationEngine()


def build_test_generation_prompt(requirement: str, scenario_limit: int = 3) -> str:
    """Description: Build a structured prompt for test generation.
    Parameters:
        requirement: Natural-language product requirement.
        scenario_limit: Maximum number of scenarios to request.
    Returns:
        str: Prompt text ready for a model provider.
    Usage Example:
        prompt = build_test_generation_prompt("Users can log in")
    """

    focus, tags, entry_point = _detect_focus(requirement)
    tag_text = ", ".join(tags)
    return (
        "You are a senior QA architect generating test scenarios.\n"
        f"Requirement: {requirement.strip()}\n"
        f"Detected focus: {focus}\n"
        f"Recommended entry point: {entry_point}\n"
        f"Suggested tags: {tag_text}\n"
        f"Scenario limit: {scenario_limit}\n"
        "Output requirements:\n"
        "- Return a concise suite summary.\n"
        "- Include happy path, negative path, and edge-case coverage when possible.\n"
        "- Use ordered steps with actions, targets, and assertions.\n"
        "- Keep the output deterministic and implementation-ready."
    )


def _detect_focus(requirement: str) -> tuple[str, list[str], str]:
    normalized = requirement.lower()
    if any(keyword in normalized for keyword in ["login", "sign in", "authenticate", "password"]):
        return "authentication", ["auth", "security", "smoke"], "/login"
    if any(keyword in normalized for keyword in ["checkout", "payment", "cart", "order"]):
        return "checkout", ["commerce", "billing", "smoke"], "/checkout"
    if any(keyword in normalized for keyword in ["search", "filter", "sort"]):
        return "search", ["discovery", "ui", "smoke"], "/search"
    if any(keyword in normalized for keyword in ["profile", "account", "settings"]):
        return "account management", ["profile", "settings", "ui"], "/account"
    return "generic workflow", ["regression", "smoke", "ui"], "/feature"


def _base_steps(entry_point: str) -> list[GeneratedStep]:
    return [
        GeneratedStep(
            order=1,
            action="navigate",
            target=entry_point,
            description=f"Open the {entry_point} entry point.",
        ),
        GeneratedStep(
            order=2,
            action="interact",
            description="Perform the primary user action described in the requirement.",
        ),
        GeneratedStep(
            order=3,
            action="assert",
            description="Verify the expected outcome is visible or persisted.",
        ),
    ]


def _validation_steps(entry_point: str) -> list[GeneratedStep]:
    return [
        GeneratedStep(
            order=1,
            action="navigate",
            target=entry_point,
            description=f"Open the {entry_point} entry point.",
        ),
        GeneratedStep(
            order=2,
            action="interact",
            value="invalid-input",
            description="Submit an invalid or incomplete payload.",
        ),
        GeneratedStep(
            order=3,
            action="assert",
            description="Verify the validation message or rejection state is shown.",
        ),
    ]


def _recovery_steps(entry_point: str) -> list[GeneratedStep]:
    return [
        GeneratedStep(
            order=1,
            action="navigate",
            target=entry_point,
            description=f"Open the {entry_point} entry point.",
        ),
        GeneratedStep(
            order=2,
            action="interact",
            description="Trigger an unexpected or edge-case input path.",
        ),
        GeneratedStep(
            order=3,
            action="assert",
            description="Verify the workflow handles the edge case safely.",
        ),
    ]


def _generate_rule_based_suite(requirement: str, scenario_limit: int = 3) -> GeneratedSuite:
    """Description: Generate a deterministic test suite from a natural-language requirement.
    Parameters:
        requirement: Natural-language product requirement.
        scenario_limit: Maximum number of scenarios to emit.
    Returns:
        GeneratedSuite: Structured test design output.
    Usage Example:
        suite = generate_test_suite("Users can log in with email and password")
    """

    focus, tags, entry_point = _detect_focus(requirement)
    _ = build_test_generation_prompt(requirement, scenario_limit)

    scenarios: list[GeneratedScenario] = [
        GeneratedScenario(
            name=f"Successful {focus}",
            description=f"Validate the primary happy path for {focus}.",
            priority=1,
            preconditions=["User has access to the application", "Required test data exists"],
            steps=_base_steps(entry_point),
            assertions=["The expected success state is visible"],
            tags=tags,
        )
    ]

    if scenario_limit > 1:
        scenarios.append(
            GeneratedScenario(
                name=f"Invalid {focus} input",
                description=f"Verify the validation behavior for invalid {focus} data.",
                priority=2,
                preconditions=["User is on the relevant screen"],
                steps=_validation_steps(entry_point),
                assertions=["Validation feedback is shown"],
                tags=tags + ["negative"],
            )
        )

    if scenario_limit > 2:
        scenarios.append(
            GeneratedScenario(
                name=f"Edge-case {focus} recovery",
                description=f"Exercise a recovery or edge-case path for {focus}.",
                priority=3,
                preconditions=["User is on the relevant screen"],
                steps=_recovery_steps(entry_point),
                assertions=["The application handles the edge case safely"],
                tags=tags + ["edge-case"],
            )
        )

    summary = f"Generated {len(scenarios)} scenario{'s' if len(scenarios) != 1 else ''} for {focus}."
    return GeneratedSuite(
        requirement=requirement.strip(),
        summary=summary,
        focus=focus,
        scenarios=scenarios[:scenario_limit],
    )


def generate_test_suite(requirement: str, scenario_limit: int = 3) -> GeneratedSuite:
    """Description: Generate a test suite skeleton from a natural-language requirement.
    Parameters:
        requirement: Natural-language product requirement.
        scenario_limit: Maximum number of scenarios to emit.
    Returns:
        GeneratedSuite: Structured test design output.
    Usage Example:
        suite = generate_test_suite("Users can log in with email and password")
    """

    engine = get_test_generation_engine()
    return engine.generate_suite(requirement, scenario_limit)