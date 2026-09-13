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


__all__ = ["router", "admin_panel"]


