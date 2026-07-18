"""Planner Agent — analyzes requirements and generates test strategies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestStrategy:
    """Test strategy for a requirement."""
    requirement: str
    focus_area: str
    entry_point: str
    coverage_type: str  # happy_path, edge_case, negative, comprehensive
    estimated_scenarios: int
    tags: list[str]


class PlannerAgent:
    """Analyzes requirements and generates test strategies."""

    def analyze_requirement(
        self,
        requirement: str,
        scenario_limit: int = 3,
    ) -> dict:
        """Analyze requirement and generate test strategy.
        
        Args:
            requirement: Natural language requirement
            scenario_limit: Maximum scenarios to plan
            
        Returns:
            Test strategy plan
        """
        focus, tags, entry_point = self._detect_focus(requirement)
        
        return {
            "requirement": requirement.strip(),
            "focus_area": focus,
            "entry_point": entry_point,
            "tags": tags,
            "coverage_types": ["happy_path", "edge_case", "negative"],
            "estimated_scenarios": min(scenario_limit, 5),
            "priority": self._calculate_priority(focus),
            "recommended_assertions": self._recommend_assertions(focus),
        }

    def _detect_focus(self, requirement: str) -> tuple[str, list[str], str]:
        """Detect the focus area from requirement text."""
        normalized = requirement.lower()
        
        if any(k in normalized for k in ["login", "sign in", "authenticate", "password"]):
            return "authentication", ["auth", "security", "smoke"], "/login"
        if any(k in normalized for k in ["checkout", "payment", "cart", "order"]):
            return "checkout", ["commerce", "billing", "smoke"], "/checkout"
        if any(k in normalized for k in ["search", "filter", "sort"]):
            return "search", ["discovery", "ui", "smoke"], "/search"
        if any(k in normalized for k in ["profile", "account", "settings"]):
            return "account management", ["profile", "settings", "ui"], "/account"
        if any(k in normalized for k in ["create", "form", "submit"]):
            return "form handling", ["crud", "ui"], "/create"
        if any(k in normalized for k in ["delete", "remove"]):
            return "deletion", ["destructive", "safety"], "/delete"
        if any(k in normalized for k in ["export", "download"]):
            return "export", ["data", "integration"], "/export"
        if any(k in normalized for k in ["upload", "import"]):
            return "upload", ["data", "integration"], "/upload"
        
        return "general workflow", ["regression", "smoke", "ui"], "/feature"

    def _calculate_priority(self, focus: str) -> str:
        """Calculate priority based on focus area."""
        high_priority = ["authentication", "checkout", "payment"]
        medium_priority = ["profile", "account management", "form handling"]
        
        if focus in high_priority:
            return "high"
        elif focus in medium_priority:
            return "medium"
        return "low"

    def _recommend_assertions(self, focus: str) -> list[str]:
        """Recommend assertions based on focus area."""
        assertions_map = {
            "authentication": [
                "User is logged in (JWT visible)",
                "Dashboard is accessible",
                "User data displayed correctly",
            ],
            "checkout": [
                "Order confirmation visible",
                "Payment processed",
                "Confirmation email sent",
            ],
            "search": [
                "Results displayed",
                "Filters applied correctly",
                "Sorting works as expected",
            ],
        }
        return assertions_map.get(focus, ["Expected outcome achieved", "No errors visible"])
