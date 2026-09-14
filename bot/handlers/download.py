"""
Download handler: entry point for the download FSM flow with PRO CACHE (Phase 2).

Pro Cache Features:
- Hash-based URL lookup (SHA-256 via HashService)
- Two-table cache: CachedDownload (URL metadata) + CachedQuality (per format)
- 3-button UX when cache found:
  1. 📚 N کیفیت از این ویدیو در آرشیو موجوده (دریافت سریع)
  2. 🔄 پیدا کردن کیفیت‌های جدید
  3. 🔙 بازگشت
"""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.states.download import DownloadStates
from bot.keyboards.inline.download import get_format_type_keyboard
from bot.keyboards.inline.cache_keyboards import (
    get_cache_options_keyboard,
    get_cached_qualities_keyboard,
)

from bot.handlers.session import get_session, clear_session
from utils.format_sizes import get_exact_format_sizes

from services.hash_service import HashService
from services import DownloadService
from modules import get_downloader, get_all_downloaders

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database.repositories.cached_download_repo import CachedDownloadRepository
from database.models.cached_download import CachedDownload, CachedQuality

import logging

logger = logging.getLogger(__name__)

router = Router()

# Initialize services
hash_service = HashService()


@router.message(F.text.startswith("http"))
async def handle_url(message: types.Message, state: FSMContext):
    """
    Handle incoming URL with Pro Cache check.

    Flow:
    1. Validate URL
    2. Generate SHA-256 hash via HashService
    3. Check cache by hash
    4. If cached → show 3-button UI
    5. If not cached → normal download flow
    """
    text = (message.text or "").strip()

    # 1. Validate URL format
    if not text or not text.startswith("http"):
        await message.reply("❌ لطفاً یک لینک معتبر ارسال کنید")
        return

    # 2. Generate URL hash
    url_info = hash_service.get_url_info(text)
    url_hash = url_info['hash']
    platform = url_info['platform'] or 'unknown'
    normalized_url = url_info['normalized_url']

    logger.info(f"[PRO CACHE] URL: {text[:60]}... → hash: {url_hash[:12]}... platform: {platform}")

    # 3. Check cache by hash
    cached_download = None
    try:
        from database.connection import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            repo = CachedDownloadRepository(session)
            cached_download = await repo.find_valid_by_url_hash(url_hash)

            if cached_download and cached_download.qualities:
                # Eager-load or copy list before session closes
                cached_qualities_count = len(cached_download.qualities)
                cached_id = cached_download.id
                cached_title = cached_download.title
                cached_duration = cached_download.duration
                cached_access_count = cached_download.access_count
            else:
                cached_qualities_count = 0
                cached_id = None
    except SQLAlchemyError as e:
        logger.warning(f"[CACHE] Database error during lookup: {e}")
        cached_qualities_count = 0
        cached_id = None

    # 4. Cache found → Show 3-button UI
    if cached_download and cached_qualities_count > 0:
        quality_count = cached_qualities_count

        # Build title preview
        title_preview = (
            cached_title[:80] + "..."
            if cached_title and len(cached_title) > 80
            else (cached_title or "بدون عنوان")
        )

        # Build caption text
        duration_text = ""
        if cached_duration:
            mins = cached_duration // 60
            secs = cached_duration % 60
            duration_text = f"\n⏱ مدت: {mins}:{secs:02d}"

        access_text = f"\n📊 تعداد دریافت: {cached_access_count} بار"

        caption = (
            f"✅ **این محتوا قبلاً دانلود شده!**\n\n"
            f"📹 **{title_preview}**{duration_text}\n"
            f"🔢 **{quality_count} کیفیت** در آرشیو موجود است{access_text}\n\n"
            f"🎯 یکی از گزینه‌های زیر را انتخاب کنید:"
        )

        # 3-button keyboard (use cached_id to stay well under 64-byte Telegram limit)
        kb = get_cache_options_keyboard(quality_count, cached_id)

        # Save URL info in state for later use
        await state.update_data(
            url=text,
            url_hash=url_hash,
            platform=platform,
            normalized_url=normalized_url,
            cached_download_id=cached_id,
            from_cache=True,
        )
        await state.set_state(DownloadStates.viewing_cached_files)

        await message.reply(caption, reply_markup=kb, parse_mode="Markdown")
        return

    # 5. Cache miss → Normal download flow
    logger.info(f"[CACHE MISS] hash={url_hash[:12]}... starting fresh download")

    # Resolve downloader
    handler = get_downloader(text)
    if handler is None:
        all_dl = get_all_downloaders()
        platforms = ", ".join(sorted(all_dl.keys())) or "هیچ ماژولی نصب نشده"
        logger.warning(f"[HANDLER] No downloader for URL: {text[:60]}")
        await message.reply(
            f"❌ **این پلتفرم پشتیبانی نمی‌شود**\n\n"
            f"پلتفرم‌های پشتیبانی‌شده:\n{platforms}",
            parse_mode="Markdown"
        )
        return

    logger.info(f"[HANDLER] Using {handler.__class__.__name__} for URL: {text[:60]}")

    # Save URL info in FSM
    await state.update_data(
        url=text,
        url_hash=url_hash,
        platform=platform,
        normalized_url=normalized_url,
        handler_name=handler.__class__.__name__,
    )

    from services.instagram_service import instagram_service
    if platform == "instagram" or instagram_service.is_instagram_url(text):
        from bot.handlers.download_exec import handle_instant_instagram_download
        await handle_instant_instagram_download(message, text, state)
        return

    # NEW PIPELINE INTEGRATION
    user_id = message.from_user.id
    session_data = get_session(user_id)
    session_data["url"] = text
    session_data["format_type"] = None
    session_data["quality"] = None
    session_data["codec"] = None
    session_data["subtitle"] = None
    session_data["send_as"] = None

    loading_msg = await message.reply("🔄 <b>در حال دریافت اطلاعات ویدیو...</b>", parse_mode="HTML")
    format_info = await get_exact_format_sizes(text)
    
    try:
        await loading_msg.delete()
    except Exception:
        pass

    if "error" in format_info:
        await message.reply(
            f"❌ <b>دریافت اطلاعات ویدیو با شکست مواجه شد!</b>\n\n"
            f"خطا:\n<code>{format_info['error'][:200]}</code>\n\n"
            f"لطفاً یک لینک دیگر امتحان کنید یا مجدداً تلاش نمایید.",
            parse_mode="HTML",
        )
        clear_session(user_id)
        await state.clear()
        return

    session_data["format_info"] = format_info
    await state.set_state(DownloadStates.selecting_format_type)

    await message.reply(
        "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>",
        reply_markup=get_format_type_keyboard(),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════════════
# PRO CACHE CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════════════════════

from aiogram.types import CallbackQuery
from aiogram import Bot


@router.callback_query(F.data.startswith("show_cached:"))
async def show_cached_qualities(
    query: CallbackQuery, state: FSMContext
):
    """
    Handle 📚 button: Show list of cached qualities for selection.
    Callback format: show_cached:{cache_id}
    """
    try:
        _, param = query.data.split(":", 1)
    except ValueError:
        await query.answer("❌ داده نامعتبر", show_alert=True)
        return

    logger.info(f"[PRO CACHE] Showing qualities for param: {param}")

    try:
        from database.connection import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            repo = CachedDownloadRepository(session)
            if param.isdigit():
                cached_download = await repo.get_by_id(int(param))
            else:
                cached_download = await repo.find_valid_by_url_hash(param)

            if not cached_download or not cached_download.qualities:
                await query.answer("❌ کیفیت‌های کش شده یافت نشد", show_alert=True)
                return

            qualities = list(cached_download.qualities)
            title = cached_download.title or "بدون عنوان"
            cached_id = cached_download.id

        # Build caption with quality list
        caption = f"📋 **کیفیت‌های موجود در آرشیو**\n\n📹 {title[:60]}\n\n"

        for i, q in enumerate(qualities, 1):
            size_text = f"{q.file_size_mb:.1f} MB" if q.file_size else "نامعلوم"
            caption += f"{i}. **{q.quality_label}** • {size_text} • {q.extension or ''}\n"

        caption += "\n🎯 یک کیفیت را برای دریافت سریع انتخاب کنید:"

        kb = get_cached_qualities_keyboard(qualities, show_back=True)

        # Update state
        await state.update_data(cached_download_id=cached_id)
        await state.set_state(DownloadStates.selecting_cached_file)

        await query.message.edit_text(caption, reply_markup=kb, parse_mode="Markdown")
        try:
            await query.answer()
        except Exception:
            pass

    except Exception as e:
        logger.exception(f"[PRO CACHE] Error showing qualities: {e}")
        await query.answer("❌ خطا در بارگذاری کیفیت‌ها", show_alert=True)


@router.callback_query(F.data.startswith("send_cached:"))
async def send_cached_file(
    query: CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Handle quality selection: Send cached file by file_id instantly.
    Callback format: send_cached:{quality_id}
    """
    try:
        _, id_str = query.data.split(":", 1)
        quality_id = int(id_str)
    except (ValueError, IndexError):
        await query.answer("❌ داده نامعتبر", show_alert=True)
        return

    logger.info(f"[PRO CACHE] Sending cached quality ID={quality_id}")

    await query.answer("⏳ در حال ارسال فایل از کش...")

    try:
        from database.connection import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            repo = CachedDownloadRepository(session)

            # Get quality
            quality = await repo.get_quality_by_id(quality_id)
            if not quality:
                await query.answer("❌ فایل کش شده یافت نشد", show_alert=True)
                return

            # Get parent download for caption
            cached_download = await session.get(CachedDownload, quality.cache_id)

            # Build caption
            title = cached_download.title if cached_download else "فایل کش شده"
            size_text = f"{quality.file_size_mb:.1f} MB" if quality.file_size else ""
            caption = (
                f"📦 **{title[:80]}**\n"
                f"🎯 کیفیت: {quality.quality_label}\n"
                f"📊 فرمت: {quality.extension or 'نامعلوم'}\n"
                f"{'📦 حجم: ' + size_text if size_text else ''}\n"
                f"⚡ **ارسال سریع از کش** (کمتر از 1 ثانیه)"
            )

            telegram_file_id = quality.telegram_file_id
            mime = quality.mime_type or ''
            cache_id = quality.cache_id

            # Send via file_id
            try:
                if 'video' in mime:
                    await bot.send_video(
                        chat_id=query.from_user.id,
                        video=telegram_file_id,
                        caption=caption,
                        parse_mode="Markdown"
                    )
                elif 'audio' in mime:
                    await bot.send_audio(
                        chat_id=query.from_user.id,
                        audio=telegram_file_id,
                        caption=caption,
                        parse_mode="Markdown"
                    )
                else:
                    await bot.send_document(
                        chat_id=query.from_user.id,
                        document=telegram_file_id,
                        caption=caption,
                        parse_mode="Markdown"
                    )
            except Exception as send_error:
                error_msg = str(send_error)
                logger.warning(f"[PRO CACHE] Send failed (file_id possibly expired): {error_msg}")

                # Mark as invalid if file_id expired
                if "FILE_ID_INVALID" in error_msg or "file_id" in error_msg.lower():
                    await repo.mark_invalid(cache_id)
                    await query.message.edit_text(
                        "⚠️ **فایل کش منقضی شده است**\n\n"
                        "فایل‌های تلگرام پس از مدتی منقضی می‌شوند.\n"
                        "لطفاً از گزینه «پیدا کردن کیفیت‌های جدید» استفاده کنید.",
                        parse_mode="Markdown"
                    )
                    await query.answer("⚠️ فایل کش منقضی شده", show_alert=True)
                    return
                raise

            # Mark as used (update stats)
            await repo.mark_used(cache_id, quality_id)

        # Delete the selection message
        try:
            await query.message.delete()
        except Exception:
            pass

        await state.clear()
        logger.info(f"[PRO CACHE] Successfully sent cached quality ID={quality_id}")

    except Exception as e:
        logger.exception(f"[PRO CACHE] Error sending cached file: {e}")
        await query.answer("❌ خطا در ارسال فایل کش شده", show_alert=True)


@router.callback_query(F.data.startswith("download_new:"))
async def download_new_callback(query: CallbackQuery, state: FSMContext):
    """
    Handle 🔄 button: Start fresh download for new qualities.
    Moves user to format selection flow.
    """
    await query.answer("🔄 شروع جستجوی کیفیت‌های جدید...")

    # Get URL from state or DB
    data = await state.get_data()
    url = data.get('url')

    if not url:
        try:
            _, param = query.data.split(":", 1)
            if param.isdigit():
                from database.connection import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    repo = CachedDownloadRepository(session)
                    cached = await repo.get_by_id(int(param))
                    if cached:
                        url = cached.original_url
        except Exception:
            pass

    if not url:
        await query.answer("❌ لینک یافت نشد. لطفاً دوباره ارسال کنید.", show_alert=True)
        return

    logger.info(f"[PRO CACHE] User requested fresh download for: {url[:60]}...")

    # NEW PIPELINE INTEGRATION
    user_id = query.from_user.id
    session_data = get_session(user_id)
    session_data["url"] = url
    session_data["format_type"] = None
    session_data["quality"] = None
    session_data["codec"] = None
    session_data["subtitle"] = None
    session_data["send_as"] = None

    await query.message.edit_text("🔄 <b>در حال دریافت اطلاعات ویدیو...</b>", parse_mode="HTML")
    format_info = await get_exact_format_sizes(url)

    if "error" in format_info:
        await query.message.edit_text(
            f"❌ <b>دریافت اطلاعات ویدیو با شکست مواجه شد!</b>\n\n"
            f"خطا:\n<code>{format_info['error'][:200]}</code>\n\n"
            f"لطفاً یک لینک دیگر امتحان کنید یا مجدداً تلاش نمایید.",
            parse_mode="HTML",
        )
        clear_session(user_id)
        await state.clear()
        return

    session_data["format_info"] = format_info
    await state.set_state(DownloadStates.selecting_format_type)

    await query.message.edit_text(
        "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>",
        reply_markup=get_format_type_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_cache_options")
async def back_to_cache_options(query: CallbackQuery, state: FSMContext):
    """
    Handle ◀️ back button from quality list → return to 3-button options.
    """
    data = await state.get_data()
    cached_download_id = data.get('cached_download_id')

    if not cached_download_id:
        await query.answer("❌ اطلاعات کش یافت نشد", show_alert=True)
        return

    try:
        from database.connection import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            repo = CachedDownloadRepository(session)
            cached_download = await repo.get_by_id(cached_download_id)

            if not cached_download or not cached_download.qualities:
                await query.answer("❌ اطلاعات کش یافت نشد", show_alert=True)
                return

            quality_count = len(cached_download.qualities)
            kb = get_cache_options_keyboard(quality_count, cached_download.id)
            title = cached_download.title or "بدون عنوان"
            duration = cached_download.duration
            access_count = cached_download.access_count

        await state.set_state(DownloadStates.viewing_cached_files)

        title_preview = title[:80] + "..." if len(title) > 80 else title
        duration_text = ""
        if duration:
            mins = duration // 60
            secs = duration % 60
            duration_text = f"\n⏱ مدت: {mins}:{secs:02d}"

        access_text = f"\n📊 تعداد دریافت: {access_count} بار"

        await query.message.edit_text(
            f"✅ **این محتوا قبلاً دانلود شده!**\n\n"
            f"📹 **{title_preview}**{duration_text}\n"
            f"🔢 **{quality_count} کیفیت** در آرشیو موجود است{access_text}\n\n"
            f"🎯 یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        try:
            await query.answer()
        except Exception:
            pass
    except Exception as e:
        logger.exception(f"[PRO CACHE] Error going back: {e}")
        await query.answer("❌ خطا", show_alert=True)


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(query: CallbackQuery, state: FSMContext):
    """
    Handle 🔙 return button: Clear state and go back to main menu.
    """
    await state.clear()
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.message.answer(
        "🔙 به منوی اصلی بازگشتید.\n\n"
        "💡 برای دانلود محتوای جدید، لینک مورد نظر را ارسال کنید."
    )
    try:
        await query.answer()
    except Exception:
        pass


@router.callback_query(F.data == "fresh_search")
async def fresh_search_callback(query: CallbackQuery, state: FSMContext):
    """
    Legacy handler: User requested fresh search from old UI.
    Redirects to format selection.
    """
    await state.set_state(DownloadStates.selecting_format_type)
    await query.message.edit_text(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard(),
        parse_mode="Markdown"
    )
    try:
        await query.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════
# LEGACY: use_cached handler (kept for backward compat)
# ═══════════════════════════════════════════════════════════════════════

@router.callback_query(
    DownloadStates.viewing_cached_files,
    F.data.startswith("use_cached:")
)
async def use_cached_file_legacy(
    query: CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Legacy handler: Send a previously cached Telegram file_id.
    Kept for backward compatibility with old cached_downloads format.
    """
    try:
        _, id_str = query.data.split(":", 1)
        quality_id = int(id_str)

        from database.connection import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            # Try to load as CachedQuality first (new format)
            quality = await session.get(CachedQuality, quality_id)
            if quality:
                # Use the new send logic by redirecting callback data
                query.data = f"send_cached:{quality_id}"
                await send_cached_file(query, state, bot)
                return

            # Fallback: try as old CachedDownload
            cd = await session.get(CachedDownload, quality_id)
            if not cd or not cd.qualities:
                await query.answer("❌ فایل کش‌شده پیدا نشد", show_alert=True)
                return

            # Send first available quality
            first_quality = cd.qualities[0] if cd.qualities else None
            if not first_quality:
                await query.answer("❌ کیفیتی یافت نشد", show_alert=True)
                return

            query.data = f"send_cached:{first_quality.id}"
            await send_cached_file(query, state, bot)

    except Exception as e:
        logger.exception(f"[LEGACY CACHE] Error: {e}")
        await query.answer("❌ خطا داخلی", show_alert=True)


# ═══════════════════════════════════════════════════════════════════════
# INSTAGRAM AUDIO EXTRACTION CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("ig_audio:"))
async def handle_instagram_audio_callback(query: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle 🎵 استخراج صوت (MP3) button for Instagram Reels/Posts."""
    await query.answer("🔄 در حال استخراج صوت...")
    shortcode = query.data.split(":", 1)[1]
    url = f"https://www.instagram.com/reel/{shortcode}/"
    
    status_msg = await query.message.reply("🎵 <b>در حال استخراج صوت با کیفیت بالا (MP3)...</b>", parse_mode="HTML")
    
    import asyncio
    import os
    from pathlib import Path
    from aiogram.types import FSInputFile
    from services.instagram_service import instagram_service
    
    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_mp3 = temp_dir / f"ig_audio_{shortcode}.mp3"
    temp_src = temp_dir / f"ig_src_{shortcode}.mp4"
    
    try:
        # 1. Download media directly to disk with session cookies (~2-3s)
        dl_file = await instagram_service.download_media_to_file(url, temp_src)
        if not dl_file or not os.path.exists(dl_file):
            # Fallback to /p/ URL
            dl_file = await instagram_service.download_media_to_file(f"https://www.instagram.com/p/{shortcode}/", temp_src)

        if dl_file and os.path.exists(dl_file):
            # 2. Extract MP3 audio stream using ffmpeg
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", str(dl_file), "-vn", "-c:a", "libmp3lame", "-b:a", "192k", str(temp_mp3),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()

            if temp_mp3.exists() and temp_mp3.stat().st_size > 1000:
                await query.message.reply_audio(
                    audio=FSInputFile(temp_mp3),
                    title=f"Instagram Audio ({shortcode})",
                    performer="Instagram Audio",
                    caption=f"🎵 <b>فایل صوتی استخراج شده (MP3 - 192kbps)</b>\n\n⚡ <i>@MaxDownloaderBot</i>",
                    parse_mode="HTML"
                )
                try:
                    await status_msg.delete()
                except Exception:
                    pass
                return

        await status_msg.edit_text("❌ متاسفانه استخراج صوت از این ویدیو امکان‌پذیر نشد.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"[InstagramAudio] Error: {e}", exc_info=True)
        try:
            await status_msg.edit_text(f"❌ خطا در استخراج صوت:\n<code>{str(e)[:100]}</code>", parse_mode="HTML")
        except Exception:
            pass
    finally:
        for f in [temp_mp3, temp_src]:
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass


__all__ = ["router"]
