"""Maintenance Agent — identify and fix test issues automatically."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MaintenanceIssueType(str, Enum):
    """Types of maintenance issues."""
    DUPLICATE_TEST = "duplicate_test"
    BROKEN_LOCATOR = "broken_locator"
    FLAKY_TEST = "flaky_test"
    SLOW_TEST = "slow_test"
    UNCLEAR_ASSERTION = "unclear_assertion"
    MISSING_CLEANUP = "missing_cleanup"
    OUTDATED_PATTERN = "outdated_pattern"
    UNUSED_HELPER = "unused_helper"


@dataclass(frozen=True)
class MaintenanceIssue:
    """A maintenance issue detected in tests."""
    issue_type: MaintenanceIssueType
    test_name: str
    severity: str  # high, medium, low
    description: str
    suggested_fix: str
    auto_fixable: bool


@dataclass(frozen=True)
class MaintenanceReport:
    """Report of test maintenance issues."""
    total_tests: int
    issues_found: int
    issues: list[MaintenanceIssue]
    auto_fixable_count: int
    refactoring_opportunities: list[str]
    estimated_fix_time_hours: float


class MaintenanceAgent:
    """Identifies and suggests fixes for test maintenance issues."""

    def analyze_tests(self, test_suite: dict) -> MaintenanceReport:
        """Analyze test suite for maintenance issues.
        
        Args:
            test_suite: Dictionary with test data
                - 'tests': list of test dicts
                - 'code': test code content
                
        Returns:
            MaintenanceReport: Maintenance analysis
        """
        tests = test_suite.get("tests", [])
        code = test_suite.get("code", "")

        total_tests = len(tests)
        issues = []

        # Check for duplicates
        issues.extend(self._detect_duplicates(tests, code))

        # Check for broken locators
        issues.extend(self._detect_broken_locators(tests, code))

        # Check for flaky patterns
        issues.extend(self._detect_flaky_patterns(tests, code))

        # Check for slow tests
        issues.extend(self._detect_slow_tests(tests, code))

        # Check for unclear assertions
        issues.extend(self._detect_unclear_assertions(tests, code))

        # Check for cleanup issues
        issues.extend(self._detect_cleanup_issues(tests, code))

        # Check for outdated patterns
        issues.extend(self._detect_outdated_patterns(code))

        auto_fixable = sum(1 for i in issues if i.auto_fixable)
        refactoring_opps = self._identify_refactoring_opportunities(tests, code)
        estimated_time = self._estimate_fix_time(issues)

        return MaintenanceReport(
            total_tests=total_tests,
            issues_found=len(issues),
            issues=issues,
            auto_fixable_count=auto_fixable,
            refactoring_opportunities=refactoring_opps,
            estimated_fix_time_hours=estimated_time,
        )

    def _detect_duplicates(self, tests: list[dict], code: str) -> list[MaintenanceIssue]:
        """Detect duplicate tests."""
        issues = []
        test_names = [t.get("name") for t in tests]
        seen = set()

        for name in test_names:
            if name in seen:
                issues.append(
                    MaintenanceIssue(
                        issue_type=MaintenanceIssueType.DUPLICATE_TEST,
                        test_name=name,
                        severity="high",
                        description=f"Test '{name}' is defined multiple times",
                        suggested_fix="Merge duplicate test cases or rename",
                        auto_fixable=False,
                    )
                )
            seen.add(name)

        return issues

    def _detect_broken_locators(self, tests: list[dict], code: str) -> list[MaintenanceIssue]:
        """Detect tests with broken locators."""
        issues = []

        # Look for non-existent selectors or XPath patterns
        broken_patterns = [r"//*[@id='']", r"querySelector('')"]
        for test in tests:
            test_code = test.get("code", "")
            for pattern in broken_patterns:
                if pattern in test_code:
                    issues.append(
                        MaintenanceIssue(
                            issue_type=MaintenanceIssueType.BROKEN_LOCATOR,
                            test_name=test.get("name", "unknown"),
                            severity="high",
                            description=f"Empty or invalid locator found",
                            suggested_fix="Use Self-Healing Engine or fix locator manually",
                            auto_fixable=True,
                        )
                    )

        return issues

    def _detect_flaky_patterns(self, tests: list[dict], code: str) -> list[MaintenanceIssue]:
        """Detect flaky test patterns."""
        issues = []

        flaky_indicators = [
            "sleep(", "time.sleep", "setTimeout",
            "wait_for", "wait(", "await",
        ]

        for test in tests:
            test_code = test.get("code", "")
            for indicator in flaky_indicators:
                if indicator in test_code:
                    issues.append(
                        MaintenanceIssue(
                            issue_type=MaintenanceIssueType.FLAKY_TEST,
                            test_name=test.get("name", "unknown"),
                            severity="medium",
                            description=f"Potential timing issue detected ({indicator})",
                            suggested_fix="Use explicit waits instead of sleep/timeout",
                            auto_fixable=True,
                        )
                    )
                    break

        return issues

    def _detect_slow_tests(self, tests: list[dict], code: str) -> list[MaintenanceIssue]:
        """Detect potentially slow tests."""
        issues = []

        for test in tests:
            duration = test.get("duration_seconds", 0)
            if duration > 10:
                issues.append(
                    MaintenanceIssue(
                        issue_type=MaintenanceIssueType.SLOW_TEST,
                        test_name=test.get("name", "unknown"),
                        severity="low",
                        description=f"Test is slow ({duration}s)",
                        suggested_fix="Parallelize or optimize expensive operations",
                        auto_fixable=False,
                    )
                )

        return issues

    def _detect_unclear_assertions(self, tests: list[dict], code: str) -> list[MaintenanceIssue]:
        """Detect tests with unclear assertions."""
        issues = []

        for test in tests:
            test_code = test.get("code", "")

            # No assertions at all
            if "assert" not in test_code.lower():
                issues.append(
                    MaintenanceIssue(
                        issue_type=MaintenanceIssueType.UNCLEAR_ASSERTION,
                        test_name=test.get("name", "unknown"),
                        severity="high",
                        description="Test has no assertions",
                        suggested_fix="Add clear assertions to verify expected behavior",
                        auto_fixable=False,
                    )
                )

            # Generic assertions
            if "assert True" in test_code or "assertTrue()" in test_code:
                issues.append(
                    MaintenanceIssue(
                        issue_type=MaintenanceIssueType.UNCLEAR_ASSERTION,
                        test_name=test.get("name", "unknown"),
                        severity="medium",
                        description="Generic assertion - unclear what is being tested",
                        suggested_fix="Use specific assertions with descriptive messages",
                        auto_fixable=False,
                    )
                )

        return issues

    def _detect_cleanup_issues(self, tests: list[dict], code: str) -> list[MaintenanceIssue]:
        """Detect missing cleanup."""
        issues = []

        cleanup_patterns = ["tearDown", "cleanup", "afterEach", "@after"]
        has_cleanup = any(p in code for p in cleanup_patterns)

        if not has_cleanup and len([t for t in tests if t.get("duration_seconds", 0) > 5]) > 0:
            issues.append(
                MaintenanceIssue(
                    issue_type=MaintenanceIssueType.MISSING_CLEANUP,
                    test_name="suite",
                    severity="medium",
                    description="No cleanup/teardown found - may cause test isolation issues",
                    suggested_fix="Add tearDown or cleanup methods for resource management",
                    auto_fixable=False,
                )
            )

        return issues

    def _detect_outdated_patterns(self, code: str) -> list[MaintenanceIssue]:
        """Detect outdated test patterns."""
        issues = []

        # Old Selenium patterns
        if "find_element_by_" in code:
            issues.append(
                MaintenanceIssue(
                    issue_type=MaintenanceIssueType.OUTDATED_PATTERN,
                    test_name="suite",
                    severity="low",
                    description="Using deprecated Selenium patterns",
                    suggested_fix="Migrate to modern WebDriver API or Playwright",
                    auto_fixable=False,
                )
            )

        # No framework detected
        if "import" not in code.lower():
            issues.append(
                MaintenanceIssue(
                    issue_type=MaintenanceIssueType.OUTDATED_PATTERN,
                    test_name="suite",
                    severity="medium",
                    description="Tests appear to have minimal structure",
                    suggested_fix="Use modern test framework (pytest, playwright, etc)",
                    auto_fixable=False,
                )
            )

        return issues

    def _identify_refactoring_opportunities(self, tests: list[dict], code: str) -> list[str]:
        """Identify refactoring opportunities."""
        opportunities = []

        # Common code that could be extracted
        if code.count("login") > 2:
            opportunities.append("Extract login helper - reused 3+ times")
        if code.count("wait") > 3:
            opportunities.append("Extract wait utilities into helper module")
        if code.count("assert") > 10:
            opportunities.append("Extract assertions into custom matchers")

        # Large test methods
        long_tests = [t for t in tests if t.get("lines", 0) > 50]
        if long_tests:
            opportunities.append(f"Split {len(long_tests)} large test methods")

        # Repeated setup
        if "setUp" in code or "@fixture" in code:
            opportunities.append("Consolidate fixture setup to reduce duplication")

        return opportunities

    def _estimate_fix_time(self, issues: list[MaintenanceIssue]) -> float:
        """Estimate time to fix all issues."""
        time_per_issue = {
            MaintenanceIssueType.DUPLICATE_TEST: 0.5,
            MaintenanceIssueType.BROKEN_LOCATOR: 0.25,
            MaintenanceIssueType.FLAKY_TEST: 1.0,
            MaintenanceIssueType.SLOW_TEST: 0.5,
            MaintenanceIssueType.UNCLEAR_ASSERTION: 0.5,
            MaintenanceIssueType.MISSING_CLEANUP: 1.0,
            MaintenanceIssueType.OUTDATED_PATTERN: 2.0,
            MaintenanceIssueType.UNUSED_HELPER: 0.25,
        }

        total = sum(
            time_per_issue.get(i.issue_type, 0.5)
            for i in issues
        )
        return total
