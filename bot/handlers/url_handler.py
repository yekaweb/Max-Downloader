"""URL entrypoint and download menu routing."""

from aiogram import Router, F, Bot
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


from config import settings

@router.callback_query(F.data == "back_prev")
async def handle_back_prev(callback: CallbackQuery):
    await callback.answer()
    
    is_admin = callback.from_user.id in settings.ADMIN_IDS_LIST
    
    await callback.message.edit_text(
        "🤖 <b>سلام به Max Youtube Downloader!</b>\n\n"
        "دانلود‌کننده حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter/X\n"
        "• 🎵 TikTok\n\n"
        "برای شروع، یک لینک ارسال کنید یا یکی از گزینه‌ها را انتخاب کنید:",
        parse_mode="HTML",
        reply_markup=main_menu_kb(is_admin=is_admin),
    )


@router.message(DownloadStates.waiting_for_url)
async def handle_url_submission(message: Message, state: FSMContext):
    """Validate the user URL and advance to format selection or instant Instagram download."""
    url = (message.text or "").strip()

    if not is_valid_url(url):
        await message.reply(
            "❌ <b>لینک نامعتبر است!</b>\n\n"
            "لطفاً یک لینک معتبر شامل http:// یا https:// ارسال کنید.",
            parse_mode="HTML",
        )
        return

    from services.instagram_service import instagram_service
    from bot.handlers.download_exec import handle_instant_instagram_download

    # Check for Instant Instagram Downloader Flow
    if instagram_service.is_instagram_url(url):
        await handle_instant_instagram_download(message, url, state)
        return

    session_data = get_session(message.from_user.id)
    session_data["url"] = url
    session_data["format_type"] = None
    session_data["quality"] = None
    session_data["codec"] = None
    session_data["subtitle"] = None
    session_data["send_as"] = None
    
    # Send loading message
    loading_msg = await message.answer("🔄 <b>در حال دریافت اطلاعات ویدیو...</b>", parse_mode="HTML")
    
    from utils.format_sizes import get_exact_format_sizes
    format_info = await get_exact_format_sizes(url)

    # Delete loading message
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
        clear_session(message.from_user.id)
        await state.clear()
        return

    session_data["format_info"] = format_info

    await state.set_state(DownloadStates.selecting_format_type)
    
    await message.answer(
        "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>\n\n"
        "• 🎬 ویدیو - دانلود با کیفیت انتخابی\n"
        "• 🎵 صدا - فقط صوت را استخراج کنید",
        reply_markup=get_format_type_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text.regexp(r"(https?://)?(www\.)?(instagram\.com|insta\.io)/(p|reel|tv|stories|reels)/[A-Za-z0-9\-_]+"))
async def handle_direct_instagram_link(message: Message, state: FSMContext):
    """Handle direct Instagram URLs sent as regular messages without prior command."""
    url = (message.text or "").strip()
    from bot.handlers.download_exec import handle_instant_instagram_download
    await handle_instant_instagram_download(message, url, state)


