from __future__ import annotations

import logging
import os
import tempfile
from collections.abc import Iterable
from time import perf_counter

from sqlalchemy.orm import Session

from veriq.application.services import test_run_service as tr_service
from veriq.infrastructure.config.settings import get_settings
from veriq.infrastructure.repositories import (
    test_case_repository as tc_repo,
)
from veriq.infrastructure.repositories import (
    test_step_repository as ts_repo,
)

logger = logging.getLogger(__name__)


class PlaywrightExecutor:
    """Playwright-based executor with hardened behaviors:
    - configurable browser
    - per-action retries and timeouts
    - screenshot and page source capture on failures
    - optional artifact upload to MinIO/S3 using configured settings
    """

    def __init__(self, browser: str | None = None, timeout_ms: int = 30000, retries: int = 2) -> None:
        settings = get_settings()
        self._browser = browser or settings.playwright_browser
        self._timeout_ms = timeout_ms
        self._retries = retries
        self._settings = settings

    def _upload_artifact(self, path: str, dest_path: str) -> str | None:
        # Try MinIO first (minio package), then fall back to aws s3 if available
        try:
            from minio import Minio
        except Exception:
            Minio = None  # type: ignore

        # Use settings from get_settings()
        endpoint = getattr(self._settings, "minio_endpoint", None)
        access = getattr(self._settings, "minio_access_key", None)
        secret = getattr(self._settings, "minio_secret_key", None)
        bucket = getattr(self._settings, "minio_bucket", None)

        if Minio and endpoint and access and secret and bucket:
            try:
                # Strip scheme
                ep = endpoint.replace("http://", "").replace("https://", "")
                client = Minio(ep, access_key=access, secret_key=secret, secure=endpoint.startswith("https"))
                object_name = dest_path
                client.fput_object(bucket, object_name, path)
                url = f"{endpoint.rstrip('/')}/{bucket}/{object_name}"
                return url
            except Exception:
                logger.exception("Failed to upload artifact to MinIO")

        # Try aws s3 via aws cli if configured
        aws_bucket = os.environ.get("AWS_S3_BUCKET") or os.environ.get("VERIQ_AWS_S3_BUCKET")
        if aws_bucket:
            try:
                import subprocess

                key = dest_path
                subprocess.check_call(["aws", "s3", "cp", path, f"s3://{aws_bucket}/{key}"])
                region = os.environ.get("AWS_DEFAULT_REGION", "")
                url = f"https://{aws_bucket}.s3.{region}.amazonaws.com/{key}"
                return url
            except Exception:
                logger.exception("Failed to upload artifact to AWS S3")

        return None

    def execute_test_run(self, session: Session, test_run_id: str) -> int:
        try:
            from playwright.sync_api import sync_playwright
        except Exception:  # pragma: no cover - optional dependency
            logger.exception("Playwright not available")
            raise

        start = perf_counter()

        run = None
        from veriq.infrastructure.repositories import test_run_repository as tr_repo
        run = tr_repo.get_test_run(session, test_run_id)
        if run is None:
            logger.warning("Test run %s not found", test_run_id)
            return 0

        workspace_id = run.workspace_id
        test_cases = tc_repo.list_test_cases(session, workspace_id)

        total = 0
        passed = 0
        failed = 0
        error = 0

        with sync_playwright() as p:
            browser = getattr(p, self._browser).launch(headless=True)
            context = browser.new_context()

            for tc in test_cases:
                total += 1
                page = context.new_page()
                try:
                    steps = ts_repo.list_test_steps(session, tc.id)
                    tc_passed = self._run_test_case(page, session, test_run_id, tc.id, steps)
                    if tc_passed:
                        passed += 1
                    else:
                        failed += 1
                except Exception as exc:  # pragma: no cover - safety net
                    error += 1
                    logger.exception("Error executing test case %s: %s", tc.id, exc)
                    tr_service.report_test_result(
                        session,
                        test_run_id=test_run_id,
                        test_case_id=tc.id,
                        status="error",
                        duration_seconds=0,
                        error_message=str(exc),
                    )
                finally:
                    try:
                        page.close()
                    except Exception:
                        pass

            browser.close()

        duration = int(perf_counter() - start)

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

    def _run_test_case(self, page, session: Session, test_run_id: str, test_case_id: str, steps: Iterable):
        from time import sleep

        start = perf_counter()
        for step in steps:
            action = getattr(step, "action", "").lower()
            target = getattr(step, "target", None)
            value = getattr(step, "value", None)

            success = False
            last_error = None
            for attempt in range(max(1, self._retries)):
                try:
                    if action == "navigate" and target:
                        page.goto(target, timeout=self._timeout_ms)
                    elif action == "click" and target:
                        page.click(target, timeout=self._timeout_ms)
                    elif action == "input" and target and value is not None:
                        page.fill(target, value, timeout=self._timeout_ms)
                    elif action == "assert" and value is not None:
                        content = page.content()
                        if value not in content:
                            raise AssertionError(f"Assertion '{value}' not found")
                    else:
                        # Unknown action - log and continue
                        logger.warning("Unknown action '%s' in step %s", action, getattr(step, "id", "?"))

                    success = True
                    break
                except Exception as exc:
                    last_error = exc
                    logger.debug("Attempt %d/%d failed for action %s: %s", attempt + 1, self._retries, action, exc)
                    sleep(0.5)

            if not success:
                # Capture artifacts
                try:
                    tmp_dir = tempfile.mkdtemp(prefix="veriq-art-")
                    screenshot_path = os.path.join(tmp_dir, f"{test_case_id}.png")
                    html_path = os.path.join(tmp_dir, f"{test_case_id}.html")
                    try:
                        page.screenshot(path=screenshot_path, full_page=True)
                    except Exception:
                        logger.exception("Failed to capture screenshot for test case %s", test_case_id)
                    try:
                        with open(html_path, "w", encoding="utf-8") as fh:
                            fh.write(page.content())
                    except Exception:
                        logger.exception("Failed to save page content for test case %s", test_case_id)

                    # Upload artifacts
                    remote_screenshot = self._upload_artifact(screenshot_path, f"test_runs/{test_run_id}/{test_case_id}/screenshot.png")
                    remote_html = self._upload_artifact(html_path, f"test_runs/{test_run_id}/{test_case_id}/page.html")
                    extra_msg = ""
                    if remote_html:
                        extra_msg = f" | page_html={remote_html}"
                except Exception:
                    logger.exception("Failed to capture/upload artifacts for test case %s", test_case_id)
                    remote_screenshot = None
                    extra_msg = ""

                tr_service.report_test_result(
                    session,
                    test_run_id=test_run_id,
                    test_case_id=test_case_id,
                    status="failed",
                    duration_seconds=int(perf_counter() - start),
                    error_message=f"{last_error}{extra_msg}",
                    failure_screenshot=remote_screenshot,
                )
                return False

        tr_service.report_test_result(
            session,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
            status="passed",
            duration_seconds=int(perf_counter() - start),
        )
        return True
