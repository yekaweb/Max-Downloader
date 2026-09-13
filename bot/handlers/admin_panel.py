"""
Admin Panel Handler – Max Youtube Downloader
A standalone admin handler with full management capabilities.
Separated from download_handler.py for clean architecture.
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import settings

logger = logging.getLogger(__name__)
router = Router()


def _admin_main_keyboard() -> InlineKeyboardMarkup:
    """منوی اصلی ادمین"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار کلی ربات", callback_data="adm_stats")],
        [
            InlineKeyboardButton(text="👥 مدیریت ادمین‌ها", callback_data="adm_manage_admins"),
            InlineKeyboardButton(text="👤 مدیریت کاربران", callback_data="adm_manage_users"),
        ],
        [
            InlineKeyboardButton(text="💳 تنظیمات زرین‌پال", callback_data="adm_zarinpal"),
            InlineKeyboardButton(text="🪙 درگاه ارز دیجیتال", callback_data="adm_crypto"),
        ],
        [InlineKeyboardButton(text="🔌 مدیریت پلاگین‌ها", callback_data="adm_plugins")],
        [InlineKeyboardButton(text="📢 ارسال پیام همگانی", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="🌐 ورود به پنل وب", url=settings.admin_panel_url)],
    ])


@router.message(Command("admin"))
async def admin_panel(message: Message, **kwargs):
    """هندلر دستور /admin — فقط برای ادمین‌ها"""
    user_id = message.from_user.id

    if user_id not in settings.ADMIN_IDS_LIST:
        await message.answer("❌ شما دسترسی ادمین ندارید.")
        return

    await message.answer(
        f"⚙️ **پنل مدیریت – Max Youtube Downloader**\n\n"
        f"👋 سلام مدیر **{message.from_user.first_name}**!\n\n"
        f"از منوی زیر یک بخش را انتخاب کنید:",
        reply_markup=_admin_main_keyboard(),
        parse_mode="Markdown",
    )

@router.callback_query(F.data == "open_admin_panel")
async def admin_panel_callback(query: CallbackQuery):
    """هندلر دکمه مدیریت در منوی شیشه‌ای"""
    user_id = query.from_user.id

    if user_id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ شما دسترسی ادمین ندارید.", show_alert=True)
        return

    await query.message.edit_text(
        f"⚙️ **پنل مدیریت – Max Youtube Downloader**\n\n"
        f"👋 سلام مدیر **{query.from_user.first_name}**!\n\n"
        f"از منوی زیر یک بخش را انتخاب کنید:",
        reply_markup=_admin_main_keyboard(),
        parse_mode="Markdown",
    )


# ─── Callback: آمار ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_stats")
async def cb_stats(query: CallbackQuery, **kwargs):
    """نمایش آمار سریع از دیتابیس"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return

    try:
        from database.connection import AsyncSessionLocal
        from database.repositories import UserRepository, DownloadRepository

        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            dl_repo = DownloadRepository(session)

            total_users = await user_repo.count_all()
            total_downloads = await dl_repo.count_all()

        text = (
            "📊 **آمار کلی ربات**\n\n"
            f"👥 کاربران: `{total_users}`\n"
            f"📥 دانلودها: `{total_downloads}`\n\n"
            "برای جزئیات بیشتر به پنل وب مراجعه کنید."
        )
    except Exception as e:
        logger.error(f"[ADMIN STATS] {e}")
        text = "⚠️ خطا در دریافت آمار. لطفاً پنل وب را بررسی کنید."

    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_back_main")]
    ])
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    try:
        await query.answer()
    except Exception:
        pass


# ─── Callback: مدیریت ادمین‌ها ───────────────────────────────────────────────

@router.callback_query(F.data == "adm_manage_admins")
async def cb_manage_admins(query: CallbackQuery, **kwargs):
    """نمایش لیست ادمین‌ها + دکمه اضافه/حذف"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return

    admin_list = "\n".join([f"• `{aid}`" for aid in settings.ADMIN_IDS_LIST])

    text = (
        "👥 **مدیریت ادمین‌ها**\n\n"
        f"**ادمین‌های فعلی:**\n{admin_list}\n\n"
        "برای اضافه/حذف ادمین، مقدار `ADMIN_IDS` را در فایل `.env` روی سرور ویرایش کنید:\n"
        "```\nADMIN_IDS=123456789,987654321\n```\n"
        "سپس ربات را ری‌استارت کنید."
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_back_main")]
    ])
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    try:
        await query.answer()
    except Exception:
        pass


