"""Failure Analysis Engine — analyze test failures and provide insights."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureSeverity(str, Enum):
    """Severity levels for test failures."""
    CRITICAL = "critical"  # System down, regression
    HIGH = "high"  # Feature broken
    MEDIUM = "medium"  # Feature degraded
    LOW = "low"  # Minor issue
    INFO = "info"  # Informational


class RootCauseType(str, Enum):
    """Types of root causes for failures."""
    LOCATOR_NOT_FOUND = "locator_not_found"
    TIMEOUT = "timeout"
    ASSERTION_FAILED = "assertion_failed"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    STATE_ERROR = "state_error"
    ENVIRONMENT_ERROR = "environment_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FailureAnalysis:
    """Complete analysis of a test failure."""
    test_name: str
    failure_message: str
    severity: FailureSeverity
    root_cause_type: RootCauseType
    root_cause_description: str
    recommendations: list[str]
    confidence_score: float  # 0-1
    affected_features: list[str]
    similar_failures: list[str]


class FailureAnalyzer:
    """Analyzes test failures and provides insights."""

    def analyze_failure(
        self,
        test_name: str,
        error_message: str,
        stack_trace: str | None = None,
        screenshot: str | None = None,
        dom_snapshot: str | None = None,
    ) -> FailureAnalysis:
        """Analyze a test failure comprehensively.
        
        Args:
            test_name: Name of the failed test
            error_message: Error message from test failure
            stack_trace: Optional stack trace
            screenshot: Optional screenshot as base64 or path
            dom_snapshot: Optional DOM snapshot
            
        Returns:
            FailureAnalysis: Comprehensive failure analysis
        """
        # Detect root cause from error message
        root_cause = self._detect_root_cause(error_message, stack_trace or "")

        # Calculate severity
        severity = self._calculate_severity(error_message, root_cause)

        # Generate recommendations
        recommendations = self._generate_recommendations(root_cause, error_message)

        # Identify affected features
        affected_features = self._identify_affected_features(test_name, error_message)

        # Find similar failures
        similar = self._find_similar_failures(error_message)

        return FailureAnalysis(
            test_name=test_name,
            failure_message=error_message,
            severity=severity,
            root_cause_type=root_cause,
            root_cause_description=self._describe_root_cause(root_cause),
            recommendations=recommendations,
            confidence_score=self._calculate_confidence(error_message, stack_trace),
            affected_features=affected_features,
            similar_failures=similar,
        )

    def _detect_root_cause(self, error_msg: str, stack_trace: str) -> RootCauseType:
        """Detect root cause from error messages and stack trace."""
        error_lower = error_msg.lower()

        # Locator-related errors
        if any(
            k in error_lower
            for k in ["no such element", "element not found", "locator", "selector"]
        ):
            return RootCauseType.LOCATOR_NOT_FOUND

        # Timeout errors
        if any(k in error_lower for k in ["timeout", "timed out", "waiting"]):
            return RootCauseType.TIMEOUT

        # Assertion errors
        if any(
            k in error_lower
            for k in ["assertion", "assert", "expected", "not equal"]
        ):
            return RootCauseType.ASSERTION_FAILED

        # Network errors
        if any(
            k in error_lower
            for k in ["network", "connection", "offline", "refused", "unreachable"]
        ):
            return RootCauseType.NETWORK_ERROR

        # Permission errors
        if any(
            k in error_lower
            for k in ["permission", "unauthorized", "forbidden", "401", "403"]
        ):
            return RootCauseType.PERMISSION_ERROR

        # State errors
        if any(
            k in error_lower
            for k in ["state", "invalid state", "precondition", "not ready"]
        ):
            return RootCauseType.STATE_ERROR

        # Environment errors
        if any(
            k in error_lower
            for k in ["environment", "config", "setup", "teardown", "fixture"]
        ):
            return RootCauseType.ENVIRONMENT_ERROR

        return RootCauseType.UNKNOWN

    def _calculate_severity(
        self, error_msg: str, root_cause: RootCauseType
    ) -> FailureSeverity:
        """Calculate severity based on error type and message."""
        error_lower = error_msg.lower()

        # Check for critical keywords
        if any(k in error_lower for k in ["crash", "critical", "fatal", "null"]):
            return FailureSeverity.CRITICAL

        if root_cause == RootCauseType.PERMISSION_ERROR:
            return FailureSeverity.HIGH

        if root_cause == RootCauseType.ASSERTION_FAILED:
            return FailureSeverity.HIGH

        if root_cause == RootCauseType.NETWORK_ERROR:
            return FailureSeverity.MEDIUM

        if root_cause == RootCauseType.LOCATOR_NOT_FOUND:
            return FailureSeverity.MEDIUM

        if root_cause == RootCauseType.TIMEOUT:
            return FailureSeverity.LOW

        return FailureSeverity.LOW

    def _generate_recommendations(
        self, root_cause: RootCauseType, error_msg: str
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations_map = {
            RootCauseType.LOCATOR_NOT_FOUND: [
                "Use Self-Healing Engine to suggest alternative locators",
                "Check if UI has changed",
                "Verify CSS/XPath selector is correct",
                "Consider using role-based or accessibility attributes",
            ],
            RootCauseType.TIMEOUT: [
                "Increase timeout threshold",
                "Check if element renders quickly",
                "Add wait conditions or visibility checks",
                "Optimize test environment performance",
            ],
            RootCauseType.ASSERTION_FAILED: [
                "Verify expected value matches actual",
                "Check if assertion is too strict",
                "Review test data and preconditions",
                "Consider adding diagnostic logging",
            ],
            RootCauseType.NETWORK_ERROR: [
                "Check network connectivity",
                "Verify API endpoints are accessible",
                "Review firewall/proxy settings",
                "Check for rate limiting or throttling",
            ],
            RootCauseType.PERMISSION_ERROR: [
                "Verify test user has correct permissions",
                "Check authentication tokens/credentials",
                "Review role-based access control",
                "Ensure test environment has proper setup",
            ],
            RootCauseType.STATE_ERROR: [
                "Verify test preconditions are met",
                "Check test setup and teardown",
                "Review test data state management",
                "Consider test isolation issues",
            ],
            RootCauseType.ENVIRONMENT_ERROR: [
                "Check test environment configuration",
                "Verify all dependencies are installed",
                "Review fixture setup/teardown",
                "Check for version mismatches",
            ],
        }

        return recommendations_map.get(root_cause, ["Investigate error message for more details"])

    def _describe_root_cause(self, root_cause: RootCauseType) -> str:
        """Get human-readable description of root cause."""
        descriptions = {
            RootCauseType.LOCATOR_NOT_FOUND: "Could not find element on page",
            RootCauseType.TIMEOUT: "Operation took too long or element didn't appear",
            RootCauseType.ASSERTION_FAILED: "Actual value didn't match expected value",
            RootCauseType.NETWORK_ERROR: "Network communication failed",
            RootCauseType.PERMISSION_ERROR: "User lacks required permissions",
            RootCauseType.STATE_ERROR: "Application was not in expected state",
            RootCauseType.ENVIRONMENT_ERROR: "Test environment misconfiguration",
            RootCauseType.UNKNOWN: "Unable to determine root cause",
        }
        return descriptions.get(root_cause, "Unknown error")

    def _identify_affected_features(self, test_name: str, error_msg: str) -> list[str]:
        """Identify which features are affected."""
        features = []

        if any(k in test_name.lower() for k in ["login", "auth", "password"]):
            features.append("Authentication")
        if any(k in test_name.lower() for k in ["checkout", "payment", "cart"]):
            features.append("Checkout")
        if any(k in test_name.lower() for k in ["search", "filter"]):
            features.append("Search")
        if any(k in test_name.lower() for k in ["profile", "account"]):
            features.append("Account Management")

        return features or ["General"]

    def _find_similar_failures(self, error_msg: str) -> list[str]:
        """Find similar historical failures."""
        # In a real system, this would query a database
        # For now, return empty list
        return []

    def _calculate_confidence(self, error_msg: str, stack_trace: str | None) -> float:
        """Calculate confidence in the analysis."""
        confidence = 0.5

        # More detailed info = higher confidence
        if error_msg and len(error_msg) > 20:
            confidence += 0.2
        if stack_trace and len(stack_trace) > 100:
            confidence += 0.3

        return min(confidence, 1.0)
