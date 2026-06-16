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
async def handle_url(message: types.Message, state: FSMContext, session: AsyncSession):
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
        repo = CachedDownloadRepository(session)
        cached_download = await repo.find_valid_by_url_hash(url_hash)

        if cached_download:
            quality_count = len(cached_download.qualities) if cached_download.qualities else 0
            logger.info(
                f"[CACHE HIT] hash={url_hash[:12]}... "
                f"title={cached_download.title[:40] if cached_download.title else 'N/A'}... "
                f"qualities={quality_count}"
            )
    except SQLAlchemyError as e:
        logger.warning(f"[CACHE] Database error during lookup: {e}")

    # 4. Cache found → Show 3-button UI
    if cached_download and cached_download.qualities:
        quality_count = len(cached_download.qualities)

        # Build title preview
        title_preview = (
            cached_download.title[:80] + "..."
            if cached_download.title and len(cached_download.title) > 80
            else (cached_download.title or "بدون عنوان")
        )

        # Build caption text
        duration_text = ""
        if cached_download.duration:
            mins = cached_download.duration // 60
            secs = cached_download.duration % 60
            duration_text = f"\n⏱ مدت: {mins}:{secs:02d}"

        access_text = f"\n📊 تعداد دریافت: {cached_download.access_count} بار"

        caption = (
            f"✅ **این محتوا قبلاً دانلود شده!**\n\n"
            f"📹 **{title_preview}**{duration_text}\n"
            f"🔢 **{quality_count} کیفیت** در آرشیو موجود است{access_text}\n\n"
            f"🎯 یکی از گزینه‌های زیر را انتخاب کنید:"
        )

        # 3-button keyboard
        kb = get_cache_options_keyboard(quality_count, url_hash)

        # Save URL info in state for later use
        await state.update_data(
            url=text,
            url_hash=url_hash,
            platform=platform,
            normalized_url=normalized_url,
            cached_download_id=cached_download.id,
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
    await state.set_state(DownloadStates.selecting_format_type)

    await message.reply(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard(),
        parse_mode="Markdown"
    )


# ═══════════════════════════════════════════════════════════════════════
# PRO CACHE CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════════════════════

from aiogram.types import CallbackQuery
from aiogram import Bot


@router.callback_query(F.data.startswith("show_cached:"))
async def show_cached_qualities(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """
    Handle 📚 button: Show list of cached qualities for selection.
    Callback format: show_cached:{url_hash}
    """
    try:
        _, url_hash = query.data.split(":", 1)
    except ValueError:
        await query.answer("❌ داده نامعتبر", show_alert=True)
        return

    logger.info(f"[PRO CACHE] Showing qualities for hash: {url_hash[:12]}...")

    try:
        repo = CachedDownloadRepository(session)
        cached_download = await repo.find_valid_by_url_hash(url_hash)

        if not cached_download or not cached_download.qualities:
            await query.answer("❌ کیفیت‌های کش شده یافت نشد", show_alert=True)
            return

        qualities = cached_download.qualities

        # Build caption with quality list
        title = cached_download.title or "بدون عنوان"
        caption = f"📋 **کیفیت‌های موجود در آرشیو**\n\n📹 {title[:60]}\n\n"

        for i, q in enumerate(qualities, 1):
            size_text = f"{q.file_size_mb:.1f} MB" if q.file_size else "نامعلوم"
            caption += f"{i}. **{q.quality_label}** • {size_text} • {q.extension or ''}\n"

        caption += "\n🎯 یک کیفیت را برای دریافت سریع انتخاب کنید:"

        kb = get_cached_qualities_keyboard(qualities, show_back=True)

        # Update state
        await state.update_data(cached_download_id=cached_download.id)
        await state.set_state(DownloadStates.selecting_cached_file)

        await query.message.edit_text(caption, reply_markup=kb, parse_mode="Markdown")
        await query.answer()

    except Exception as e:
        logger.exception(f"[PRO CACHE] Error showing qualities: {e}")
        await query.answer("❌ خطا در بارگذاری کیفیت‌ها", show_alert=True)


@router.callback_query(F.data.startswith("send_cached:"))
async def send_cached_file(
    query: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
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

        # Send via file_id
        try:
            mime = quality.mime_type or ''
            if 'video' in mime:
                await bot.send_video(
                    chat_id=query.from_user.id,
                    video=quality.telegram_file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            elif 'audio' in mime:
                await bot.send_audio(
                    chat_id=query.from_user.id,
                    audio=quality.telegram_file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await bot.send_document(
                    chat_id=query.from_user.id,
                    document=quality.telegram_file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
        except Exception as send_error:
            error_msg = str(send_error)
            logger.warning(f"[PRO CACHE] Send failed (file_id possibly expired): {error_msg}")

            # Mark as invalid if file_id expired
            if "FILE_ID_INVALID" in error_msg or "file_id" in error_msg.lower():
                await repo.mark_invalid(quality.cache_id)
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
        await repo.mark_used(quality.cache_id, quality_id)

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

    # Get URL from state
    data = await state.get_data()
    url = data.get('url')

    if not url:
        await query.answer("❌ لینک یافت نشد. لطفاً دوباره ارسال کنید.", show_alert=True)
        return

    logger.info(f"[PRO CACHE] User requested fresh download for: {url[:60]}...")

    # Move to normal download flow
    await state.set_state(DownloadStates.selecting_format_type)

    await query.message.edit_text(
        "🔄 **جستجوی کیفیت‌های جدید**\n\n"
        "⏳ در حال انتقال به بخش دانلود...",
        reply_markup=get_format_type_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_cache_options")
async def back_to_cache_options(query: CallbackQuery, state: FSMContext):
    """
    Handle ◀️ back button from quality list → return to 3-button options.
    """
    data = await state.get_data()
    url_hash = data.get('url_hash')
    cached_download_id = data.get('cached_download_id')

    if not url_hash:
        await query.answer("❌ اطلاعات کش یافت نشد", show_alert=True)
        return

    try:
        # Get quality count
        from sqlalchemy import select, func
        quality_count_result = await query.bot.session.execute(
            select(func.count(CachedQuality.id)).where(
                CachedQuality.cache_id == cached_download_id
            )
        ) if cached_download_id else None

        quality_count = quality_count_result.scalar() if quality_count_result else 0

        kb = get_cache_options_keyboard(quality_count, url_hash)
        await state.set_state(DownloadStates.viewing_cached_files)
        title = data.get('title', '')
        await query.message.edit_text(
            f"✅ **این محتوا قبلاً دانلود شده!**\n\n"
            f"🔢 **{quality_count} کیفیت** در آرشیو موجود است\n\n"
            f"🎯 یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        await query.answer()
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
    await query.answer()


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
    await query.answer()


# ═══════════════════════════════════════════════════════════════════════
# LEGACY: use_cached handler (kept for backward compat)
# ═══════════════════════════════════════════════════════════════════════

@router.callback_query(
    DownloadStates.viewing_cached_files,
    F.data.startswith("use_cached:")
)
async def use_cached_file_legacy(
    query: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
):
    """
    Legacy handler: Send a previously cached Telegram file_id.
    Kept for backward compatibility with old cached_downloads format.
    """
    try:
        _, id_str = query.data.split(":", 1)
        quality_id = int(id_str)

        # Try to load as CachedQuality first (new format)
        quality = await session.get(CachedQuality, quality_id)
        if quality:
            # Use the new send logic by redirecting callback data
            query.data = f"send_cached:{quality_id}"
            await send_cached_file(query, state, session, bot)
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
        await send_cached_file(query, state, session, bot)

    except Exception as e:
        logger.exception(f"[LEGACY CACHE] Error: {e}")
        await query.answer("❌ خطا داخلی", show_alert=True)


__all__ = ["router"]
