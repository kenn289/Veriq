"""PR Agent — analyze pull requests and generate targeted tests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ChangeType(str, Enum):
    """Types of code changes."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class RiskLevel(str, Enum):
    """Risk levels for changes."""
    CRITICAL = "critical"  # Core functionality, multiple files
    HIGH = "high"  # Important features, cascading changes
    MEDIUM = "medium"  # Features, isolated changes
    LOW = "low"  # Minor changes, utilities
    MINIMAL = "minimal"  # Docs, comments


@dataclass(frozen=True)
class FileChange:
    """A changed file."""
    path: str
    change_type: ChangeType
    additions: int
    deletions: int
    risk_level: RiskLevel
    affected_functions: list[str]


@dataclass(frozen=True)
class PRAnalysis:
    """Analysis of a pull request."""
    pr_number: int
    title: str
    overall_risk_level: RiskLevel
    files_changed: int
    total_changes: int
    affected_features: list[str]
    file_changes: list[FileChange]
    test_recommendations: list[str]
    coverage_gaps: list[str]
    breaking_changes: list[str]
    impact_summary: str


class PRAgent:
    """Analyzes pull requests and generates targeted tests."""

    def analyze_pr(
        self,
        pr_number: int,
        title: str,
        diff: str,
        base_branch: str = "main",
    ) -> PRAnalysis:
        """Analyze a pull request for testing requirements.
        
        Args:
            pr_number: PR number
            title: PR title
            diff: Git diff output
            base_branch: Base branch (for context)
            
        Returns:
            PRAnalysis: Complete PR analysis
        """
        # Parse diff to extract changes
        file_changes = self._parse_diff(diff)

        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(file_changes)

        # Identify affected features
        affected_features = self._identify_affected_features(file_changes)

        # Generate test recommendations
        test_recommendations = self._generate_test_recommendations(
            file_changes, affected_features
        )

        # Identify coverage gaps
        coverage_gaps = self._identify_coverage_gaps(file_changes)

        # Detect breaking changes
        breaking_changes = self._detect_breaking_changes(diff, file_changes)

        # Generate impact summary
        impact_summary = self._generate_impact_summary(
            file_changes, overall_risk, affected_features
        )

        return PRAnalysis(
            pr_number=pr_number,
            title=title,
            overall_risk_level=overall_risk,
            files_changed=len(file_changes),
            total_changes=sum(f.additions + f.deletions for f in file_changes),
            affected_features=affected_features,
            file_changes=file_changes,
            test_recommendations=test_recommendations,
            coverage_gaps=coverage_gaps,
            breaking_changes=breaking_changes,
            impact_summary=impact_summary,
        )

    def _parse_diff(self, diff: str) -> list[FileChange]:
        """Parse git diff to extract changes."""
        file_changes = []
        current_file = None
        additions = 0
        deletions = 0

        for line in diff.split("\n"):
            if line.startswith("diff --git"):
                # New file
                if current_file:
                    file_changes.append(current_file)

                # Extract file path
                parts = line.split()
                if len(parts) >= 4:
                    path = parts[3].lstrip("b/")
                    current_file = self._create_file_change(
                        path, additions, deletions
                    )
                    additions = 0
                    deletions = 0

            elif line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        if current_file:
            file_changes.append(current_file)

        return file_changes

    def _create_file_change(self, path: str, additions: int, deletions: int) -> FileChange:
        """Create a FileChange object."""
        change_type = self._determine_change_type(path, additions, deletions)
        risk_level = self._calculate_file_risk(path, additions, deletions)
        affected_functions = self._extract_affected_functions(path)

        return FileChange(
            path=path,
            change_type=change_type,
            additions=additions,
            deletions=deletions,
            risk_level=risk_level,
            affected_functions=affected_functions,
        )

    def _determine_change_type(self, path: str, additions: int, deletions: int) -> ChangeType:
        """Determine type of change."""
        if additions > 0 and deletions == 0:
            return ChangeType.ADDED
        elif deletions > 0 and additions == 0:
            return ChangeType.DELETED
        else:
            return ChangeType.MODIFIED

    def _calculate_file_risk(self, path: str, additions: int, deletions: int) -> RiskLevel:
        """Calculate risk level for a file."""
        critical_paths = [
            "auth", "payment", "security", "core", "database",
        ]
        high_paths = [
            "api", "service", "business logic",
        ]

        total_changes = additions + deletions

        # Check path
        for critical in critical_paths:
            if critical in path.lower():
                return RiskLevel.CRITICAL

        for high in high_paths:
            if high in path.lower():
                if total_changes > 50:
                    return RiskLevel.HIGH
                return RiskLevel.MEDIUM

        # Based on size
        if total_changes > 100:
            return RiskLevel.HIGH
        elif total_changes > 50:
            return RiskLevel.MEDIUM
        elif total_changes > 10:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    def _extract_affected_functions(self, path: str) -> list[str]:
        """Extract affected functions from file path."""
        # Simplified: would need to parse actual code
        functions = []
        if "login" in path:
            functions.append("login()")
        if "checkout" in path:
            functions.append("checkout()")
        if "payment" in path:
            functions.append("process_payment()")
        return functions

    def _calculate_overall_risk(self, file_changes: list[FileChange]) -> RiskLevel:
        """Calculate overall PR risk."""
        risks = [f.risk_level for f in file_changes]

        if any(r == RiskLevel.CRITICAL for r in risks):
            return RiskLevel.CRITICAL
        if any(r == RiskLevel.HIGH for r in risks):
            return RiskLevel.HIGH
        if any(r == RiskLevel.MEDIUM for r in risks):
            return RiskLevel.MEDIUM
        if any(r == RiskLevel.LOW for r in risks):
            return RiskLevel.LOW
        return RiskLevel.MINIMAL

    def _identify_affected_features(self, file_changes: list[FileChange]) -> list[str]:
        """Identify affected features."""
        features = set()
        for fc in file_changes:
            if "auth" in fc.path.lower():
                features.add("Authentication")
            if "payment" in fc.path.lower() or "checkout" in fc.path.lower():
                features.add("Checkout")
            if "profile" in fc.path.lower() or "account" in fc.path.lower():
                features.add("User Account")
            if "search" in fc.path.lower():
                features.add("Search")
        return sorted(features) or ["General"]

    def _generate_test_recommendations(
        self, file_changes: list[FileChange], affected_features: list[str]
    ) -> list[str]:
        """Generate test recommendations."""
        recommendations = []

        # High risk files need comprehensive testing
        high_risk_files = [f for f in file_changes if f.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        if high_risk_files:
            recommendations.append(f"High risk: Run full suite + new integration tests for {len(high_risk_files)} files")

        # Specific feature tests
        for feature in affected_features:
            recommendations.append(f"Add {feature} regression tests")

        # Breaking change tests
        recommendations.append("Test backward compatibility")
        recommendations.append("Test migration scenarios")

        return recommendations

    def _identify_coverage_gaps(self, file_changes: list[FileChange]) -> list[str]:
        """Identify coverage gaps."""
        gaps = []
        for fc in file_changes:
            if fc.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                gaps.append(f"No test coverage for {fc.path}")
            if fc.change_type == ChangeType.ADDED:
                gaps.append(f"New code in {fc.path} - add unit tests")
        return gaps

    def _detect_breaking_changes(self, diff: str, file_changes: list[FileChange]) -> list[str]:
        """Detect potential breaking changes."""
        breaking = []

        # Look for signature changes
        if "@deprecated" in diff:
            breaking.append("Deprecated API detected - ensure backward compatibility")

        # Look for database schema changes
        if "migration" in diff.lower() or "schema" in diff.lower():
            breaking.append("Database schema change - verify migration and rollback")

        # Look for API endpoint changes
        if "api" in diff.lower() or "endpoint" in diff.lower():
            breaking.append("API endpoint change - verify backward compatibility")

        # Look for authentication/permission changes
        if "auth" in diff.lower() or "permission" in diff.lower():
            breaking.append("Security/permission change - test access control")

        return breaking

    def _generate_impact_summary(
        self,
        file_changes: list[FileChange],
        overall_risk: RiskLevel,
        affected_features: list[str],
    ) -> str:
        """Generate an impact summary."""
        return (
            f"PR has {overall_risk.value} risk with {len(file_changes)} files changed, "
            f"affecting features: {', '.join(affected_features)}. "
            f"Total changes: {sum(f.additions + f.deletions for f in file_changes)} lines."
        )
