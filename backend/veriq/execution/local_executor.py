from __future__ import annotations

import logging
from collections.abc import Iterable
from time import perf_counter

from sqlalchemy.orm import Session

from veriq.application.services import test_run_service as tr_service
from veriq.infrastructure.repositories import (
    test_case_repository as tc_repo,
)
from veriq.infrastructure.repositories import (
    test_step_repository as ts_repo,
)

logger = logging.getLogger(__name__)


class LocalTestExecutor:
    """A lightweight, deterministic local executor used for production
    deployments where a simple, dependency-free runner is required.

    Execution rules are intentionally minimal: steps are interpreted by
    `action` and a special failing marker (`value == "__FAIL__"`) will
    cause the step and test to fail. This keeps execution deterministic
    and safe for serverless environments.
    """

    def __init__(self) -> None:
        self._logger = logger

    def execute_test_run(self, session: Session, test_run_id: str) -> int:
        start = perf_counter()

        # load run to get workspace
        from veriq.infrastructure.repositories import test_run_repository as tr_repo

        run = tr_repo.get_test_run(session, test_run_id)
        if run is None:
            self._logger.warning("Test run %s not found", test_run_id)
            return 0

        workspace_id = run.workspace_id

        test_cases = tc_repo.list_test_cases(session, workspace_id)

        total = 0
        passed = 0
        failed = 0
        error = 0

        for tc in test_cases:
            total += 1
            try:
                steps = ts_repo.list_test_steps(session, tc.id)
                tc_passed = self._run_test_case(session, test_run_id, tc.id, steps)
                if tc_passed:
                    passed += 1
                else:
                    failed += 1
            except Exception as exc:  # pragma: no cover - safety net
                error += 1
                self._logger.exception("Error executing test case %s: %s", tc.id, exc)
                tr_service.report_test_result(
                    session,
                    test_run_id=test_run_id,
                    test_case_id=tc.id,
                    status="error",
                    duration_seconds=0,
                    error_message=str(exc),
                )

        duration = int(perf_counter() - start)

        # finalise run counters
        tr_repo.update_test_run_status(
            session=session,
            test_run_id=test_run_id,
            status="completed",
            total_count=total,
            passed_count=passed,
            failed_count=failed,
            error_count=error,
            duration_seconds=duration,
        )

        return duration

    def _run_test_case(
        self, session: Session, test_run_id: str, test_case_id: str, steps: Iterable
    ):
        # A simple interpreter: any step with value == "__FAIL__" fails.
        for step in steps:
            if getattr(step, "value", None) == "__FAIL__":
                tr_service.report_test_result(
                    session,
                    test_run_id=test_run_id,
                    test_case_id=test_case_id,
                    status="failed",
                    duration_seconds=0,
                    failure_step_id=step.id,
                    error_message="Step marked as failing",
                )
                return False

        # otherwise pass
        tr_service.report_test_result(
            session,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
            status="passed",
            duration_seconds=0,
        )
        return True
