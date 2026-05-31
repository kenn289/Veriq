from __future__ import annotations

from celery import Celery

from veriq.infrastructure.config.settings import get_settings


settings = get_settings()


def make_celery() -> Celery:
    celery = Celery(
        "veriq",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    celery.conf.task_default_queue = "default"
    celery.conf.task_acks_late = True
    return celery


celery_app = make_celery()
