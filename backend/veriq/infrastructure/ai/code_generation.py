from __future__ import annotations

import io
import json
import os
import time
import zipfile
from typing import Any

from veriq.api.v1.schemas.test_generation import TestGenerationResponse


def _sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name).lower()


def _render_playwright_package_json() -> dict:
    return {
        "name": "veriq-generated-tests",
        "version": "0.1.0",
        "private": True,
        "devDependencies": {"@playwright/test": "^1.40.0"},
        "scripts": {"test": "playwright test"},
    }


def _render_tsconfig() -> str:
    return """
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "CommonJS",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true
  }
}
"""


def _render_playwright_test(scenario: Any) -> str:
    title = scenario.name.replace('"', "\\\"")
    lines: list[str] = [
        "import { test, expect } from '@playwright/test';",
        "",
        f"test(\"{title}\", async ({'{'} page {'}'}) => {{",
    ]

    for step in scenario.steps:
        action = (step.action or "").lower()
        target = (step.target or "")
        value = step.value or ""

        # helper to choose selector-like string
        selector = target or ""
        if selector.startswith("/"):
            # looks like a path/url
            lines.append(f"  // navigate to {selector}")
            lines.append(f"  await page.goto(\"{selector}\");")
            continue

        if action in ("navigate", "goto") or selector.startswith("http"):
            lines.append(f"  // navigate to {selector}")
            lines.append(f"  await page.goto(\"{selector}\");")
        elif action.startswith("click") or action == "click":
            sel = selector
            desc = (step.description or "").strip()
            if not sel and desc:
                # prefer text-based clicking when no selector provided
                safe = desc.replace('"', '\\"')
                lines.append(f"  // click text '{desc}'")
                lines.append(f"  await page.getByText(\"{safe}\").click();")
            else:
                sel = sel or "button:has-text('')"
                lines.append(f"  // click {sel}")
                lines.append(f"  await page.click(\"{sel}\");")
        elif action.startswith("type") or action.startswith("fill") or action == "input":
            sel = selector
            desc = (step.description or "").strip()
            if not sel and desc:
                safe = desc.replace('"', '\\"')
                lines.append(f"  // fill by label/text '{desc}' with {value}")
                lines.append(f"  await page.getByLabel(\"{safe}\").fill(\"{value}\");")
            else:
                sel = sel or "input"
                lines.append(f"  // fill {sel} with {value}")
                lines.append(f"  await page.fill(\"{sel}\", \"{value}\");")
        elif action.startswith("select") or action == "choose":
            sel = selector or "select"
            lines.append(f"  // select {value} in {sel}")
            lines.append(f"  await page.selectOption(\"{sel}\", \"{value}\");")
        elif action.startswith("press") or action == "key":
            sel = selector or "body"
            lines.append(f"  // press {value} on {sel}")
            lines.append(f"  await page.press(\"{sel}\", \"{value}\");")
        elif action.startswith("wait") or action.startswith("sleep"):
            # allow numeric waits in seconds
            try:
                secs = float(value)
            except Exception:
                secs = 1
            lines.append(f"  // wait {secs}s")
            lines.append(f"  await page.waitForTimeout({int(secs * 1000)});")
        elif action.startswith("assert") or action.startswith("expect"):
            sel = selector or "body"
            if value:
                lines.append(f"  // assertion: expect {sel} to contain {value}")
                lines.append(f"  await expect(page.locator(\"{sel}\")).toContainText(\"{value}\");")
            else:
                lines.append(f"  // assertion: {step.description or 'assertion'}")
        elif action == "interact":
            # generic heuristic: if description contains "click" or "type", attempt mapping
            desc = (step.description or "").lower()
            if "click" in desc and selector:
                lines.append(f"  // interact->click {selector}")
                lines.append(f"  await page.click(\"{selector}\");")
            elif "type" in desc and selector:
                lines.append(f"  // interact->fill {selector} with {value}")
                lines.append(f"  await page.fill(\"{selector}\", \"{value}\");")
            else:
                lines.append(f"  // interact (generic) — consider replacing with explicit selectors/actions")
        else:
            lines.append(f"  // {action} {selector} {value}")

    lines.append("});")
    return "\n".join(lines)


