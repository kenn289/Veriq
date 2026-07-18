"""Coverage Intelligence Engine — analyze coverage gaps and identify risks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageGap:
    """A gap in test coverage."""
    requirement_id: str
    requirement_description: str
    coverage_percentage: float
    tested_scenarios: list[str]
    untested_scenarios: list[str]
    risk_level: str  # high, medium, low
    priority: int  # 1-10


@dataclass(frozen=True)
class CoverageAnalysis:
    """Complete coverage analysis."""
    total_requirements: int
    total_coverage_percentage: float
    fully_covered_count: int
    partially_covered_count: int
    uncovered_count: int
    coverage_gaps: list[CoverageGap]
    critical_gaps: list[CoverageGap]
    recommendations: list[str]
    risk_areas: list[str]


class CoverageIntelligence:
    """Analyzes test coverage and identifies risks."""

    def analyze_coverage(
        self,
        requirements: list[dict],
        test_cases: list[dict],
        code_coverage: dict | None = None,
    ) -> CoverageAnalysis:
        """Analyze coverage across requirements and tests.
        
        Args:
            requirements: List of requirement dicts
            test_cases: List of test case dicts
            code_coverage: Optional code coverage report
            
        Returns:
            CoverageAnalysis: Complete coverage analysis
        """
        gaps = []
        fully_covered = 0
        partially_covered = 0

        for req in requirements:
            req_id = req.get("id")
            req_desc = req.get("description", "")

            # Find matching tests
            matching_tests = self._find_matching_tests(req_desc, test_cases)
            coverage_pct = len(matching_tests) / max(1, len(test_cases))

            if coverage_pct == 0:
                uncovered = True
                partially_covered_count = 0
            elif coverage_pct < 1.0:
                uncovered = False
                partially_covered_count = 1
                partially_covered += 1
            else:
                uncovered = False
                partially_covered_count = 0
                fully_covered += 1

            # Extract tested scenarios
            tested_scenarios = self._extract_scenarios(matching_tests)

            # Generate untested scenarios
            untested_scenarios = self._generate_untested_scenarios(req_desc)

            # Calculate risk
            risk_level = self._calculate_risk_level(req_desc, coverage_pct)
            priority = self._calculate_priority(req_desc, coverage_pct)

            gap = CoverageGap(
                requirement_id=req_id or "unknown",
                requirement_description=req_desc,
                coverage_percentage=coverage_pct,
                tested_scenarios=tested_scenarios,
                untested_scenarios=untested_scenarios,
                risk_level=risk_level,
                priority=priority,
            )

            gaps.append(gap)

        # Calculate overall coverage
        total_coverage = sum(g.coverage_percentage for g in gaps) / max(1, len(gaps))

        # Identify critical gaps
        critical_gaps = [g for g in gaps if g.risk_level == "high" and g.coverage_percentage < 0.5]

        # Generate recommendations
        recommendations = self._generate_recommendations(gaps, total_coverage)

        # Identify risk areas
        risk_areas = self._identify_risk_areas(gaps)

        uncovered_count = len(gaps) - fully_covered - partially_covered

        return CoverageAnalysis(
            total_requirements=len(requirements),
            total_coverage_percentage=total_coverage,
            fully_covered_count=fully_covered,
            partially_covered_count=partially_covered,
            uncovered_count=uncovered_count,
            coverage_gaps=gaps,
            critical_gaps=critical_gaps,
            recommendations=recommendations,
            risk_areas=risk_areas,
        )

    def _find_matching_tests(self, requirement: str, test_cases: list[dict]) -> list[dict]:
        """Find tests that match a requirement."""
        req_lower = requirement.lower()
        matching = []

        for test in test_cases:
            test_name = test.get("name", "").lower()
            test_desc = test.get("description", "").lower()

            # Simple keyword matching
            if any(word in test_name or word in test_desc for word in req_lower.split()):
                matching.append(test)

        return matching

    def _extract_scenarios(self, tests: list[dict]) -> list[str]:
        """Extract scenario names from tests."""
        scenarios = []
        for test in tests:
            scenario = test.get("scenario", test.get("name", ""))
            if scenario:
                scenarios.append(scenario)
        return scenarios

    def _generate_untested_scenarios(self, requirement: str) -> list[str]:
        """Generate potential untested scenarios."""
        scenarios = []

        # Always need edge cases
        scenarios.append(f"Edge cases for: {requirement}")

        # Often need error cases
        scenarios.append(f"Error handling for: {requirement}")

        # Concurrency if relevant
        if "concurrent" not in requirement.lower() and "parallel" not in requirement.lower():
            scenarios.append(f"Concurrent access for: {requirement}")

        # Performance
        scenarios.append(f"Performance under load for: {requirement}")

        # Internationalization
        scenarios.append(f"Internationalization for: {requirement}")

        return scenarios

    def _calculate_risk_level(self, requirement: str, coverage: float) -> str:
        """Calculate risk level based on requirement and coverage."""
        critical_keywords = ["authentication", "payment", "security", "compliance"]
        high_keywords = ["api", "data", "user", "core"]

        req_lower = requirement.lower()

        if any(k in req_lower for k in critical_keywords):
            if coverage < 0.5:
                return "high"
            elif coverage < 0.8:
                return "medium"
        elif any(k in req_lower for k in high_keywords):
            if coverage < 0.3:
                return "high"
            elif coverage < 0.7:
                return "medium"

        if coverage < 0.2:
            return "medium"
        elif coverage < 0.5:
            return "low"

        return "low"

    def _calculate_priority(self, requirement: str, coverage: float) -> int:
        """Calculate priority (1-10, where 10 is highest)."""
        critical_keywords = ["authentication", "payment", "security"]
        high_keywords = ["api", "data", "user"]

        req_lower = requirement.lower()

        # Higher priority for critical features with low coverage
        if any(k in req_lower for k in critical_keywords):
            base = 9
        elif any(k in req_lower for k in high_keywords):
            base = 7
        else:
            base = 5

        # Adjust by coverage
        priority = base - int(coverage * 4)  # -4 at full coverage

        return max(1, min(10, priority))

    def _generate_recommendations(self, gaps: list[CoverageGap], total_coverage: float) -> list[str]:
        """Generate coverage improvement recommendations."""
        recommendations = []

        if total_coverage < 0.5:
            recommendations.append("⚠️  Critical: Overall coverage is below 50% - focus on critical features")

        high_risk_gaps = [g for g in gaps if g.risk_level == "high"]
        if high_risk_gaps:
            recommendations.append(f"Focus on {len(high_risk_gaps)} high-risk gaps first")

        uncovered = [g for g in gaps if g.coverage_percentage == 0]
        if uncovered:
            recommendations.append(f"Address {len(uncovered)} completely uncovered requirements")

        # Pattern recommendations
        edge_cases_needed = [g for g in gaps if "edge case" in str(g.untested_scenarios)]
        if edge_cases_needed:
            recommendations.append("Add more edge case tests")

        error_cases_needed = [g for g in gaps if "error" in str(g.untested_scenarios)]
        if error_cases_needed:
            recommendations.append("Add error handling tests")

        return recommendations

    def _identify_risk_areas(self, gaps: list[CoverageGap]) -> list[str]:
        """Identify high-risk areas."""
        risk_areas = []

        for gap in gaps:
            if gap.risk_level == "high":
                risk_areas.append(gap.requirement_description)

        return risk_areas[:5]  # Top 5 risk areas
