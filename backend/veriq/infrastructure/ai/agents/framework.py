"""Framework Agent — generates runnable test code from designs."""

from __future__ import annotations

from typing import Literal


class FrameworkAgent:
    """Generates runnable test framework code."""

    def generate_framework(
        self,
        test_cases: list[dict],
        target: str = "playwright-ts",
    ) -> dict:
        """Generate framework code from test designs.
        
        Args:
            test_cases: Test case designs from DesignerAgent
            target: Code generation target (playwright-ts, pytest-playwright, etc)
            
        Returns:
            Generated code artifacts
        """
        if target == "playwright-ts":
            return self._generate_playwright_ts(test_cases)
        elif target == "pytest-playwright":
            return self._generate_pytest_playwright(test_cases)
        else:
            raise ValueError(f"Unknown target: {target}")

    def _generate_playwright_ts(self, test_cases: list[dict]) -> dict:
        """Generate Playwright TypeScript test code."""
        spec_code = self._build_playwright_spec(test_cases)
        return {
            "target": "playwright-ts",
            "files": {
                "tests/generated.spec.ts": spec_code,
                "playwright.config.ts": self._playwright_config(),
            },
            "package_json_deps": {
                "@playwright/test": "^1.40.0",
                "typescript": "^5.3.0",
                "ts-node": "^10.9.0",
            },
        }

    def _generate_pytest_playwright(self, test_cases: list[dict]) -> dict:
        """Generate pytest-playwright test code."""
        test_code = self._build_pytest_code(test_cases)
        return {
            "target": "pytest-playwright",
            "files": {
                "tests/test_generated.py": test_code,
                "conftest.py": self._pytest_conftest(),
            },
            "requirements_txt_deps": [
                "pytest>=7.4.0",
                "pytest-playwright>=0.4.0",
                "playwright>=1.40.0",
            ],
        }

    def _build_playwright_spec(self, test_cases: list[dict]) -> str:
        """Build Playwright test spec."""
        imports = """import { test, expect } from '@playwright/test';

test.describe('Generated Test Suite', () => {
"""
        
        test_blocks = []
        for i, tc in enumerate(test_cases, 1):
            name = tc.get("name", f"Test {i}")
            description = tc.get("description", "")
            steps = tc.get("steps", [])
            
            test_block = f"""  test('{name}', async ({{ page }}) => {{
    // {description}
"""
            for step in steps:
                action = step.get("action", "")
                target = step.get("target", "")
                description = step.get("description", "")
                
                if action == "navigate":
                    test_block += f"""    await page.goto('{target}'); // {description}
"""
                elif action == "perform_primary_action":
                    test_block += f"""    // TODO: Implement primary action
    // {description}
"""
                elif action == "verify_success":
                    test_block += f"""    // TODO: Add assertions
    // {description}
"""
                else:
                    test_block += f"""    // {description}
"""
            
            test_block += """  });
"""
            test_blocks.append(test_block)
        
        closing = "});"
        return imports + "".join(test_blocks) + closing

    def _build_pytest_code(self, test_cases: list[dict]) -> str:
        """Build pytest test code."""
        imports = """import pytest
from playwright.async_api import Page, expect


@pytest.mark.asyncio
class TestGeneratedSuite:
"""
        
        test_methods = []
        for i, tc in enumerate(test_cases, 1):
            name = tc.get("name", f"test_{i}").lower().replace(" ", "_")
            description = tc.get("description", "")
            steps = tc.get("steps", [])
            
            test_method = f"""    async def test_{name}(self, page: Page):
        '''
        {description}
        '''
"""
            for step in steps:
                action = step.get("action", "")
                target = step.get("target", "")
                desc = step.get("description", "")
                
                if action == "navigate":
                    test_method += f"""        await page.goto('{target}')  # {desc}
"""
                elif action == "perform_primary_action":
                    test_method += f"""        # TODO: Implement primary action
        # {desc}
"""
                elif action == "verify_success":
                    test_method += f"""        # TODO: Add assertions
        # {desc}
"""
                else:
                    test_method += f"""        # {desc}
"""
            
            test_method += "\n"
            test_methods.append(test_method)
        
        return imports + "".join(test_methods)

    def _playwright_config(self) -> str:
        """Playwright configuration."""
        return """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: 0,
  workers: 1,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chromium'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
"""

    def _pytest_conftest(self) -> str:
        """pytest conftest for async support."""
        return """import pytest
import asyncio
from playwright.async_api import async_playwright


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()
"""
