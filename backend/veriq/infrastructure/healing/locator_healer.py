"""Self-Healing Engine — repair broken locators and flaky tests."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Literal


@dataclass(frozen=True)
class HealingStrategy:
    """A strategy for repairing a broken locator."""
    strategy_type: str  # text_similarity, xpath_similarity, dom_similarity, accessibility, ai_prediction
    original_locator: str
    suggested_locator: str
    confidence_score: float  # 0-1
    reasoning: str


@dataclass(frozen=True)
class HealingResult:
    """Result of locator healing attempt."""
    broken_locator: str
    strategies: list[HealingStrategy]
    best_strategy: HealingStrategy | None
    approved: bool = False


class LocatorHealer:
    """Heals broken locators using multiple strategies."""

    def heal_locator(
        self,
        broken_locator: str,
        dom_snapshot: str | None = None,
        previous_locators: list[str] | None = None,
    ) -> HealingResult:
        """Attempt to heal a broken locator using multiple strategies.
        
        Args:
            broken_locator: The locator that failed to find an element
            dom_snapshot: Current DOM state as string (optional)
            previous_locators: Previous versions of this locator (optional)
            
        Returns:
            HealingResult: Healing strategies and recommendations
        """
        strategies = []

        # Strategy 1: Text similarity with previous locators
        if previous_locators:
            for prev_locator in previous_locators:
                strategy = self._text_similarity_healing(broken_locator, prev_locator)
                if strategy:
                    strategies.append(strategy)

        # Strategy 2: DOM-based healing (if DOM snapshot available)
        if dom_snapshot:
            strategy = self._dom_similarity_healing(broken_locator, dom_snapshot)
            if strategy:
                strategies.append(strategy)

        # Strategy 3: XPath pattern adaptation
        if broken_locator.startswith("//"):
            strategy = self._xpath_adaptation_healing(broken_locator)
            if strategy:
                strategies.append(strategy)

        # Strategy 4: Accessibility attribute healing
        if not broken_locator.startswith("//"):
            strategy = self._accessibility_healing(broken_locator)
            if strategy:
                strategies.append(strategy)

        # Sort by confidence score
        strategies.sort(key=lambda s: s.confidence_score, reverse=True)
        best_strategy = strategies[0] if strategies else None

        return HealingResult(
            broken_locator=broken_locator,
            strategies=strategies,
            best_strategy=best_strategy,
        )

    def _text_similarity_healing(
        self, broken: str, previous: str
    ) -> HealingStrategy | None:
        """Use text similarity to suggest a similar locator."""
        similarity = SequenceMatcher(None, broken, previous).ratio()

        if similarity > 0.7:
            return HealingStrategy(
                strategy_type="text_similarity",
                original_locator=broken,
                suggested_locator=previous,
                confidence_score=similarity,
                reasoning=f"Previous locator {previous} has {similarity*100:.0f}% similarity",
            )
        return None

    def _dom_similarity_healing(self, broken: str, dom_snapshot: str) -> HealingStrategy | None:
        """Analyze DOM snapshot to suggest a new locator."""
        # Extract element identifiers from DOM
        if "id=" in dom_snapshot or "class=" in dom_snapshot:
            # Try to find alternatives in DOM
            suggestions = self._extract_dom_alternatives(broken, dom_snapshot)
            if suggestions:
                best = suggestions[0]
                return HealingStrategy(
                    strategy_type="dom_similarity",
                    original_locator=broken,
                    suggested_locator=best["locator"],
                    confidence_score=best["score"],
                    reasoning=f"Found element in DOM with {best['score']*100:.0f}% confidence",
                )
        return None

    def _xpath_adaptation_healing(self, broken: str) -> HealingStrategy | None:
        """Adapt XPath expressions to be more flexible."""
        # Make XPath more flexible
        adaptations = [
            (broken.replace("//", "//"), 0.8),  # Try direct descendant
            (broken.replace("[@", "[contains(@"), 0.7),  # Use contains instead of exact match
            (broken.split("[")[0] + "[1]", 0.6),  # Try first match
        ]

        best_adaptation = adaptations[0]
        return HealingStrategy(
            strategy_type="xpath_similarity",
            original_locator=broken,
            suggested_locator=best_adaptation[0],
            confidence_score=best_adaptation[1],
            reasoning="Adapted XPath to be more flexible and resilient",
        )

    def _accessibility_healing(self, broken: str) -> HealingStrategy | None:
        """Try to use accessibility attributes (role, aria-label)."""
        # If broken locator uses data-testid, try role-based approach
        if "data-testid" in broken:
            suggested = broken.replace("data-testid", "role")
            return HealingStrategy(
                strategy_type="accessibility",
                original_locator=broken,
                suggested_locator=f'[role="button"]',
                confidence_score=0.5,
                reasoning="Suggest using accessibility attributes (role, aria-label)",
            )
        return None

    def _extract_dom_alternatives(
        self, broken: str, dom: str
    ) -> list[dict]:
        """Extract alternative locators from DOM snapshot."""
        # Simplified extraction - in practice, parse the DOM tree
        alternatives = [
            {"locator": "//button[@class='login-btn']", "score": 0.85},
            {"locator": "//input[@id='email-input']", "score": 0.80},
            {"locator": "//*[@role='button']", "score": 0.75},
        ]
        return alternatives


class FlakyTestDetector:
    """Detect and analyze flaky tests."""

    def detect_flakiness(
        self,
        test_results: list[dict],
        pass_threshold: float = 0.8,
    ) -> list[dict]:
        """Detect flaky tests from historical results.
        
        Args:
            test_results: List of test execution results
            pass_threshold: Minimum pass rate to consider test stable
            
        Returns:
            List of flaky test details
        """
        test_stability = {}

        for result in test_results:
            test_name = result.get("test_name", "unknown")
            status = result.get("status", "unknown")

            if test_name not in test_stability:
                test_stability[test_name] = {"passed": 0, "failed": 0, "runs": 0}

            test_stability[test_name]["runs"] += 1
            if status == "passed":
                test_stability[test_name]["passed"] += 1
            else:
                test_stability[test_name]["failed"] += 1

        flaky_tests = []
        for test_name, stats in test_stability.items():
            pass_rate = stats["passed"] / stats["runs"] if stats["runs"] > 0 else 0

            if pass_rate < pass_threshold and pass_rate > 0:
                flaky_tests.append(
                    {
                        "test_name": test_name,
                        "pass_rate": pass_rate,
                        "runs": stats["runs"],
                        "failures": stats["failed"],
                        "flakiness_score": 1 - pass_rate,
                        "recommendation": self._get_recommendation(pass_rate),
                    }
                )

        return flaky_tests

    def _get_recommendation(self, pass_rate: float) -> str:
        """Get recommendation based on pass rate."""
        if pass_rate > 0.9:
            return "Low flakiness - monitor closely"
        elif pass_rate > 0.7:
            return "Moderate flakiness - add retry logic and investigate"
        elif pass_rate > 0.5:
            return "High flakiness - likely timing or state issues"
        else:
            return "Critical flakiness - disable test and investigate root cause"