# ─── Callback: زرین‌پال ───────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_zarinpal")
async def cb_zarinpal(query: CallbackQuery, **kwargs):
    """نمایش وضعیت و راهنمای تنظیم زرین‌پال"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return

    merchant = settings.ZARINPAL_MERCHANT
    status = "✅ تنظیم شده" if merchant else "❌ تنظیم نشده"
    masked = f"`{merchant[:8]}...`" if merchant else "—"

    text = (
        "💳 **تنظیمات زرین‌پال**\n\n"
        f"وضعیت: {status}\n"
        f"Merchant ID: {masked}\n\n"
        "برای تغییر، مقدار `ZARINPAL_MERCHANT` را در فایل `.env` روی سرور ویرایش کنید:\n"
        "```\nZARINPAL_MERCHANT=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx\n```\n"
        "سپس ربات را ری‌استارت کنید."
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_back_main")]
    ])
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    try:
        await query.answer()
    except Exception:
        pass


# ─── Callback: درگاه ارز دیجیتال ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_crypto")
async def cb_crypto(query: CallbackQuery, **kwargs):
    """نمایش وضعیت درگاه‌های ارز دیجیتال"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return

    cp = settings.CRYPTOPAY_TOKEN
    np = settings.NOWPAYMENTS_KEY

    text = (
        "🪙 **درگاه ارز دیجیتال**\n\n"
        f"CryptoPay Token: {'✅ تنظیم شده' if cp else '❌ تنظیم نشده'}\n"
        f"NowPayments Key: {'✅ تنظیم شده' if np else '❌ تنظیم نشده'}\n\n"
        "برای تنظیم، مقادیر زیر را در فایل `.env` روی سرور اضافه کنید:\n"
        "```\nCRYPTOPAY_TOKEN=your_token\nNOWPAYMENTS_KEY=your_key\n```"
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_back_main")]
    ])
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    try:
        await query.answer()
    except Exception:
        pass


# ─── Callback: پلاگین‌ها ──────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_plugins")
async def cb_plugins(query: CallbackQuery, **kwargs):
    """نمایش وضعیت پلاگین‌ها"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return

    text = (
        "🔌 **وضعیت پلاگین‌ها / ماژول‌ها**\n\n"
        f"🎥 YouTube: ✅ فعال\n"
        f"📸 Instagram: ✅ فعال\n"
        f"🎵 TikTok: ✅ فعال\n"
        f"🐦 Twitter/X: ✅ فعال\n"
        f"🔗 Direct Link: ✅ فعال\n\n"
        "برای فعال/غیرفعال کردن پلاگین‌ها به پنل وب مراجعه کنید."
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 پنل وب", url=settings.admin_panel_url)],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_back_main")],
    ])
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    try:
        await query.answer()
    except Exception:
        pass


# ─── Callback: بازگشت به منوی اصلی ادمین ────────────────────────────────────

@router.callback_query(F.data == "adm_back_main")
async def cb_back_main(query: CallbackQuery, **kwargs):
    """بازگشت به منوی اصلی ادمین"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return

    await query.message.edit_text(
        f"⚙️ **پنل مدیریت – Max Youtube Downloader**\n\n"
        f"از منوی زیر یک بخش را انتخاب کنید:",
        reply_markup=_admin_main_keyboard(),
        parse_mode="Markdown",
    )
    try:
        await query.answer()
    except Exception:
        pass


# ─── Callback: Broadcast ─────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_broadcast")
async def cb_broadcast(query: CallbackQuery, **kwargs):
    """هدایت به دستور broadcast"""
    if query.from_user.id not in settings.ADMIN_IDS_LIST:
        await query.answer("❌ دسترسی رد شد", show_alert=True)
        return
    await query.message.answer(
        "📢 برای ارسال پیام همگانی، از دستور /broadcast استفاده کنید."
    )


# ─── Commands: مدیریت سشن و کوکی اینستاگرام ─────────────────────────────────

