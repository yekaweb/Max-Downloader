"""Download execution logic for the modular handler flow."""

import os
import glob
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

COOKIE_FILE = Path("/root/Max-Downloader/cookies.txt")

# Shared bot-detection bypass options with Anti-Bot Player Client Spoofing
_BASE_YDL_OPTS = {
    'socket_timeout': 30,
    'noplaylist': True,
    'cookiefile': str(COOKIE_FILE) if COOKIE_FILE.exists() else None,
    'js_runtimes': {'node': {}},
    'remote_components': ['ejs:github'],
    'extractor_args': {
        'youtube': {
            'player_client': ['all'],
            'lang': ['en', 'fa'],
        }
    },
    'http_headers': {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/128.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
    },
    'retries': 10,
    'fragment_retries': 10,
    'skip_unavailable_fragments': True,
}


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

    media_title = session_data.get("format_info", {}).get("title") or "در حال آماده‌سازی..."
    progress_msg = await message.answer(
        generate_progress_message(
            title=media_title,
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
            **_BASE_YDL_OPTS,
            "quiet": True,
            "no_warnings": True,
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
        }
        
        if max_file_size:
            ydl_opts["max_filesize"] = max_file_size

        is_youtube = "youtube.com" in url or "youtu.be" in url

        if not is_youtube:
            if format_type == "video":
                ydl_opts["format"] = "bestvideo+bestaudio/best"
            else:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }]
        elif format_type == "video":
            codec = session_data.get("codec")
            quality_str = session_data.get("quality", "720")
            audio_lang = session_data.get("audio_lang")  # Phase 5.5: None = default

            # Supported video qualities
            quality_map = {
                "4k": 2160,
                "1440": 1440,
                "1080": 1080,
                "720": 720,
                "480": 480,
                "360": 360,
                "240": 240,
                "144": 144,
            }
            height = quality_map.get(quality_str, 720)

            # Phase 5.5: build audio selector with optional language constraint
            if audio_lang:
                audio_sel = f"bestaudio[language={audio_lang}]/bestaudio"
            else:
                audio_sel = "bestaudio"

            # FIX Bug #6: all fallbacks are height-constrained
            if codec == "h264":
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][vcodec*=avc]+{audio_sel}[ext=m4a]"
                    f"/bestvideo[height<={height}][ext=mp4]+{audio_sel}"
                    f"/bestvideo[height<={height}]+{audio_sel}"
                    f"/best[height<={height}]"
                )
            elif codec == "av1":
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][vcodec^=av01]+{audio_sel}"
                    f"/bestvideo[height<={height}]+{audio_sel}"
                    f"/best[height<={height}]"
                )
            elif codec == "vp9":
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][vcodec^=vp09]+{audio_sel}"
                    f"/bestvideo[height<={height}][vcodec^=vp9]+{audio_sel}"
                    f"/bestvideo[height<={height}]+{audio_sel}"
                    f"/best[height<={height}]"
                )
            else:
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}]+{audio_sel}"
                    f"/best[height<={height}]"
                )

        else:
            audio_fmt = session_data.get("audio_format", {"format": "mp3", "bitrate": "128"})
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_fmt.get("format", "mp3"),
                "preferredquality": audio_fmt.get("bitrate", "128"),
            }]

        from utils.proxy_manager import get_random_proxy
        proxy = get_random_proxy()
        if proxy:
            ydl_opts['proxy'] = proxy

        filename = None
        
        import asyncio
        loop = asyncio.get_running_loop()
        
        from utils.progress import update_progress_message

        async def yt_dlp_progress_callback(percent, dl_mb, tot_mb, speed, eta, phase="download"):
            await update_progress_message(
                message=message,
                user_id=user_id,
                chat_id=message.chat.id,
                message_id=progress_msg.message_id,
                title=media_title,
                progress_percent=percent,
                downloaded_mb=dl_mb,
                total_mb=tot_mb,
                speed_mbps=speed,
                eta_seconds=eta,
                phase=phase
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
                        yt_dlp_progress_callback(percent, dl_mb, tot_mb, speed_mbps, eta_sec, "download"),
                        loop
                    )
                except Exception:
                    pass
            elif d['status'] == 'finished':
                try:
                    asyncio.run_coroutine_threadsafe(
                        yt_dlp_progress_callback(100.0, 0, 0, 0, 0, "processing"),
                        loop
                    )
                except Exception:
                    pass

        ydl_opts["progress_hooks"] = [progress_hook]

        # Run yt-dlp in an executor to prevent blocking the async event loop
        import functools
        
        def run_ytdlp():
            import glob
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                raw_name = ydl.prepare_filename(info)
                # FIX Bug #5: prepare_filename returns pre-merge extension.
                # After ffmpeg merges audio+video, the extension changes.
                # Use glob to find the actual file by base name.
                base = os.path.splitext(raw_name)[0]
                matches = [f for f in glob.glob(f"{base}.*") if os.path.isfile(f)]
                if matches:
                    return max(matches, key=os.path.getsize)
                return raw_name  # Fallback to original if no glob match
                
        max_retries = 3
        retry_delay = 2
        filename = None
        engine_used = "yt-dlp (Native)"
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
                    # Fall back to Waterfall Download Service (Tier 2 Cobalt / Tier 3 Direct)
                    import logging
                    logging.warning(f"yt-dlp failed after {max_retries} attempts: {e}. Activating Waterfall Multi-Engine Fallback...")
                    try:
                        from services.waterfall_download_service import waterfall_download_service
                        filename, engine_used = await waterfall_download_service.execute_download(
                            url=url,
                            format_type=format_type,
                            quality=session_data.get("quality", "720"),
                            codec=session_data.get("codec", "h264"),
                            audio_format=session_data.get("audio_format"),
                            audio_lang=session_data.get("audio_lang"),
                            max_filesize=max_file_size,
                            progress_callback=yt_dlp_progress_callback,
                        )
                        if not filename or not os.path.exists(filename):
                            raise e
                    except Exception as waterfall_err:
                        logging.error(f"Waterfall fallback also failed: {waterfall_err}")
                        raise e

        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)

        caption = (
            f"✅ دانلود موفق!\n\n"
            f"📹 {os.path.basename(filename)}\n"
            f"💾 {file_size_mb:.1f} MB\n"
            f"⚡ موتور دانلود: {engine_used}"
        )

        send_as = session_data.get("send_as", "file")
        
        # Check if Pyrogram is available and file is > 50MB
        import bot.loader
        pyrogram_client = getattr(bot.loader, "pyrogram_client", None)
        
        sent_msg = None
        if file_size_mb > 49 and pyrogram_client:
            await progress_msg.edit_text("⬆️ در حال آپلود فایل بزرگ (Pyrogram)...")
            from services.file_service import FileService
            file_svc = FileService(temp_dir="temp_downloads", cache_dir="cached_files", pyrogram_client=pyrogram_client)
            
            async def progress_callback(current, total):
                pass
                
            sent_msg = await file_svc.upload_to_telegram(
                file_path=filename,
                chat_id=message.chat.id,
                caption=caption,
                progress_callback=progress_callback
            )
        else:
            if format_type == "video" and send_as == "video":
                sent_msg = await message.reply_video(
                    FSInputFile(filename),
                    caption=caption,
                )
            else:
                sent_msg = await message.reply_document(
                    FSInputFile(filename),
                    caption=caption,
                )

        # Pro Cache write-back
        if sent_msg:
            try:
                telegram_file_id = None
                if getattr(sent_msg, "video", None):
                    telegram_file_id = sent_msg.video.file_id
                elif getattr(sent_msg, "document", None):
                    telegram_file_id = sent_msg.document.file_id
                elif getattr(sent_msg, "audio", None):
                    telegram_file_id = sent_msg.audio.file_id

                if telegram_file_id:
                    from services.hash_service import HashService
                    from database.repositories.cached_download_repo import CachedDownloadRepository
                    hs = HashService()
                    u_info = hs.get_url_info(url)
                    u_hash = u_info.get("hash")
                    u_plat = u_info.get("platform") or "youtube"
                    quality_str = session_data.get("quality", "720")
                    codec_str = session_data.get("codec", "h264")

                    async with AsyncSessionLocal() as db_session:
                        c_repo = CachedDownloadRepository(db_session)
                        await c_repo.create_from_upload(
                            source_url=url,
                            source_platform=u_plat,
                            media_title=os.path.basename(filename),
                            media_duration=None,
                            media_uploader=None,
                            telegram_file_id=telegram_file_id,
                            file_size=file_size,
                            file_type="video/mp4" if format_type == "video" else "audio/mp3",
                            quality=str(quality_str),
                            format_codec=str(codec_str),
                            format_container=os.path.splitext(filename)[1].lstrip("."),
                            url_hash=u_hash,
                        )
            except Exception as cache_err:
                import logging
                logging.getLogger(__name__).warning(f"Failed to save Pro Cache file_id: {cache_err}")

    except yt_dlp.utils.DownloadError as e:
        msg = str(e).lower()
        if "sign in" in msg or "login" in msg:
            error_text = "❌ این محتوا خصوصی است یا نیاز به لاگین دارد."
        elif "unavailable" in msg or "not found" in msg or "404" in msg:
            error_text = "❌ محتوا پیدا نشد یا حذف شده است."
        elif "geo-restricted" in msg or "country" in msg:
            error_text = "❌ این محتوا در سرور فعلی محدودیت منطقه‌ای دارد."
        elif "403" in msg or "forbidden" in msg:
            error_text = "❌ یوتیوب موقتاً دسترسی مستقیم به این کیفیت را محدود کرد. لطفاً کیفیت دیگری را امتحان کنید."
        else:
            error_text = f"❌ خطا در دریافت مدیا:\n{str(e)[:200]}"
        try:
            await progress_msg.edit_text(error_text, parse_mode="HTML")
        except Exception:
            await message.answer(error_text, parse_mode="HTML")
        
    except FileNotFoundError:
        error_text = "❌ فایل پس از دانلود پیدا نشد. ممکن است دانلود ناقص بوده باشد."
        try:
            await progress_msg.edit_text(error_text, parse_mode="HTML")
        except Exception:
            await message.answer(error_text, parse_mode="HTML")
        
    except Exception as exc:
        import traceback
        import bot.loader
        logger = getattr(bot.loader, "logger", None)
        if logger:
            logger.error(f"Download Error: {exc}\n{traceback.format_exc()}")
        error_text = f"❌ خطای سیستمی رخ داد:\n{str(exc)[:200]}"
        try:
            await progress_msg.edit_text(error_text, parse_mode="HTML")
        except Exception:
            await message.answer(error_text, parse_mode="HTML")

    finally:
        if sent_msg:
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


