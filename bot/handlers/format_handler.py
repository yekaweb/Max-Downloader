"""Handlers for format selection and transition to download execution."""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.session import get_session
from bot.states.download import DownloadStates
from bot.keyboards.inline.download import (
    get_format_type_keyboard,
    get_video_quality_keyboard,
    get_video_codec_keyboard,
    get_subtitle_keyboard,
    get_send_as_keyboard,
    get_audio_format_keyboard,
)
from bot.handlers.download_exec import start_download

router = Router()


@router.callback_query(DownloadStates.selecting_format_type)
async def select_format_type(query: CallbackQuery, state: FSMContext):
    """Handle the user selection between video and audio."""
    await query.answer()

    if query.data == "cancel_download":
        await query.message.delete()
        await query.message.answer("❌ عملیات دانلود لغو شد.")
        await state.clear()
        return

    session_data = get_session(query.from_user.id)
    format_info = session_data.get("format_info", {})
    codec_sizes = format_info.get("codec_sizes", {}) if format_info else None

    if query.data == "format_video":
        session_data["format_type"] = "video"
        await query.message.edit_text(
            "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>\n\n"
            "• H.264 | MP4 ✅ سازگار با همه دستگاه‌ها\n"
            "• AV1 | WebM 🏆 بهترین کیفیت/حجم\n"
            "• VP9 | WebM ⚡ سبک و کارآمد\n",
            reply_markup=get_video_codec_keyboard(codec_sizes),
            parse_mode="HTML",
        )
        await state.set_state(DownloadStates.video_codec_selection)

    elif query.data == "format_audio":
        session_data["format_type"] = "audio"
        await query.message.edit_text(
            "🎵 <b>فرمت صوتی را انتخاب کنید:</b>",
            reply_markup=get_audio_format_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(DownloadStates.audio_format_selection)


@router.callback_query(DownloadStates.video_codec_selection)
async def select_video_codec(query: CallbackQuery, state: FSMContext):
    """Handle video codec selection and show quality options."""
    await query.answer()

    if query.data == "back_to_format":
        await query.message.edit_text(
            "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>",
            reply_markup=get_format_type_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(DownloadStates.selecting_format_type)
        return

    codec_map = {
        "codec_h264": "h264",
        "codec_av1": "av1",
        "codec_vp9": "vp9",
    }
    codec = codec_map.get(query.data)
    if not codec:
        await query.answer("❌ انتخاب نامعتبر", show_alert=True)
        return

    session_data = get_session(query.from_user.id)
    session_data["codec"] = codec
    
    format_info = session_data.get("format_info", {})
    video_formats = format_info.get("video_formats", {}) if format_info else None

    await query.message.edit_text(
        "📺 <b>کیفیت ویدیو را انتخاب کنید:</b>",
        reply_markup=get_video_quality_keyboard(video_formats),
        parse_mode="HTML",
    )
    await state.set_state(DownloadStates.video_quality_selection)


@router.callback_query(DownloadStates.video_quality_selection)
async def select_video_quality(query: CallbackQuery, state: FSMContext):
    """Handle video quality selection and proceed to subtitle choice."""
    await query.answer()

    session_data = get_session(query.from_user.id)
    format_info = session_data.get("format_info", {})
    codec_sizes = format_info.get("codec_sizes", {}) if format_info else None

    if query.data == "back_to_codec":
        await query.message.edit_text(
            "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>",
            reply_markup=get_video_codec_keyboard(codec_sizes),
            parse_mode="HTML",
        )
        await state.set_state(DownloadStates.video_codec_selection)
        return

    if not query.data.startswith("quality_"):
        await query.answer("❌ انتخاب نامعتبر", show_alert=True)
        return

    quality_key = query.data.replace("quality_", "")
    session_data = get_session(query.from_user.id)
    session_data["quality"] = quality_key

    await query.message.edit_text(
        "📝 <b>زیرنویس می‌خواهید؟</b>",
        reply_markup=get_subtitle_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(DownloadStates.video_selecting_subtitle)


@router.callback_query(DownloadStates.video_selecting_subtitle)
async def select_subtitle(query: CallbackQuery, state: FSMContext):
    """Handle subtitle selection and advance to send-as choice."""
    await query.answer()

    if query.data == "back_to_codec":
        await query.message.edit_text(
            "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>",
            reply_markup=get_video_codec_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(DownloadStates.video_codec_selection)
        return

    session_data = get_session(query.from_user.id)
    session_data["subtitle"] = query.data.replace("sub_", "")

    await query.message.edit_text(
        "📤 <b>نحوه دریافت فایل را انتخاب کنید:</b>",
        reply_markup=get_send_as_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(DownloadStates.video_selecting_send_as)


@router.callback_query(DownloadStates.video_selecting_send_as)
async def select_send_as(query: CallbackQuery, state: FSMContext):
    """Handle send-as selection and begin the download execution."""
    await query.answer()

    if query.data == "back_to_subtitle":
        await query.message.edit_text(
            "📝 <b>زیرنویس می‌خواهید؟</b>",
            reply_markup=get_subtitle_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(DownloadStates.video_selecting_subtitle)
        return

    send_as_map = {
        "send_as_video": "video",
        "send_as_file": "file",
    }
    send_as = send_as_map.get(query.data)
    if not send_as:
        await query.answer("❌ گزینه نامعتبر", show_alert=True)
        return

    session_data = get_session(query.from_user.id)
    session_data["send_as"] = send_as
    await state.set_state(DownloadStates.downloading)
    await start_download(query.message, query.from_user.id, state)


@router.callback_query(DownloadStates.audio_format_selection)
async def select_audio_format(query: CallbackQuery, state: FSMContext):
    """Handle audio format selection and start audio download."""
    await query.answer()

    audio_map = {
        "audio_mp3_320": {"format": "mp3", "bitrate": "320"},
        "audio_mp3_128": {"format": "mp3", "bitrate": "128"},
        "audio_aac_256": {"format": "aac", "bitrate": "256"},
        "audio_m4a_128": {"format": "m4a", "bitrate": "128"},
        "audio_opus": {"format": "opus", "bitrate": "128"},
    }

    audio_data = audio_map.get(query.data)
    if not audio_data:
        await query.answer("❌ فرمت نامعتبر", show_alert=True)
        return

    session_data = get_session(query.from_user.id)
    session_data["audio_format"] = audio_data

    await state.set_state(DownloadStates.downloading)
    await start_download(query.message, query.from_user.id, state)


@router.callback_query(F.data == "back_to_format")
async def back_to_format(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(DownloadStates.selecting_format_type)
    await query.message.edit_text(
        "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>",
        reply_markup=get_format_type_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_codec")
async def back_to_codec(query: CallbackQuery, state: FSMContext):
    await query.answer()
    session_data = get_session(query.from_user.id)
    format_info = session_data.get("format_info", {})
    codec_sizes = format_info.get("codec_sizes", {}) if format_info else None
    await state.set_state(DownloadStates.video_codec_selection)
    await query.message.edit_text(
        "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>",
        reply_markup=get_video_codec_keyboard(codec_sizes),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_quality")
async def back_to_quality(query: CallbackQuery, state: FSMContext):
    await query.answer()
    session_data = get_session(query.from_user.id)
    format_info = session_data.get("format_info", {})
    video_formats = format_info.get("video_formats", {}) if format_info else None
    await state.set_state(DownloadStates.video_quality_selection)
    await query.message.edit_text(
        "📺 <b>کیفیت ویدیو را انتخاب کنید:</b>",
        reply_markup=get_video_quality_keyboard(video_formats),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_subtitle")
async def back_to_subtitle(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(DownloadStates.video_selecting_subtitle)
    await query.message.edit_text(
        "📝 <b>زیرنویس می‌خواهید؟</b>",
        reply_markup=get_subtitle_keyboard(),
        parse_mode="HTML",
    )
