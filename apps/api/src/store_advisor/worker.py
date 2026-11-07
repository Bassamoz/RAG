"""Celery entry point from the same application package; no demo seed or business jobs."""

import json
from uuid import uuid4

from celery import Celery

from store_advisor.config import Settings, load_settings


def make_worker(settings: Settings) -> Celery:
    # https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html
    app = Celery(
        "store_advisor",
        broker=settings.redis_url.get_secret_value(),
        backend=settings.redis_url.get_secret_value(),
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_default_queue=f"store_advisor.{settings.app_env}",
        result_expires=60,
        broker_connection_retry_on_startup=True,
        broker_connection_timeout=2,
        task_soft_time_limit=15,
        task_time_limit=20,
        worker_hijack_root_logger=False,
        worker_log_color=False,
    )

    @app.task(name="store_advisor.worker_probe")
    def worker_probe() -> dict[str, str]:
        print(
            json.dumps(
                {
                    "event": "worker_probe",
                    "entryPoint": "worker_probe",
                    "request_id": str(uuid4()),
                    "status": "ok",
                }
            ),
            flush=True,
        )
        return {"status": "ok"}

    return app


def create_worker() -> Celery:
    """Celery CLI resolves this factory; configuration is validated before broker access."""
    return make_worker(load_settings())
