"""Designer Agent — creates detailed test case designs from strategies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestCaseDesign:
    """Detailed test case design."""
    name: str
    description: str
    scenario_type: str  # happy_path, edge_case, negative
    preconditions: list[str]
    steps: list[dict]
    expected_results: list[str]
    tags: list[str]


class DesignerAgent:
    """Designs detailed test cases from strategy."""

    def design_test_cases(self, plan: dict, requirement: str) -> list[dict]:
        """Design test cases from a plan.
        
        Args:
            plan: Test strategy from PlannerAgent
            requirement: Original requirement
            
        Returns:
            List of detailed test case designs
        """
        test_cases = []
        focus = plan.get("focus_area", "general workflow")
        entry_point = plan.get("entry_point", "/")
        estimated_scenarios = plan.get("estimated_scenarios", 3)
        
        # Design happy path scenario
        test_cases.append(
            self._design_happy_path(focus, entry_point, requirement)
        )
        
        # Design edge case scenarios (if estimated_scenarios > 1)
        if estimated_scenarios > 1:
            test_cases.append(
                self._design_edge_case(focus, entry_point)
            )
        
        # Design negative scenario (if estimated_scenarios > 2)
        if estimated_scenarios > 2:
            test_cases.append(
                self._design_negative_case(focus, entry_point)
            )
        
        return test_cases

    def _design_happy_path(self, focus: str, entry_point: str, requirement: str) -> dict:
        """Design a happy path scenario."""
        return {
            "name": f"Successful {focus}",
            "description": f"Verify that {requirement.lower()} works as expected",
            "scenario_type": "happy_path",
            "preconditions": [
                "User is logged in",
                "User has required permissions",
            ],
            "steps": [
                {
                    "order": 1,
                    "action": "navigate",
                    "target": entry_point,
                    "description": f"Open the {focus} page",
                },
                {
                    "order": 2,
                    "action": "perform_primary_action",
                    "description": "Execute the primary user action",
                },
                {
                    "order": 3,
                    "action": "verify_success",
                    "description": "Verify the action was successful",
                },
            ],
            "expected_results": [
                "Action completed successfully",
                "Confirmation message displayed",
                "State persisted in database",
            ],
            "tags": ["happy_path", "smoke", "regression"],
            "priority": "high",
        }

    def _design_edge_case(self, focus: str, entry_point: str) -> dict:
        """Design an edge case scenario."""
        return {
            "name": f"Edge case - {focus}",
            "description": f"Verify boundary conditions for {focus}",
            "scenario_type": "edge_case",
            "preconditions": [
                "User is logged in",
            ],
            "steps": [
                {
                    "order": 1,
                    "action": "navigate",
                    "target": entry_point,
                    "description": f"Open the {focus} page",
                },
                {
                    "order": 2,
                    "action": "enter_boundary_value",
                    "description": "Enter a boundary value or extreme input",
                },
                {
                    "order": 3,
                    "action": "verify_handling",
                    "description": "Verify boundary condition is handled correctly",
                },
            ],
            "expected_results": [
                "Boundary value accepted or rejected gracefully",
                "No system errors",
                "User given clear feedback",
            ],
            "tags": ["edge_case", "regression"],
            "priority": "medium",
        }

    def _design_negative_case(self, focus: str, entry_point: str) -> dict:
        """Design a negative scenario."""
        return {
            "name": f"Error handling - {focus}",
            "description": f"Verify error handling in {focus}",
            "scenario_type": "negative",
            "preconditions": [
                "User is logged in",
            ],
            "steps": [
                {
                    "order": 1,
                    "action": "navigate",
                    "target": entry_point,
                    "description": f"Open the {focus} page",
                },
                {
                    "order": 2,
                    "action": "perform_invalid_action",
                    "description": "Attempt an invalid operation",
                },
                {
                    "order": 3,
                    "action": "verify_error",
                    "description": "Verify error is handled appropriately",
                },
            ],
            "expected_results": [
                "Clear error message displayed",
                "User can retry or recover",
                "No data corruption",
            ],
            "tags": ["negative", "error_handling", "regression"],
            "priority": "high",
        }
