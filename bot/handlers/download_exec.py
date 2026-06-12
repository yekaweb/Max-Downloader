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

        if format_type == "video":
            codec = session_data.get("codec")
            if codec == "h264":
                ydl_opts["format"] = "best[ext=mp4][vcodec^=h264]"
            elif codec == "av1":
                ydl_opts["format"] = "best[ext=webm][vcodec^=av1]"
            elif codec == "vp9":
                ydl_opts["format"] = "best[ext=webm][vcodec^=vp9]"
            else:
                ydl_opts["format"] = "best[ext=mp4]"

        else:
            audio_fmt = session_data.get("audio_format", {"format": "mp3", "bitrate": "128"})
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_fmt.get("format", "mp3"),
                "preferredquality": audio_fmt.get("bitrate", "128"),
            }]

        filename = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not filename or not os.path.exists(filename):
            raise FileNotFoundError("فایل دانلود شده پیدا نشد")

        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)

        caption = (
            f"✅ دانلود موفق!\n\n"
            f"📹 {os.path.basename(filename)}\n"
            f"💾 {file_size_mb:.1f} MB"
        )

        send_as = session_data.get("send_as", "file")
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

    except Exception as exc:
        await message.answer(
            f"❌ خطا در دانلود:\n{str(exc)[:200]}"
        )

    finally:
        try:
            await progress_msg.delete()
        except Exception:
            pass

        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass

        clear_session(user_id)
        await state.clear()
