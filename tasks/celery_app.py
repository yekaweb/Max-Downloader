"""Celery app configuration.

This module provides a lightweight fallback when the `celery` package is
not available (e.g., in constrained CI environments). The fallback
exposes a minimal `celery_app` with a no-op `task` decorator so task
modules can be imported safely.
"""
try:
    from celery import Celery
    from config_simple import settings

    celery_app = Celery(
        "dlbot_tasks",
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/1",
    )

    celery_app.conf.task_time_limit = 3600
except Exception:
    # Fallback shim: provide a dummy app with a no-op `task` decorator.
    class _DummyCeleryApp:
        def task(self, *args, **kwargs):
            def _decorator(func):
                return func

            return _decorator


    celery_app = _DummyCeleryApp()

__all__ = ["celery_app"]
