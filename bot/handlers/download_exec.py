"""Download execution logic for the modular handler flow."""

import os
from pathlib import Path
from typing import Optional

from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.handlers.session import get_session, clear_session
from utils.progress import generate_progress_message

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


async def start_download(message: Message, user_id: int, state: FSMContext):
    """Start the actual yt-dlp download based on user selections."""
    session_data = get_session(user_id)
    url = session_data.get("url")
    format_type = session_data.get("format_type")

    if not url or not format_type:
        await message.answer("❌ خطا: اطلاعات دانلود کامل نیست.")
        clear_session(user_id)
        await state.clear()
        return

    from database.connection import AsyncSessionLocal
    from services.subscription_service import SubscriptionService

    max_file_size = None
    async with AsyncSessionLocal() as db:
        sub_service = SubscriptionService(db)
        can_dl, error_msg = await sub_service.can_user_download(user_id)
        if not can_dl:
            await message.answer("❌ " + error_msg)
            clear_session(user_id)
            await state.clear()
            return
            
        limits = await sub_service.check_user_limits(user_id)
        max_file_size = limits.get("max_file_size")

    progress_msg = await message.answer(
        generate_progress_message(
            title="جاری سازی دانلود...",
            progress_percent=0,
            downloaded_mb=0,
            total_mb=1,
            speed_mbps=0,
            eta_seconds=0,
            phase="download",
        ),
        parse_mode="HTML",
    )

    output_dir = Path("temp_downloads")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if not YTDLP_AVAILABLE:
            raise RuntimeError("yt-dlp نصب نیست")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        }
        
        if max_file_size:
            ydl_opts["max_filesize"] = max_file_size

        if format_type == "video":
            codec = session_data.get("codec")
            quality_str = session_data.get("quality", "1080")
            
            quality_map = {
                "4k": 2160,
                "1080": 1080,
                "720": 720,
                "480": 480,
                "360": 360,
                "240": 240
            }
            height = quality_map.get(quality_str, 1080)

            if codec == "h264":
                ydl_opts["format"] = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<={height}]/best"
            elif codec == "av1":
                ydl_opts["format"] = f"bestvideo[height<={height}][vcodec^=av01]+bestaudio/best[height<={height}]/best"
            elif codec == "vp9":
                ydl_opts["format"] = f"bestvideo[height<={height}][vcodec^=vp09]+bestaudio/bestvideo[height<={height}][vcodec^=vp9]+bestaudio/best[height<={height}]/best"
            else:
                ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"

        else:
            audio_fmt = session_data.get("audio_format", {"format": "mp3", "bitrate": "128"})
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_fmt.get("format", "mp3"),
                "preferredquality": audio_fmt.get("bitrate", "128"),
            }]

        filename = None
        
        import asyncio
        loop = asyncio.get_running_loop()
        
        from utils.progress import update_progress_message

        async def yt_dlp_progress_callback(percent, dl_mb, tot_mb, speed, eta):
            await update_progress_message(
                message=message,
                user_id=user_id,
                chat_id=message.chat.id,
                message_id=progress_msg.message_id,
                title=f"{url[:20]}...",
                progress_percent=percent,
                downloaded_mb=dl_mb,
                total_mb=tot_mb,
                speed_mbps=speed,
                eta_seconds=eta,
                phase="download"
            )

        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    speed_bytes = d.get('speed', 0) or 0
                    eta_sec = d.get('eta', 0) or 0

                    if total_bytes > 0:
                        percent = (downloaded_bytes / total_bytes) * 100
                    else:
                        percent = 0

                    dl_mb = downloaded_bytes / (1024 * 1024)
                    tot_mb = total_bytes / (1024 * 1024) if total_bytes else 0
                    speed_mbps = speed_bytes / (1024 * 1024)

                    asyncio.run_coroutine_threadsafe(
                        yt_dlp_progress_callback(percent, dl_mb, tot_mb, speed_mbps, eta_sec),
                        loop
                    )
                except Exception:
                    pass

        ydl_opts["progress_hooks"] = [progress_hook]

        # Run yt-dlp in an executor to prevent blocking the async event loop
        import functools
        
        def run_ytdlp():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
                
        max_retries = 3
        retry_delay = 2
        filename = None
        
        for attempt in range(1, max_retries + 1):
            try:
                filename = await loop.run_in_executor(None, run_ytdlp)
                if filename and os.path.exists(filename):
                    break
                else:
                    raise FileNotFoundError("فایل دانلود شده پیدا نشد")
            except Exception as e:
                if attempt < max_retries:
                    import logging
                    logging.warning(f"Download attempt {attempt} failed: {e}")
                    await asyncio.sleep(retry_delay)
                else:
                    raise e

        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)

        caption = (
            f"✅ دانلود موفق!\n\n"
            f"📹 {os.path.basename(filename)}\n"
            f"💾 {file_size_mb:.1f} MB"
        )

        send_as = session_data.get("send_as", "file")
        
        # Check if Pyrogram is available and file is > 50MB
        import bot.loader
        pyrogram_client = getattr(bot.loader, "pyrogram_client", None)
        
        if file_size_mb > 49 and pyrogram_client:
            await progress_msg.edit_text("⬆️ در حال آپلود فایل بزرگ (Pyrogram)...")
            from services.file_service import FileService
            file_svc = FileService(temp_dir="temp_downloads", cache_dir="cached_files", pyrogram_client=pyrogram_client)
            
            async def progress_callback(current, total):
                pass  # Minimal callback to prevent errors; complex progress handling can be added later
                
            await file_svc.upload_to_telegram(
                file_path=filename,
                chat_id=message.chat.id,
                caption=caption,
                progress_callback=progress_callback
            )
        else:
            if format_type == "video" and send_as == "video":
                await message.reply_video(
                    FSInputFile(filename),
                    caption=caption,
                )
            else:
                await message.reply_document(
                    FSInputFile(filename),
                    caption=caption,
                )

    except yt_dlp.utils.DownloadError as e:
        msg = str(e).lower()
        if "sign in" in msg or "login" in msg:
            error_text = "❌ این محتوا خصوصی است یا نیاز به لاگین دارد."
        elif "unavailable" in msg or "not found" in msg or "404" in msg:
            error_text = "❌ محتوا پیدا نشد یا حذف شده است."
        elif "geo-restricted" in msg or "country" in msg:
            error_text = "❌ این محتوا در سرور فعلی محدودیت منطقه‌ای دارد."
        else:
            error_text = f"❌ خطا در دریافت مدیا:\n{str(e)[:200]}"
        await message.answer(error_text)
        
    except FileNotFoundError:
        await message.answer("❌ فایل پس از دانلود پیدا نشد. ممکن است دانلود ناقص بوده باشد.")
        
    except Exception as exc:
        import traceback
        import bot.loader
        logger = getattr(bot.loader, "logger", None)
        if logger:
            logger.error(f"Download Error: {exc}\n{traceback.format_exc()}")
        await message.answer(
            f"❌ خطای سیستمی رخ داد:\n{str(exc)[:200]}"
        )

    finally:
        try:
            await progress_msg.delete()
        except Exception:
            pass

        if filename:
            try:
                base_name = os.path.splitext(filename)[0]
                import glob
                for f in glob.glob(f"{base_name}*"):
                    if os.path.exists(f):
                        try:
                            os.remove(f)
                        except Exception:
                            pass
            except Exception:
                pass

        clear_session(user_id)
        await state.clear()
