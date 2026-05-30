from __future__ import annotations

from celery import Celery

from veriq.infrastructure.config.settings import get_settings


def create_celery_app() -> Celery:
    """Description: Create the Celery application instance.
    Parameters:
        None
    Returns:
        Celery: Configured Celery app.
    Usage Example:
        celery_app = create_celery_app()
    """

    settings = get_settings()
    app = Celery(
        "veriq",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    app.conf.update(task_track_started=True)
    return app


celery_app = create_celery_app()
