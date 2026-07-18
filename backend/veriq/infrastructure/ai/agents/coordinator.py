"""Coordinator Agent — orchestrates multi-agent test generation workflows."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from veriq.infrastructure.ai.agents.planner import PlannerAgent
from veriq.infrastructure.ai.agents.designer import DesignerAgent
from veriq.infrastructure.ai.agents.framework import FrameworkAgent


class AgentPhase(str, Enum):
    """Phases in the test generation workflow."""
    PLANNING = "planning"
    DESIGN = "design"
    FRAMEWORK = "framework"
    COMPLETE = "complete"


@dataclass(frozen=True)
class CoordinatorResult:
    """Result from full test generation workflow."""
    test_plan: dict
    test_cases: list[dict]
    framework_code: dict
    phases_executed: list[str]


class CoordinatorAgent:
    """Orchestrates test generation across multiple specialized agents."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.designer = DesignerAgent()
        self.framework = FrameworkAgent()

    async def orchestrate_test_generation(
        self,
        requirement: str,
        target_framework: str = "playwright-ts",
        scenario_limit: int = 3,
    ) -> CoordinatorResult:
        """Execute the full test generation pipeline.
        
        Args:
            requirement: Natural language test requirement
            target_framework: Code generation target
            scenario_limit: Max scenarios to generate
            
        Returns:
            CoordinatorResult: Full workflow output
        """
        return self.orchestrate_test_generation_sync(requirement, target_framework, scenario_limit)
    
    def orchestrate_test_generation_sync(
        self,
        requirement: str,
        target_framework: str = "playwright-ts",
        scenario_limit: int = 3,
    ) -> CoordinatorResult:
        """Execute the full test generation pipeline (sync version).
        
        Args:
            requirement: Natural language test requirement
            target_framework: Code generation target
            scenario_limit: Max scenarios to generate
            
        Returns:
            CoordinatorResult: Full workflow output
        """
        phases_executed = []

        # Phase 1: Planning — analyze requirement and generate strategy
        plan = self.planner.analyze_requirement(requirement, scenario_limit)
        phases_executed.append(AgentPhase.PLANNING.value)

        # Phase 2: Design — generate detailed test cases
        test_cases = self.designer.design_test_cases(plan, requirement)
        phases_executed.append(AgentPhase.DESIGN.value)

        # Phase 3: Framework — generate runnable code
        framework_code = self.framework.generate_framework(
            test_cases, target_framework
        )
        phases_executed.append(AgentPhase.FRAMEWORK.value)

        return CoordinatorResult(
            test_plan=plan,
            test_cases=test_cases,
            framework_code=framework_code,
            phases_executed=phases_executed,
        )
