"""Download tasks - Celery async tasks

These tasks are implemented as safe stubs so the project can import
and run basic checks without external services. They log their
activity and return lightweight statuses.
"""
try:
    from loguru import logger
except Exception:
    import logging

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
from tasks.celery_app import celery_app


@celery_app.task
def download_media(download_id: int):
    """Async task for downloading media (safe stub).

    This function intentionally avoids heavy side-effects. It logs the
    request and returns a small status dict so callers can verify
    the task executed.
    """
    logger.info("download_media called with id={}", download_id)

    try:
        # Attempt to import downloader registry if available; do not fail
        # if modules are not present. This keeps the task safe to import.
        from modules import get_downloader  # type: ignore

        # For now, we don't execute actual downloads inside CI runs.
        logger.debug("Downloader registry import succeeded (stub path)")
        return {"status": "skipped", "download_id": download_id}
    except Exception:
        logger.debug("Downloader registry not available; running stub")
        return {"status": "skipped", "download_id": download_id}


@celery_app.task
def cleanup_old_files():
    """Cleanup old cached files (safe stub)."""
    logger.info("cleanup_old_files invoked")
    # Real cleanup should remove old files and update DB; keep stub
    return True


__all__ = ["download_media", "cleanup_old_files"]