@router.message(Command("music", "song"))
async def cmd_music_search(message: Message, state: FSMContext, bot: Bot):
    """
    Direct full music search & 320kbps MP3 downloader with Pro Cache.
    Usage: /music <song name / artist> or /song <song name>
    """
    import hashlib
    import os
    from pathlib import Path
    from aiogram.types import FSInputFile
    from services.music_downloader_service import music_downloader_service
    from database.connection import AsyncSessionLocal
    from database.repositories.cached_download_repo import CachedDownloadRepository

    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.reply(
            "🎵 <b>جستجو و دانلود مستقیم موزیک (320kbps)</b>\n\n"
            "💡 لطفاً نام آهنگ یا خواننده را همراه با دستور ارسال کنید:\n"
            "مثال:\n"
            "<code>/music shadmehr aghili</code>\n"
            "<code>/song billie eilish birds of a feather</code>",
            parse_mode="HTML"
        )
        return

    query_term = args[1].strip()
    clean_norm_key = query_term.lower().strip()
    music_hash = hashlib.sha256(f"music_320_{clean_norm_key}".encode()).hexdigest()

    # 1. Check Pro Cache first (Instant Delivery in 0.1s)
    try:
        async with AsyncSessionLocal() as session:
            repo = CachedDownloadRepository(session)
            cached = await repo.find_valid_by_url_hash(music_hash)
            if cached and cached.qualities:
                cached_file_id = cached.qualities[0].telegram_file_id
                logger.info(f"[MusicCommand] Pro Cache HIT for '{query_term}'! Delivering instantly.")
                await message.reply_audio(
                    audio=cached_file_id,
                    title=cached.title or query_term,
                    performer=cached.uploader or "Music",
                    duration=cached.duration,
                    caption=(
                        f"🎧 <b>نسخه اصلی و استودیویی (320kbps)</b>\n\n"
                        f"🎵 <b>{cached.title or query_term}</b>\n"
                        f"👤 <b>{cached.uploader or 'Music'}</b>\n\n"
                        f"⚡ <i>تحویل آنی از کش ابری تلگرام (۰.۱ ثانیه)</i>\n"
                        f"⚡ <i>@MaxDownloaderBot</i>"
                    ),
                    parse_mode="HTML"
                )
                await repo.mark_used(cached.id, cached.qualities[0].id)
                return
    except Exception as c_lookup_err:
        logger.warning(f"[MusicCommand] Pro Cache lookup error: {c_lookup_err}")

    status_msg = await message.reply(
        f"🔍 <b>در حال جستجو و دریافت نسخه باکیفیت و کامل (320kbps)...</b>\n\n"
        f"🎵 <i>{query_term}</i>\n"
        f"⚡ <i>لطفاً چند لحظه شکیبا باشید...</i>",
        parse_mode="HTML"
    )

    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    f_path = None

    try:
        res = await music_downloader_service.download_track_by_query(
            query=query_term,
            output_dir=temp_dir,
            custom_filename=f"search_{music_hash[:8]}"
        )

        if res and res.get("file_path") and os.path.exists(res["file_path"]):
            f_path = res["file_path"]
            track_title = res.get("title", query_term)
            track_performer = res.get("artist", "Music")
            duration = res.get("duration")

            sent_msg = await message.reply_audio(
                audio=FSInputFile(f_path),
                title=track_title,
                performer=track_performer,
                duration=int(duration) if duration else None,
                caption=(
                    f"🎧 <b>نسخه اصلی و استودیویی (320kbps)</b>\n\n"
                    f"🎵 <b>{track_title}</b>\n"
                    f"👤 <b>{track_performer}</b>\n\n"
                    f"⚡ <i>دانلود شده توسط @MaxDownloaderBot</i>"
                ),
                parse_mode="HTML"
            )
            try:
                await status_msg.delete()
            except Exception:
                pass

            # 2. Save to Pro Cache
            if sent_msg and sent_msg.audio:
                try:
                    async with AsyncSessionLocal() as session:
                        repo = CachedDownloadRepository(session)
                        await repo.create_from_upload(
                            source_url=f"music://{clean_norm_key}",
                            source_platform="music",
                            media_title=track_title,
                            media_duration=int(duration) if duration else None,
                            media_uploader=track_performer,
                            telegram_file_id=sent_msg.audio.file_id,
                            file_size=os.path.getsize(f_path) if os.path.exists(f_path) else 0,
                            file_type="audio/mp3",
                            quality="320kbps",
                            format_codec="mp3",
                            format_container="mp3",
                            url_hash=music_hash,
                        )
                        logger.info(f"[MusicCommand] Pro Cache SAVED for '{query_term}' (hash={music_hash[:8]})")
                except Exception as c_save_err:
                    logger.warning(f"[MusicCommand] Failed to write Pro Cache: {c_save_err}")
            return

        await status_msg.edit_text(
            f"❌ متاسفانه آهنگی با عنوان <b>{query_term}</b> یافت نشد.\n"
            f"💡 لطفاً نام لاتین یا نام دقیق‌تری را امتحان کنید.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.exception(f"[MusicCommand] Error: {e}")
        try:
            await status_msg.edit_text(f"❌ خطا در دانلود موزیک:\n<code>{str(e)[:120]}</code>", parse_mode="HTML")
        except Exception:
            pass
    finally:
        # Guarantee 0-disk footprint: delete file immediately
        if f_path and os.path.exists(f_path):
            try:
                os.remove(f_path)
            except Exception:
                pass


@router.callback_query(F.data == "cancel_download")
async def cancel_download(query: CallbackQuery, state: FSMContext):
    """Cancel the download flow and clear temporary session state."""
    await query.answer("❌ عملیات لغو شد", show_alert=False)
    clear_session(query.from_user.id)
    await state.clear()
    await query.message.delete()
    await query.message.answer("❌ عملیات دانلود لغو شد.")
