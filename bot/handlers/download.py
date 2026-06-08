"""Download handler: entry point for the download FSM flow with CACHING (Phase 1).

This handler validates the URL, resolves a downloader via the module
registry, checks cache for previously uploaded files, and then pushes 
the user into the `SELECTING_FORMAT_TYPE` state with the URL stored in FSM data.

### PHASE 1: Caching System
- Check if URL was downloaded before
- If yes: Send cached file (0.5 seconds) ✨
- If no: Start normal download flow
"""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.download import DownloadStates
from bot.keyboards.inline.download import get_format_type_keyboard
from services import DownloadService
from modules import get_downloader, get_all_downloaders
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database.repositories.cached_download_repo import CachedDownloadRepository
from services.comprehensive_cache_service import CacheService
import logging

logger = logging.getLogger(__name__)

router = Router()

# Initialize cache service
cache_service = CacheService()


@router.message()
async def handle_url(message: types.Message, state: FSMContext, session: AsyncSession):
    """
    Handle incoming URL and start download FSM.
    
    PHASE 1 ENHANCEMENT: 
    - Validates URL
    - ✨ NEW: Checks cache first (99% faster!)
    - Resolves a downloader via modules.get_downloader
    - Sends a friendly error if no handler found
    - Saves URL in FSM and asks user to select format type

    Args:
        message: Telegram message
        state: FSM state context
        session: Database session for cache check

    Returns:
        None (sends message to user)
    """
    text = (message.text or "").strip()
    
    # 1. Validate URL format
    if not text or not text.startswith("http"):
        await message.reply("❌ لطفاً یک لینک معتبر ارسال کنید")
        return

    # 2. ✨ PHASE 1: Check cache FIRST (before any download)
    logger.info(f"[CACHE] Checking cache for URL: {text[:60]}...")
    try:
        cached_repo = CachedDownloadRepository(session)
        cached_list = await cached_repo.find_valid_by_url(text)
        
        if cached_list:
            logger.info(f"[CACHE HIT] Found {len(cached_list)} cached version(s)")
    except SQLAlchemyError as e:
        logger.warning(f"[CACHE] Database error: {e}")
        cached_list = []

    # 3. If cache found, show cached options
    if cached_list:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        kb = InlineKeyboardMarkup(inline_keyboard=[])
        for c in cached_list:
            size_mb = c.file_size / (1024 * 1024)
            label = f"📦 {c.quality} • {size_mb:.1f} MB"
            kb.inline_keyboard.append([
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"use_cached:{c.id}"
                )
            ])

        # Add option for fresh download
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="🔄 دانلود جدید", callback_data="fresh_search")
        ])

        await state.update_data(
            url=text,
            cached_ids=[c.id for c in cached_list]
        )
        await state.set_state(DownloadStates.viewing_cached_files)

        title_preview = cached_list[0].media_title[:80] + (
            "..." if len(cached_list[0].media_title) > 80 else ""
        )
        
        await message.reply(
            f"✨ **فایل کش‌شده پیدا شد!**\n\n"
            f"📹 {title_preview}\n"
            f"⏱️ بدون نیاز به دانلود دوباره (0.5 ثانیه!)\n\n"
            f"🎯 یکی رو انتخاب کنید یا دانلود جدید:",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        return

    # 4. Not in cache, resolve handler
    handler = get_downloader(text)
    if handler is None:
        # Build supported platforms list
        all_dl = get_all_downloaders()
        platforms = ", ".join(sorted(all_dl.keys())) or "هیچ ماژولی نصب نشده"
        logger.warning(f"[HANDLER] No downloader for URL: {text[:60]}")
        await message.reply(
            f"❌ **این پلتفرم پشتیبانی نمی‌شود**\n\n"
            f"پلتفرم‌های پشتیبانی‌شده:\n"
            f"{platforms}",
            parse_mode="Markdown"
        )
        return

    logger.info(f"[HANDLER] Using {handler.__class__.__name__} for URL: {text[:60]}")

    # 5. Save URL in FSM and move to format selection
    await state.update_data(url=text, handler_name=handler.__class__.__name__)
    await state.set_state(DownloadStates.selecting_format_type)

    await message.reply(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard(),
        parse_mode="Markdown"
    )


# -------------------- Cached-file actions --------------------
from aiogram import F
from aiogram.types import CallbackQuery
from database.models.cached_download import CachedDownload


@router.callback_query(DownloadStates.viewing_cached_files, F.data.startswith("use_cached:"))
async def use_cached_file(query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Send a previously cached Telegram file_id to the user without re-downloading."""
    try:
        _, id_str = query.data.split(":", 1)
        cached_id = int(id_str)

        # Load cached entry
        cd: CachedDownload | None = await session.get(CachedDownload, cached_id)
        if not cd:
            await query.answer("❌ فایل کش‌شده پیدا نشد", show_alert=True)
            return

        # Send cached file by file_id
        caption = f"📦 ارسال فایل کش‌شده:\n{cd.media_title[:80]}\n{cd.quality} • {cd.file_size/1024/1024:.1f} MB"
        try:
            await query.message.reply_document(cd.telegram_file_id, caption=caption)
        except Exception as e:
            logger.exception(e)
            # If sending the cached file failed (file_id expired or invalid), mark cache invalid
            try:
                repo = CachedDownloadRepository(session)
                await repo.mark_invalid(cd.id)
            except Exception:
                pass
            await query.answer("❌ خطا در ارسال فایل کش‌شده — رکورد کش غیرفعال شد", show_alert=True)
            return

        # Mark cached entry as used
        try:
            repo = CachedDownloadRepository(session)
            await repo.mark_used(cached_id)
        except Exception:
            pass

        await state.clear()
        await query.answer("✅ فایل ارسال شد")

    except Exception as e:
        logger.exception(e)
        await query.answer("❌ خطا داخلی", show_alert=True)


@router.callback_query(DownloadStates.viewing_cached_files, F.data == "fresh_search")
async def fresh_search_callback(query: CallbackQuery, state: FSMContext):
    """User requested a fresh search — continue normal download flow."""
    # Move user to format selection to proceed with fresh download
    await state.set_state(DownloadStates.selecting_format_type)
    await query.message.edit_text(
        "🎯 نوع فایل دریافتی را انتخاب کنید:",
        reply_markup=get_format_type_keyboard()
    )
    await query.answer()


__all__ = ["router"]
