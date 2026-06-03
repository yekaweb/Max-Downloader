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


__all__ = ["router"]
