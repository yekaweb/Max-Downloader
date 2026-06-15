"""Download tasks - Celery async tasks for background media downloading"""
from loguru import logger
from tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def download_and_send(self, user_telegram_id: int, chat_id: int, url: str, format_opts: dict):
    """
    Background Celery task: download media and send to user.

    Args:
        user_telegram_id: Telegram user ID (for DB lookup)
        chat_id:          Telegram chat ID to send result
        url:              Media URL to download
        format_opts:      Dict with format/quality options
    """
    import asyncio
    import os
    from pathlib import Path

    logger.info(f"[Celery] Starting download task for user {user_telegram_id} | URL: {url}")

    try:
        import yt_dlp
    except ImportError:
        logger.error("[Celery] yt-dlp not installed")
        return {"status": "failed", "error": "yt-dlp not installed"}

    output_dir = Path("temp_downloads")
    output_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
    }

    fmt_type = format_opts.get("format_type", "video")
    if fmt_type == "video":
        height = format_opts.get("height", 720)
        ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
    else:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": format_opts.get("audio_codec", "mp3"),
            "preferredquality": format_opts.get("bitrate", "128"),
        }]

    downloaded_path = None

    def _dl_hook(d):
        nonlocal downloaded_path
        if d["status"] == "finished":
            downloaded_path = d["filename"]

    ydl_opts["progress_hooks"] = [_dl_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        logger.error(f"[Celery] yt-dlp download failed: {e}")
        raise self.retry(exc=e)

    if not downloaded_path or not os.path.exists(downloaded_path):
        logger.error(f"[Celery] File not found after download: {downloaded_path}")
        return {"status": "failed", "error": "File not found after download"}

    # Send the file to the user via Telegram bot
    async def _send():
        from bot.loader import bot
        from aiogram.types import FSInputFile
        if not bot:
            logger.error("[Celery] Bot instance not available")
            return

        file = FSInputFile(downloaded_path)
        if downloaded_path.endswith((".mp4", ".mkv", ".webm", ".avi")):
            await bot.send_video(chat_id=chat_id, video=file, caption="✅ دانلود تکمیل شد.")
        elif downloaded_path.endswith((".mp3", ".aac", ".m4a", ".opus")):
            await bot.send_audio(chat_id=chat_id, audio=file, caption="✅ دانلود تکمیل شد.")
        else:
            await bot.send_document(chat_id=chat_id, document=file, caption="✅ دانلود تکمیل شد.")

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_send())
        loop.close()
    except Exception as e:
        logger.error(f"[Celery] Failed to send file to user: {e}")

    # Cleanup temp file
    try:
        os.remove(downloaded_path)
    except Exception:
        pass

    logger.info(f"[Celery] Task complete for user {user_telegram_id}")
    return {"status": "completed", "url": url}


@celery_app.task
def cleanup_old_files():
    """Cleanup temp downloads older than 1 hour."""
    import os
    import time
    from pathlib import Path

    output_dir = Path("temp_downloads")
    if not output_dir.exists():
        return {"cleaned": 0}

    cleaned = 0
    now = time.time()
    one_hour = 3600

    for f in output_dir.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > one_hour:
            try:
                f.unlink()
                cleaned += 1
            except Exception as e:
                logger.warning(f"[Celery] Could not delete {f}: {e}")

    logger.info(f"[Celery] Cleanup complete. Removed {cleaned} files.")
    return {"cleaned": cleaned}


__all__ = ["download_and_send", "cleanup_old_files"]
