"""Menu handler: Routes reply keyboard button clicks to their respective commands"""
from aiogram import Router, F
from aiogram.types import Message

# Import command handlers directly to call them
from bot.handlers.profile import show_profile
from bot.handlers.plans import show_plans
from bot.handlers.referral import show_referral
from bot.handlers.history import show_history
from bot.handlers.help import show_help
from bot.handlers.admin_panel import admin_panel

router = Router()

# Register imported handlers directly with text filters
router.message(F.text == "👤 پروفایل من")(show_profile)
router.message(F.text == "💳 خرید اشتراک / سکه")(show_plans)
router.message(F.text == "👥 معرفی به دوستان")(show_referral)
router.message(F.text == "📊 تاریخچه دانلودها")(show_history)
router.message(F.text == "🆘 راهنما / پشتیبانی")(show_help)
router.message(F.text == "🛠 پنل مدیریت (Admin)")(admin_panel)

@router.message(F.text == "📥 دانلود جدید (ارسال لینک)")
async def menu_download(message: Message, **kwargs):
    await message.reply("لینک ویدیو یا آهنگ خود را (از یوتیوب، اینستاگرام، تیک‌تاک و...) ارسال کنید تا دانلود شروع شود 📥")

@router.message(F.text == "⚙️ تنظیمات")
async def menu_settings(message: Message, **kwargs):
    await message.reply("بخش تنظیمات به زودی اضافه خواهد شد ⚙️")

__all__ = ["router"]
