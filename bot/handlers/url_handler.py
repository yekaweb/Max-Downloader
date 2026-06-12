"""URL entrypoint and download menu routing."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.handlers.session import get_session, clear_session
from bot.states.download import DownloadStates
from bot.keyboards.inline import download_platform_kb, main_menu_kb
from bot.keyboards.inline.download import get_format_type_keyboard
from utils.validators import is_valid_url

router = Router()


@router.message(Command("download"))
async def cmd_download(message: Message, state: FSMContext):
    """Handle /download command and begin the download flow."""
    await state.set_state(DownloadStates.waiting_for_url)
    await message.answer(
        "🎬 <b>لطفاً لینک فایل را ارسال کنید:</b>\n\n"
        "پشتیبانی شده:\n"
        "✅ YouTube\n"
        "✅ Instagram\n"
        "✅ Twitter / X\n"
        "✅ TikTok\n",
        reply_markup=download_platform_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "download_menu")
async def download_menu(callback: CallbackQuery, state: FSMContext):
    """Handle the main menu "دانلود ویدیو" button."""
    await callback.answer()
    await state.set_state(DownloadStates.waiting_for_url)
    await callback.message.edit_text(
        "🎬 <b>لطفاً لینک فایل را ارسال کنید:</b>\n\n"
        "پشتیبانی شده:\n"
        "✅ YouTube\n"
        "✅ Instagram\n"
        "✅ Twitter / X\n"
        "✅ TikTok\n",
        parse_mode="HTML",
        reply_markup=download_platform_kb(),
    )


@router.callback_query(F.data == "platform_youtube")
async def handle_platform_youtube(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DownloadStates.waiting_for_url)
    await callback.message.edit_text(
        "🎥 <b>لطفاً لینک ویدیوی YouTube را ارسال کنید:</b>\n\n"
        "مثال: https://youtu.be/... یا https://youtube.com/watch?v=...",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "platform_instagram")
async def handle_platform_instagram(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DownloadStates.waiting_for_url)
    await callback.message.edit_text(
        "📸 <b>لطفاً لینک Instagram را ارسال کنید:</b>\n\n"
        "مثال: https://instagram.com/p/... یا https://instagram.com/reel/...",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "platform_twitter")
async def handle_platform_twitter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DownloadStates.waiting_for_url)
    await callback.message.edit_text(
        "🐦 <b>لطفاً لینک Twitter / X را ارسال کنید:</b>\n\n"
        "مثال: https://twitter.com/... یا https://x.com/...",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_prev")
async def handle_back_prev(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🤖 <b>سلام به DLBot!</b>\n\n"
        "دانلود‌کننده حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter/X\n"
        "• 🎵 TikTok\n\n"
        "برای شروع، یک لینک ارسال کنید یا یکی از گزینه‌ها را انتخاب کنید:",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.message(DownloadStates.waiting_for_url)
async def handle_url_submission(message: Message, state: FSMContext):
    """Validate the user URL and advance to format selection."""
    url = (message.text or "").strip()

    if not is_valid_url(url):
        await message.reply(
            "❌ <b>لینک نامعتبر است!</b>\n\n"
            "لطفاً یک لینک معتبر شامل http:// یا https:// ارسال کنید.",
            parse_mode="HTML",
        )
        return

    session_data = get_session(message.from_user.id)
    session_data["url"] = url
    session_data["format_type"] = None
    session_data["quality"] = None
    session_data["codec"] = None
    session_data["subtitle"] = None
    session_data["send_as"] = None

    await state.set_state(DownloadStates.selecting_format_type)
    await message.answer(
        "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>\n\n"
        "• 🎬 ویدیو - دانلود با کیفیت انتخابی\n"
        "• 🎵 صدا - فقط صوت را استخراج کنید",
        reply_markup=get_format_type_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "cancel_download")
async def cancel_download(query: CallbackQuery, state: FSMContext):
    """Cancel the download flow and clear temporary session state."""
    await query.answer("❌ عملیات لغو شد", show_alert=False)
    clear_session(query.from_user.id)
    await state.clear()
    await query.message.delete()
    await query.message.answer("❌ عملیات دانلود لغو شد.")
