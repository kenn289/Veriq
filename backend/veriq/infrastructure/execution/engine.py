"""Execution Engine — manages test execution across different platforms."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile


class ExecutionStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass(frozen=True)
class ExecutionResult:
    """Result of a test execution."""
    test_id: str
    status: ExecutionStatus
    duration_seconds: float
    passed_count: int
    failed_count: int
    error_count: int
    stdout: str
    stderr: str
    artifacts: dict  # Screenshots, videos, logs, etc


class ExecutionEngine:
    """Manages test execution across platforms."""

    def __init__(self):
        self.execution_results = {}

    def execute_playwright_ts(
        self,
        test_code: str,
        test_name: str = "generated_tests",
    ) -> ExecutionResult:
        """Execute Playwright TypeScript tests.
        
        Args:
            test_code: TypeScript test code
            test_name: Name for the test run
            
        Returns:
            ExecutionResult: Test execution results
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write test code to file
            test_file = tmppath / f"{test_name}.spec.ts"
            test_file.write_text(test_code)
            
            # Write playwright config
            config_file = tmppath / "playwright.config.ts"
            config_file.write_text(self._get_playwright_config())
            
            # Execute tests
            try:
                result = subprocess.run(
                    [
                        "npx",
                        "playwright",
                        "test",
                        str(test_file),
                        "--reporter=json",
                    ],
                    cwd=str(tmppath),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                
                # Parse results
                return self._parse_playwright_results(
                    test_id=test_name,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.returncode,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    test_id=test_name,
                    status=ExecutionStatus.ERROR,
                    duration_seconds=60.0,
                    passed_count=0,
                    failed_count=0,
                    error_count=1,
                    stdout="",
                    stderr="Test execution timed out after 60 seconds",
                    artifacts={},
                )
            except Exception as e:
                return ExecutionResult(
                    test_id=test_name,
                    status=ExecutionStatus.ERROR,
                    duration_seconds=0.0,
                    passed_count=0,
                    failed_count=0,
                    error_count=1,
                    stdout="",
                    stderr=str(e),
                    artifacts={},
                )

    def execute_pytest_playwright(
        self,
        test_code: str,
        test_name: str = "generated_tests",
    ) -> ExecutionResult:
        """Execute pytest-playwright tests.
        
        Args:
            test_code: Python test code
            test_name: Name for the test run
            
        Returns:
            ExecutionResult: Test execution results
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write test code to file
            test_file = tmppath / f"test_{test_name}.py"
            test_file.write_text(test_code)
            
            # Write conftest if needed
            conftest_file = tmppath / "conftest.py"
            conftest_file.write_text(self._get_pytest_conftest())
            
            # Execute tests
            try:
                result = subprocess.run(
                    [
                        "pytest",
                        str(test_file),
                        "-v",
                        "--tb=short",
                        "--json-report",
                        f"--json-report-file={tmppath}/report.json",
                    ],
                    cwd=str(tmppath),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                
                # Parse results
                return self._parse_pytest_results(
                    test_id=test_name,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.returncode,
                    report_file=tmppath / "report.json",
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    test_id=test_name,
                    status=ExecutionStatus.ERROR,
                    duration_seconds=60.0,
                    passed_count=0,
                    failed_count=0,
                    error_count=1,
                    stdout="",
                    stderr="Test execution timed out after 60 seconds",
                    artifacts={},
                )
            except Exception as e:
                return ExecutionResult(
                    test_id=test_name,
                    status=ExecutionStatus.ERROR,
                    duration_seconds=0.0,
                    passed_count=0,
                    failed_count=0,
                    error_count=1,
                    stdout="",
                    stderr=str(e),
                    artifacts={},
                )

    def _parse_playwright_results(
        self,
        test_id: str,
        stdout: str,
        stderr: str,
        return_code: int,
    ) -> ExecutionResult:
        """Parse Playwright test results."""
        # Simple parsing based on return code
        status = ExecutionStatus.PASSED if return_code == 0 else ExecutionStatus.FAILED
        
        passed_count = 1 if return_code == 0 else 0
        failed_count = 1 if return_code != 0 else 0
        
        return ExecutionResult(
            test_id=test_id,
            status=status,
            duration_seconds=0.0,
            passed_count=passed_count,
            failed_count=failed_count,
            error_count=0,
            stdout=stdout,
            stderr=stderr,
            artifacts={},
        )

    def _parse_pytest_results(
        self,
        test_id: str,
        stdout: str,
        stderr: str,
        return_code: int,
        report_file: Path,
    ) -> ExecutionResult:
        """Parse pytest test results."""
        status = ExecutionStatus.PASSED if return_code == 0 else ExecutionStatus.FAILED
        
        # Try to parse report if it exists
        passed_count = 0
        failed_count = 0
        
        if report_file.exists():
            try:
                with open(report_file) as f:
                    report = json.load(f)
                    summary = report.get("summary", {})
                    passed_count = summary.get("passed", 0)
                    failed_count = summary.get("failed", 0)
            except Exception:
                pass
        
        return ExecutionResult(
            test_id=test_id,
            status=status,
            duration_seconds=0.0,
            passed_count=passed_count,
            failed_count=failed_count,
            error_count=0,
            stdout=stdout,
            stderr=stderr,
            artifacts={},
        )

    def _get_playwright_config(self) -> str:
        """Get minimal Playwright config."""
        return """export default {
  testDir: '.',
  timeout: 30000,
  retries: 0,
};
"""

    def _get_pytest_conftest(self) -> str:
        """Get minimal pytest conftest."""
        return """import pytest


@pytest.fixture
def browser():
    # Placeholder for browser fixture
    yield None
"""

    def store_result(self, execution_id: str, result: ExecutionResult) -> None:
        """Store execution result."""
        self.execution_results[execution_id] = result

    def get_result(self, execution_id: str) -> ExecutionResult | None:
        """Retrieve execution result."""
        return self.execution_results.get(execution_id)