def _render_pytest_test(scenario: Any) -> str:
    title = scenario.name.replace('"', '\\"')
    lines: list[str] = [
        "from playwright.sync_api import sync_playwright",
        "",
        f"def test_{_sanitize_filename(scenario.name)}():",
        "    with sync_playwright() as p:",
        "        browser = p.chromium.launch(headless=True)",
        "        page = browser.new_page()",
    ]

    for step in scenario.steps:
        action = (step.action or "").lower()
        target = step.target or ""
        value = step.value or ""
        if target.startswith("http"):
            lines.append(f"        # navigate to {target}")
            lines.append(f"        page.goto(\"{target}\")")
        elif action.startswith("click"):
            selector = target or ""
            desc = (step.description or "").strip()
            if not selector and desc:
                safe = desc.replace('"', '\\"')
                lines.append(f"        # click text '{desc}'")
                lines.append(f"        page.get_by_text(\"{safe}\").click()")
            else:
                selector = selector or "button:has-text('')"
                lines.append(f"        # click {selector}")
                lines.append(f"        page.click(\"{selector}\")")
        elif action.startswith("type") or action.startswith("fill"):
            selector = target or ""
            desc = (step.description or "").strip()
            if not selector and desc:
                safe = desc.replace('"', '\\"')
                lines.append(f"        # fill by label/text '{desc}' with {value}")
                lines.append(f"        page.get_by_label(\"{safe}\").fill(\"{value}\")")
            else:
                selector = selector or "input"
                lines.append(f"        # fill {selector} with {value}")
                lines.append(f"        page.fill(\"{selector}\", \"{value}\")")
        elif action.startswith("assert") or action.startswith("expect"):
            selector = target or "body"
            if value:
                lines.append(f"        # expect {selector} to contain {value}")
                lines.append(f"        assert {value!r} in page.text_content(\"{selector}\")")
            else:
                lines.append(f"        # {step.description or 'assertion'}")
        else:
            lines.append(f"        # {action} {target} {value}")

    lines.append("        browser.close()")
    return "\n".join(lines)


def generate_zip_from_plan(plan: TestGenerationResponse, target: str = "playwright-ts") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        if target == "playwright-ts":
            pkg = _render_playwright_package_json()
            z.writestr("package.json", json.dumps(pkg, indent=2))
            z.writestr("tsconfig.json", _render_tsconfig())
            z.writestr(
                "README.md",
                "Generated by Veriq — Playwright TypeScript tests. Run `npm install` then `npx playwright test`.",
            )
            for scenario in plan.scenarios:
                fname = _sanitize_filename(scenario.name) or "scenario"
                path = f"tests/{fname}.spec.ts"
                z.writestr(path, _render_playwright_test(scenario))
        elif target == "pytest-playwright":
            z.writestr(
                "README.md",
                "Generated by Veriq — Playwright Python tests. Install `playwright` and run `pytest`.",
            )
            z.writestr("requirements.txt", "playwright\n")
            # add a minimal conftest to help users configure pytest/playwright
            z.writestr(
                "conftest.py",
                """
import pytest

@pytest.fixture(scope='function')
def page_context():
    # placeholder fixture for users to adapt; requires playwright to be installed
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()
""",
            )
            for scenario in plan.scenarios:
                fname = _sanitize_filename(scenario.name) or "scenario"
                path = f"tests/test_{fname}.py"
                z.writestr(path, _render_pytest_test(scenario))
        else:
            # fallback to playwright-ts
            return generate_zip_from_plan(plan, target="playwright-ts")

    return buf.getvalue()


def persist_artifact(workspace_id: str, blob: bytes) -> str:
    base = os.path.join(os.getcwd(), "automation", "generated", workspace_id)
    os.makedirs(base, exist_ok=True)
    name = f"veriq_generated_{int(time.time())}.zip"
    path = os.path.join(base, name)
    with open(path, "wb") as fh:
        fh.write(blob)
    # return relative path from project root
    return path