@router.message(Command("set_ig_cookie"))
async def cmd_set_ig_cookie(message: Message, **kwargs):
    """ثبت یا به‌روزرسانی کوکی اینستاگرام توسط ادمین"""
    if message.from_user.id not in settings.ADMIN_IDS_LIST:
        await message.answer("❌ شما دسترسی ادمین ندارید.")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer(
            "⚠️ <b>فرمت دستور نامعتبر است!</b>\n\n"
            "لطفاً مقدار <code>sessionid</code> را به شکل زیر ارسال کنید:\n"
            "<code>/set_ig_cookie your_session_id [optional_ds_user_id]</code>\n\n"
            "💡 <b>نحوه دریافت sessionid:</b>\n"
            "۱. در مرورگر وارد سایت instagram.com شوید.\n"
            "۲. کلید F12 را بزنید و به تب <code>Application &gt; Cookies</code> بروید.\n"
            "۳. مقدار کوکی <code>sessionid</code> را کپی کرده و در دستور بالا قرار دهید.",
            parse_mode="HTML",
        )
        return

    session_id = parts[1].strip()
    ds_user_id = parts[2].strip() if len(parts) > 2 else ""

    from services.instagram_service import instagram_service
    success = instagram_service.set_session_id(session_id, ds_user_id)

    if success:
        await message.answer(
            "✅ <b>کوکی اینستاگرام با موفقیت تنظیم و فعال شد!</b>\n\n"
            "ربات اکنون می‌تواند تمامی ریلزها، پست‌ها و استوری‌های اینستاگرام را بدون مشکل لاگین دانلود کند.",
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ خطا در ذخیره‌سازی کوکی اینستاگرام.")


@router.message(Command("ig_status"))
async def cmd_ig_status(message: Message, **kwargs):
    """بررسی وضعیت سشن اینستاگرام"""
    if message.from_user.id not in settings.ADMIN_IDS_LIST:
        await message.answer("❌ شما دسترسی ادمین ندارید.")
        return

    from services.instagram_service import instagram_service
    has_session = instagram_service.has_active_session()

    if has_session:
        await message.answer(
            "✅ <b>سشن اینستاگرام فعال است!</b>\n\n"
            "کوکی و سشن معتبر برای دانلود از اینستاگرام روی سرور تنظیم شده است.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "⚠️ <b>سشن اینستاگرام تنظیم نشده است!</b>\n\n"
            "برای لینک‌های عمومی از موتور پرسرعت بدون لاگین استفاده می‌شود.\n"
            "در صورت نیاز به فعال‌سازی سشن برای پیج‌های خصوصی:\n"
            "<code>/ig_login username password</code> یا <code>/set_ig_cookie sessionid</code>",
            parse_mode="HTML"
        )


@router.message(Command("ig_login"))
async def cmd_ig_login(message: Message, **kwargs):
    """لاگین خودکار با نام کاربری و رمز عبور اینستاگرام توسط ادمین"""
    if message.from_user.id not in settings.ADMIN_IDS_LIST:
        await message.answer("❌ شما دسترسی ادمین ندارید.")
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer(
            "⚠️ <b>فرمت دستور نامعتبر است!</b>\n\n"
            "برای لاگین خودکار، مشخصات اکانت (ترجیحاً اکانت دوم/تستی) را ارسال کنید:\n"
            "<code>/ig_login username password [2fa_code]</code>\n\n"
            "💡 این دستور خودکار لاگین کرده و سشن را در سرور ذخیره می‌کند.",
            parse_mode="HTML",
        )
        return

    username = parts[1].strip()
    password = parts[2].strip()
    code = parts[3].strip() if len(parts) > 3 else None

    loading = await message.answer("⏳ <b>در حال اتصال و لاگین به اینستاگرام...</b>", parse_mode="HTML")

    from services.instagram_service import instagram_service
    import asyncio
    loop = asyncio.get_running_loop()
    success, resp_msg = await loop.run_in_executor(
        None, lambda: instagram_service.login_with_credentials(username, password, code)
    )

    try:
        await loading.delete()
    except Exception:
        pass

    await message.answer(resp_msg, parse_mode="HTML")


# ─── File Upload: دریافت و اعمال مستقیم فایل cookies.txt / JSON ──────────────────

from aiogram import Bot

@router.message(F.document)
async def handle_admin_cookie_file_upload(message: Message, bot: Bot):
    """دریافت مستقیم فایل کوکی (با هر نامی) ارسالی توسط ادمین"""
    if message.from_user.id not in settings.ADMIN_IDS_LIST:
        return

    doc = message.document
    filename = (doc.file_name or "cookies.txt").lower()
    
    loading = await message.reply("📥 <b>در حال پردازش و اعمال فایل کوکی...</b>", parse_mode="HTML")
    try:
        from pathlib import Path
        import json
        import re
        from services.instagram_service import instagram_service
        
        cookie_file = Path("/root/Max-Downloader/cookies.txt")
        temp_dir = Path("/root/Max-Downloader/temp_downloads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / (doc.file_name or "uploaded_cookies.txt")
        
        await message.bot.download(doc, destination=temp_file)
        content = temp_file.read_text(encoding="utf-8", errors="ignore").strip()
        
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass

        if content.startswith("j2cpwd") or "U2FsdGVkX" in content[:40]:
            await loading.edit_text(
                "⚠️ <b>این فایل با پسورد رمزنگاری شده است!</b>\n\n"
                "افزونه Cookie-Editor موقع خروجی گرفتن از شما پسورد خواسته و فایل را قفل کرده است.\n"
                "لطفاً در منوی Export افزونه، تیک پسورد را بردارید یا از گزینه <b>Export > Netscape</b> یا <b>Export > JSON</b> بدون رمز استفاده کنید.",
                parse_mode="HTML"
            )
            return

        session_extracted = None
        ds_user_extracted = None

        # 1. Try JSON parsing
        if content.startswith("[") or content.startswith("{"):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    session_extracted = data.get("sessionid")
                    ds_user_extracted = data.get("ds_user_id")
                elif isinstance(data, list):
                    for c in data:
                        if isinstance(c, dict):
                            if c.get("name") == "sessionid":
                                session_extracted = c.get("value")
                            elif c.get("name") == "ds_user_id":
                                ds_user_extracted = c.get("value")
            except Exception as json_err:
                logger.warning(f"[AdminCookieUpload] JSON parse error: {json_err}")

        # 2. Try Netscape / line-by-line parsing
        if not session_extracted:
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "instagram.com" in line and "sessionid" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        session_extracted = parts[6]
                    elif len(parts) >= 2:
                        session_extracted = parts[-1]
                elif "instagram.com" in line and "ds_user_id" in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        ds_user_extracted = parts[6]
                elif re.match(r"^sessionid[\s:=]+", line, re.IGNORECASE):
                    session_extracted = re.sub(r"^sessionid[\s:=]+", "", line, flags=re.IGNORECASE).strip()

        # 3. Try regex search for raw Instagram session pattern (e.g. 681234567%3A...)
        if not session_extracted:
            raw_match = re.search(r"(\d{6,16}(?:%3A|:)[A-Za-z0-9_%-]+)", content)
            if raw_match:
                session_extracted = raw_match.group(1)

        # 4. If session found, apply to instagram_service
        if session_extracted:
            instagram_service.set_session_id(session_extracted, ds_user_extracted or "")

        # 5. If it looks like Netscape format, also write/replace cookies.txt
        if "instagram.com" in content or "youtube.com" in content or content.startswith("# Netscape"):
            cookie_file.write_text(content, encoding="utf-8")

        if session_extracted:
            await loading.edit_text(
                "✅ <b>کوکی و سشن اینستاگرام با موفقیت فعال شد!</b>\n\n"
                f"📄 فایل: <code>{doc.file_name}</code>\n"
                f"🔑 Session ID: <code>{session_extracted[:15]}...</code>\n\n"
                "🚀 ربات آماده دانلود بدون محدودیت است.",
                parse_mode="HTML"
            )
        else:
            await loading.edit_text(
                "📄 <b>فایل کوکی در سرور ذخیره شد.</b>\n\n"
                f"نام فایل: <code>{doc.file_name}</code>\n"
                "در صورتی که سشن اینستاگرام شناسایی نشد، می‌توانید مستقیم با دستور زیر سشن را ست کنید:\n"
                "<code>/set_ig_cookie sessionid_value</code>",
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"[AdminCookieUpload] Error: {e}", exc_info=True)
        await loading.edit_text(f"❌ خطا در پردازش فایل: {e}", parse_mode="HTML")


__all__ = ["router", "admin_panel"]



