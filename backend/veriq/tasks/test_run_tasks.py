from __future__ import annotations

from veriq.celery_app import celery_app
from veriq.execution.local_executor import LocalTestExecutor
from veriq.infrastructure.config.settings import get_settings
from veriq.infrastructure.db.session import get_session_factory

settings = get_settings()

try:
    # optional Playwright executor
    from veriq.execution.playwright_executor import PlaywrightExecutor
except Exception:
    PlaywrightExecutor = None


@celery_app.task(name="veriq.tasks.execute_test_run")
def execute_test_run_task(test_run_id: str) -> int:
    """Celery task wrapper to execute a test run using the LocalTestExecutor.

    Returns the total duration in seconds.
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        backend = settings.execution_backend or "local"
        if backend == "playwright" and PlaywrightExecutor is not None:
            executor = PlaywrightExecutor(browser=settings.playwright_browser)
        else:
            executor = LocalTestExecutor()

        duration = executor.execute_test_run(session, test_run_id)
        session.commit()
        return duration
    finally:
        session.close()
