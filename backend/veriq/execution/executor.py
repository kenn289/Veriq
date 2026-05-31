from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session


class TestExecutor(Protocol):
    """Protocol for test executors.

    Implementations should run a test run and report results via the
    existing service APIs (report_test_result / complete_test_run).
    """

    def execute_test_run(self, session: Session, test_run_id: str) -> int:
        """Execute a test run synchronously.

        Returns total duration in seconds.
        """
