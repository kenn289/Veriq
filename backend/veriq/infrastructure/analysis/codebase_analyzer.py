"""Codebase Understanding Engine — analyze existing tests and learn patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TestPattern:
    """A detected test pattern."""
    name: str
    description: str
    count: int
    examples: list[str]
    frequency: float  # 0-1


@dataclass(frozen=True)
class CodebaseAnalysis:
    """Analysis of a codebase."""
    language: str
    framework: str
    total_tests: int
    test_patterns: list[TestPattern]
    locator_strategies: dict
    assertion_patterns: dict
    setup_teardown_patterns: list[str]
    common_helpers: list[str]
    recommendations: list[str]


class CodebaseAnalyzer:
    """Analyzes existing test codebases to learn patterns."""

    def analyze_codebase(self, code_files: list[dict]) -> CodebaseAnalysis:
        """Analyze test codebase to extract patterns.
        
        Args:
            code_files: List of code file dicts with 'name' and 'content'
            
        Returns:
            CodebaseAnalysis: Analysis results
        """
        language = self._detect_language(code_files)
        framework = self._detect_framework(code_files, language)

        all_content = "\n".join(f["content"] for f in code_files)

        test_count = self._count_tests(all_content)
        patterns = self._detect_patterns(all_content, language)
        locator_strategies = self._analyze_locators(all_content, framework)
        assertion_patterns = self._analyze_assertions(all_content, language)
        setup_teardown = self._analyze_setup_teardown(all_content, language)
        helpers = self._extract_helpers(code_files, language)
        recommendations = self._generate_recommendations(
            test_count, patterns, locator_strategies, framework
        )

        return CodebaseAnalysis(
            language=language,
            framework=framework,
            total_tests=test_count,
            test_patterns=patterns,
            locator_strategies=locator_strategies,
            assertion_patterns=assertion_patterns,
            setup_teardown_patterns=setup_teardown,
            common_helpers=helpers,
            recommendations=recommendations,
        )

    def _detect_language(self, code_files: list[dict]) -> str:
        """Detect programming language from file extensions."""
        for f in code_files:
            name = f.get("name", "").lower()
            if name.endswith(".py"):
                return "python"
            if name.endswith(".ts"):
                return "typescript"
            if name.endswith(".js"):
                return "javascript"
            if name.endswith(".java"):
                return "java"
            if name.endswith(".cs"):
                return "csharp"
        return "unknown"

    def _detect_framework(self, code_files: list[dict], language: str) -> str:
        """Detect test framework from imports and usage."""
        all_content = "\n".join(f["content"] for f in code_files)

        if language == "python":
            if "import pytest" in all_content:
                return "pytest"
            if "import unittest" in all_content:
                return "unittest"
            if "from playwright" in all_content:
                return "pytest-playwright"

        if language in ["typescript", "javascript"]:
            if "@playwright/test" in all_content or "describe(" in all_content:
                return "playwright"
            if "jest" in all_content:
                return "jest"
            if "mocha" in all_content:
                return "mocha"

        if language == "java":
            if "import org.junit" in all_content:
                return "junit"
            if "testng" in all_content:
                return "testng"
            if "selenium" in all_content:
                return "selenium"

        return "unknown"

    def _count_tests(self, content: str) -> int:
        """Count number of tests."""
        # Look for test function/method declarations
        patterns = [
            r"^\s*(def test_|async def test_)",  # pytest
            r"^\s*(it\(|test\(|describe\()",  # JavaScript
            r"^\s*(public void test)",  # Java
        ]

        count = 0
        for line in content.split("\n"):
            for pattern in patterns:
                if re.match(pattern, line):
                    count += 1
        return count

    def _detect_patterns(self, content: str, language: str) -> list[TestPattern]:
        """Detect common test patterns."""
        patterns = []

        # AAA pattern (Arrange-Act-Assert)
        aaa_matches = len(re.findall(r"(setup|arrange).*(test|act).*(assert|verify)", content, re.IGNORECASE))
        if aaa_matches > 0:
            patterns.append(
                TestPattern(
                    name="AAA Pattern",
                    description="Arrange-Act-Assert pattern",
                    count=aaa_matches,
                    examples=["# Arrange\n# Act\n# Assert"],
                    frequency=min(aaa_matches / max(10, self._count_tests(content)), 1.0),
                )
            )

        # Page Object Model
        page_obj_matches = len(re.findall(r"class.*Page|class.*PO", content))
        if page_obj_matches > 0:
            patterns.append(
                TestPattern(
                    name="Page Object Model",
                    description="Page Object Model pattern",
                    count=page_obj_matches,
                    examples=["class LoginPage:", "class Dashboard:"],
                    frequency=min(page_obj_matches / max(10, self._count_tests(content)), 1.0),
                )
            )

        # Data-driven tests
        data_driven_matches = len(
            re.findall(r"@pytest\.mark\.parametrize|\.parametrize\(|@DataProvider", content)
        )
        if data_driven_matches > 0:
            patterns.append(
                TestPattern(
                    name="Data-Driven Tests",
                    description="Parameterized/data-driven tests",
                    count=data_driven_matches,
                    examples=["@pytest.mark.parametrize"],
                    frequency=min(data_driven_matches / max(10, self._count_tests(content)), 1.0),
                )
            )

        # Fixture/setup-teardown
        fixture_matches = len(re.findall(r"@pytest\.fixture|setUp|tearDown|@Before|@After", content))
        if fixture_matches > 0:
            patterns.append(
                TestPattern(
                    name="Fixtures/Setup-Teardown",
                    description="Test fixtures and lifecycle management",
                    count=fixture_matches,
                    examples=["@pytest.fixture", "def setUp(self):"],
                    frequency=min(fixture_matches / max(10, self._count_tests(content)), 1.0),
                )
            )

        return patterns

    def _analyze_locators(self, content: str, framework: str) -> dict:
        """Analyze locator strategies used."""
        strategies = {
            "css_selectors": len(re.findall(r"get_by_css|querySelector|\.css\(", content)),
            "xpath": len(re.findall(r"xpath=|get_by_xpath|getByXPath|//", content)),
            "role": len(re.findall(r"get_by_role|getByRole", content)),
            "label": len(re.findall(r"get_by_label|getByLabel", content)),
            "test_id": len(re.findall(r"get_by_test_id|data-testid", content)),
            "placeholder": len(re.findall(r"get_by_placeholder|placeholder", content)),
        }
        return {k: v for k, v in strategies.items() if v > 0}

    def _analyze_assertions(self, content: str, language: str) -> dict:
        """Analyze assertion patterns used."""
        assertion_patterns = {
            "visible": len(re.findall(r"to_be_visible|is_visible|visible|isDisplayed", content, re.IGNORECASE)),
            "enabled": len(re.findall(r"to_be_enabled|is_enabled|enabled|isEnabled", content, re.IGNORECASE)),
            "text": len(re.findall(r"to_contain_text|has_text|text_content|getText", content, re.IGNORECASE)),
            "value": len(re.findall(r"to_have_value|value|getValue", content, re.IGNORECASE)),
            "class": len(re.findall(r"to_have_class|classList|class", content, re.IGNORECASE)),
            "url": len(re.findall(r"to_have_url|current_url|getURL", content, re.IGNORECASE)),
        }
        return {k: v for k, v in assertion_patterns.items() if v > 0}

    def _analyze_setup_teardown(self, content: str, language: str) -> list[str]:
        """Analyze setup and teardown patterns."""
        patterns = []

        if "browser" in content.lower():
            patterns.append("Browser setup/teardown")
        if "database" in content.lower():
            patterns.append("Database reset")
        if "login" in content.lower():
            patterns.append("User login before test")
        if "seed" in content.lower():
            patterns.append("Data seeding")

        return patterns

    def _extract_helpers(self, code_files: list[dict], language: str) -> list[str]:
        """Extract common helper functions/methods."""
        helpers = []

        for f in code_files:
            content = f.get("content", "")
            if "helper" in f.get("name", "").lower() or "util" in f.get("name", "").lower():
                # Find function/method definitions
                if language == "python":
                    funcs = re.findall(r"^def (\w+)\(", content, re.MULTILINE)
                    helpers.extend(funcs)
                elif language in ["typescript", "javascript"]:
                    funcs = re.findall(r"(?:export\s+)?(?:async\s+)?function (\w+)\(", content)
                    helpers.extend(funcs)

        return list(set(helpers))[:5]  # Return top 5 unique helpers

    def _generate_recommendations(
        self,
        test_count: int,
        patterns: list[TestPattern],
        locator_strategies: dict,
        framework: str,
    ) -> list[str]:
        """Generate recommendations for improving codebase."""
        recommendations = []

        # Coverage recommendations
        if test_count < 10:
            recommendations.append("❌ Low test count - consider expanding test coverage")
        elif test_count < 50:
            recommendations.append("⚠️  Moderate test count - expand critical path coverage")
        else:
            recommendations.append("✅ Good test count")

        # Pattern recommendations
        if not any(p.name == "Page Object Model" for p in patterns):
            recommendations.append("💡 Consider using Page Object Model for maintainability")
        else:
            recommendations.append("✅ Using Page Object Model - good practice")

        if not any(p.name == "AAA Pattern" for p in patterns):
            recommendations.append("💡 Use Arrange-Act-Assert pattern for clarity")

        # Locator recommendations
        if "xpath" in locator_strategies and locator_strategies.get("xpath", 0) > 5:
            recommendations.append("⚠️  Many XPath selectors - consider CSS or role-based locators")
        if not any(s in locator_strategies for s in ["role", "test_id"]):
            recommendations.append("💡 Use accessibility attributes (role, test-id) for resilience")

        return recommendations
