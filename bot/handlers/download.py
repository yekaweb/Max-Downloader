"""Download handler: entry point for the download FSM flow.

This handler validates the URL, resolves a downloader via the module
registry, checks basic preconditions and then pushes the user into the
`SELECTING_FORMAT_TYPE` state with the URL stored in FSM data.
"""

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states.download import DownloadStates
from bot.keyboards.inline.download import get_format_type_keyboard
from services import DownloadService
from modules import get_downloader, get_all_downloaders
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database.repositories.cached_download_repo import CachedDownloadRepository
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message()
async def handle_url(message: types.Message, state: FSMContext, session: AsyncSession):
    """Handle incoming URL and start download FSM.

    - Validates URL
    - Resolves a downloader via modules.get_downloader
    - Sends a friendly error if no handler found (lists supported platforms)
    - Saves URL in FSM and asks user to select format type (video/audio)
    """
    text = (message.text or "").strip()
    if not text or not text.startswith("http"):
        await message.reply("❌ لطفاً یک لینک معتبر ارسال کنید")
        return

    # Resolve handler from module registry
    handler = get_downloader(text)
    if handler is None:
        # Build supported platforms list
        all_dl = get_all_downloaders()
        platforms = ", ".join(sorted(all_dl.keys())) or "هیچ ماژولی نصب نشده"
        await message.reply(
            f"❌ این پلتفرم پشتیبانی نمی‌شود.\nپلتفرم‌های پشتیبانی‌شده: {platforms}")
        return

    # Check cache in DB for previously uploaded Telegram file_id
    try:
        cached_repo = CachedDownloadRepository(session)
        cached_list = await cached_repo.find_valid_by_url(text)
    except SQLAlchemyError:
        cached_list = []

    if cached_list:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        kb = InlineKeyboardMarkup(inline_keyboard=[])
        for c in cached_list:
            size_mb = c.file_size / (1024 * 1024)
            label = f"{c.quality} • {size_mb:.1f} MB"
            kb.inline_keyboard.append([InlineKeyboardButton(text=label, callback_data=f"use_cached:{c.id}")])

        kb.inline_keyboard.append([InlineKeyboardButton(text="🔄 Fresh Search", callback_data="fresh_search")])

        await state.update_data(url=text, handler_name=handler.__class__.__name__, cached_ids=[c.id for c in cached_list])
        await state.set_state(DownloadStates.viewing_cached_files)

        await message.reply(
            f"📦 فایل(های) کش‌شده برای این لینک پیدا شد:\n{cached_list[0].media_title[:80]}",
            reply_markup=kb,
        )
        return

    # Save URL and resolved handler name in FSM and move to format selection
    await state.update_data(url=text, handler_name=handler.__class__.__name__)
    await state.set_state(DownloadStates.selecting_format_type)

    await message.reply(
        "🎯 نوع فایل دریافتی را انتخاب کنید:",
        reply_markup=get_format_type_keyboard()
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