async def handle_instant_instagram_download(message: Message, url: str, state: FSMContext):
    """
    Instant 1-Click Zero-Login Instagram Downloader Handler.
    Bypasses redundant format selection menus and delivers direct media in 1-2 seconds.
    Supports single reels, single photos, and multi-slide carousels (MediaGroups).
    """
    user_id = message.from_user.id
    from database.connection import AsyncSessionLocal
    from services.subscription_service import SubscriptionService
    from services.instagram_service import instagram_service
    from services.cobalt_service import cobalt_service
    from services.hash_service import HashService
    from database.repositories.cached_download_repo import CachedDownloadRepository
    from aiogram.types import InputMediaPhoto, InputMediaVideo
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    # 1. Check user permission & subscription limits
    async with AsyncSessionLocal() as db:
        sub_service = SubscriptionService(db)
        can_dl, error_msg = await sub_service.can_user_download(user_id)
        if not can_dl:
            await message.reply(f"❌ {error_msg}")
            clear_session(user_id)
            await state.clear()
            return

    # 2. Check Pro Cache (Instant 0.1s response for previously downloaded media)
    hs = HashService()
    u_info = hs.get_url_info(url)
    u_hash = u_info.get("hash")

    if u_hash:
        async with AsyncSessionLocal() as db_session:
            c_repo = CachedDownloadRepository(db_session)
            cached = await c_repo.find_valid_by_url_hash(u_hash)
            if cached and cached.qualities:
                for q in cached.qualities:
                    if q.telegram_file_id:
                        try:
                            # Send cached file directly
                            shortcode = instagram_service.extract_shortcode(url) or "media"
                            builder = InlineKeyboardBuilder()
                            builder.button(text="🎵 استخراج صوت (MP3)", callback_data=f"ig_audio:{shortcode}")
                            
                            c_text = f"✅ دانلود سریع از حافظه کش (Lightning Cache)\n\n⚡ <i>ارسال شده توسط ربات</i>"
                            if "image" in (q.file_type or ""):
                                await message.reply_photo(photo=q.telegram_file_id, caption=c_text, parse_mode="HTML")
                            else:
                                await message.reply_video(video=q.telegram_file_id, caption=c_text, parse_mode="HTML", reply_markup=builder.as_markup(), supports_streaming=True)
                            
                            # Record download usage
                            await sub_service.record_download(user_id)
                            clear_session(user_id)
                            await state.clear()
                            return
                        except Exception as cache_send_err:
                            import logging
                            logging.warning(f"Failed to send cached telegram_file_id: {cache_send_err}")
                            break

    # 3. Status Notification
    status_msg = await message.reply("⚡ <b>در حال پردازش و دریافت رسانه از اینستاگرام...</b>", parse_mode="HTML")

    try:
        # 4. Resolve media through Next-Gen Waterfall Engine
        res = await instagram_service.resolve_media(url)
        if not res.get("success"):
            err_msg = res.get("message", "متاسفانه امکان دریافت رسانه وجود ندارد.")
            await status_msg.edit_text(f"❌ <b>خطا در دریافت از اینستاگرام</b>\n\n{err_msg}", parse_mode="HTML")
            clear_session(user_id)
            await state.clear()
            return

        items = res.get("items", [])
        if not items:
            await status_msg.edit_text("❌ محتوای قابل دانلودی در این لینک یافت نشد.", parse_mode="HTML")
            clear_session(user_id)
            await state.clear()
            return

        shortcode = res.get("shortcode") or instagram_service.extract_shortcode(url) or "media"
        caption_raw = res.get("caption", "").strip()
        engine_name = res.get("engine", "Fast CDN")
        footer = f"\n\n⚡ <i>دانلود شده توسط @MaxDownloaderBot</i>"
        full_caption = (caption_raw[:850] + footer) if caption_raw else f"📹 Instagram ({shortcode}){footer}"

        builder = InlineKeyboardBuilder()
        builder.button(text="🎵 استخراج صوت (MP3)", callback_data=f"ig_audio:{shortcode}")
        kb = builder.as_markup()

        sent_msg = None

        # ----------------------------------------------------
        # CASE A: Multi-item Carousel / Album (MediaGroup)
        # ----------------------------------------------------
        if res.get("is_album") and len(items) > 1:
            media_group = []
            for idx, it in enumerate(items[:10]):  # Telegram limit is max 10 items per media group
                c = full_caption if idx == 0 else None
                m_url = it.get("url")
                if it.get("type") == "photo":
                    media_group.append(InputMediaPhoto(media=m_url, caption=c, parse_mode="HTML"))
                else:
                    media_group.append(InputMediaVideo(media=m_url, caption=c, parse_mode="HTML"))

            try:
                await message.reply_media_group(media=media_group)
            except Exception as mg_err:
                import logging
                logging.warning(f"Direct URL MediaGroup failed ({mg_err}), sending items individually...")
                for it in items[:5]:
                    if it.get("type") == "photo":
                        await message.reply_photo(photo=it["url"])
                    else:
                        await message.reply_video(video=it["url"], reply_markup=kb, supports_streaming=True)

        # ----------------------------------------------------
        # CASE B: Single Video / Reel
        # ----------------------------------------------------
        elif items[0].get("type") == "video":
            v_url = items[0]["url"]
            try:
                # Direct CDN URL Send (~1.5s, 0 VPS Bandwidth)
                sent_msg = await message.reply_video(
                    video=v_url,
                    caption=full_caption,
                    parse_mode="HTML",
                    reply_markup=kb,
                    supports_streaming=True
                )
            except Exception as direct_err:
                import logging
                logging.warning(f"Direct video URL send failed: {direct_err}. Streaming via temp download...")
                temp_dir = Path("temp_downloads")
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_file = temp_dir / f"ig_{shortcode}.mp4"
                try:
                    await cobalt_service.download_file(v_url, temp_file)
                    sent_msg = await message.reply_video(
                        video=FSInputFile(temp_file),
                        caption=full_caption,
                        parse_mode="HTML",
                        reply_markup=kb,
                        supports_streaming=True
                    )
                finally:
                    if temp_file.exists():
                        try:
                            temp_file.unlink()
                        except Exception:
                            pass

        # ----------------------------------------------------
        # CASE C: Single Photo
        # ----------------------------------------------------
        else:
            p_url = items[0]["url"]
            try:
                sent_msg = await message.reply_photo(
                    photo=p_url,
                    caption=full_caption,
                    parse_mode="HTML"
                )
            except Exception as direct_photo_err:
                import logging
                logging.warning(f"Direct photo URL send failed: {direct_photo_err}. Streaming via temp download...")
                temp_dir = Path("temp_downloads")
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_file = temp_dir / f"ig_{shortcode}.jpg"
                try:
                    await cobalt_service.download_file(p_url, temp_file)
                    sent_msg = await message.reply_photo(
                        photo=FSInputFile(temp_file),
                        caption=full_caption,
                        parse_mode="HTML"
                    )
                finally:
                    if temp_file.exists():
                        try:
                            temp_file.unlink()
                        except Exception:
                            pass

        # 5. Record download usage & Write Pro Cache
        async with AsyncSessionLocal() as db_session:
            sub_service = SubscriptionService(db_session)
            await sub_service.record_download(user_id)

            if sent_msg and u_hash:
                f_id = None
                if getattr(sent_msg, "video", None):
                    f_id = sent_msg.video.file_id
                elif getattr(sent_msg, "photo", None):
                    f_id = sent_msg.photo[-1].file_id

                if f_id:
                    try:
                        c_repo = CachedDownloadRepository(db_session)
                        await c_repo.create_from_upload(
                            source_url=url,
                            source_platform="instagram",
                            media_title=f"Instagram_{shortcode}",
                            media_duration=None,
                            media_uploader=None,
                            telegram_file_id=f_id,
                            file_size=15 * 1024 * 1024,
                            file_type="video/mp4" if items[0]["type"] == "video" else "image/jpeg",
                            quality="original",
                            format_codec="h264",
                            format_container="mp4" if items[0]["type"] == "video" else "jpg",
                            url_hash=u_hash,
                        )
                    except Exception as cache_save_err:
                        import logging
                        logging.warning(f"Error caching Instagram file_id: {cache_save_err}")

        # 6. Clean status message
        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as exc:
        import logging
        logging.error(f"[InstagramInstant] Unexpected error: {exc}", exc_info=True)
        try:
            await status_msg.edit_text(f"❌ خطایی در پردازش ویدیو رخ داد:\n<code>{str(exc)[:150]}</code>", parse_mode="HTML")
        except Exception:
            await message.reply("❌ متاسفانه در دانلود اینستاگرام خطایی رخ داد.")
    finally:
        clear_session(user_id)
        await state.clear()

