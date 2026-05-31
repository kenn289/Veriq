from __future__ import annotations

from veriq.celery_app import celery_app

from sqlalchemy.orm import scoped_session

from veriq.infrastructure.db.session import get_session_factory
from veriq.execution.local_executor import LocalTestExecutor
from veriq.infrastructure.config.settings import get_settings

settings = get_settings()

_EXECUTOR_BACKENDS = {
    "local": LocalTestExecutor,
}

try:
    # optional Playwright executor
    from veriq.execution.playwright_executor import PlaywrightExecutor

    _EXECUTOR_BACKENDS["playwright"] = PlaywrightExecutor
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
        executor_cls = _EXECUTOR_BACKENDS.get(backend, LocalTestExecutor)
        # PlaywrightExecutor constructor accepts browser param
        if backend == "playwright":
            executor = executor_cls(browser=settings.playwright_browser)
        else:
            executor = executor_cls()

        duration = executor.execute_test_run(session, test_run_id)
        session.commit()
        return duration
    finally:
        session.close()
