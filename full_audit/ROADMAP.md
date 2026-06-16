# 🗺️ نقشه راه اصلاحات جامع – Max Youtube Downloader

**تاریخ ایجاد:** ۲۶ خرداد ۱۴۰۵  
**مرجع:** [FULL_AUDIT_REPORT.md](../FULL_AUDIT_REPORT.md)  
**تعداد فازها:** ۵ فاز  
**مجموع تسک‌ها:** ۲۸ تسک  

---

## 📊 راهنمای وضعیت

| نماد | وضعیت |
|------|-------|
| ⬜ | انجام نشده |
| 🔄 | در حال انجام |
| ✅ | تکمیل شده |
| ⏭️ | رد شده / منتقل شده |

---

## 🔴 فاز ۱: رفع باگ‌های بحرانی (اولویت: حیاتی)

> **زمان تخمینی:** ۲-۳ ساعت  
> **هدف:** ربات باید بدون خطا استارت بخورد، دکمه‌ها کار کنند، ادمین شناسایی شود.  
> **وضعیت کلی فاز:** ⬜ انجام نشده

---

### تسک ۱.۱: یکسان‌سازی سیستم تنظیمات ⬜

**باگ مرتبط:** BUG-01  
**مشکل:** دو فایل `config.py` و `config_simple.py` هم‌زمان وجود دارند و فایل‌های مختلف از هر کدام ایمپورت می‌کنند.

**فایل‌های نیازمند اصلاح:**

| # | فایل | تغییر | وضعیت |
|---|------|-------|-------|
| 1 | `bot/handlers/download_handler.py` خط ۸ | `from config_simple import settings` → `from config import settings` | ⬜ |
| 2 | `bot/filters/admin.py` خط ۴ | `from config_simple import settings` → `from config import settings` | ⬜ |
| 3 | `web/app.py` خط ۸ | `from config_simple import settings` → `from config import settings` | ⬜ |
| 4 | `web/auth.py` خط ۱۱ | `from config_simple import settings` → `from config import settings` | ⬜ |
| 5 | `tasks/cache_cleanup_tasks.py` خط ۱۳ | `from config_simple import settings` → `from config import settings` | ⬜ |
| 6 | حذف فایل `config_simple.py` | فایل را به پوشه `archive/` منتقل کنید | ⬜ |

**راه حل دقیق:**
```diff
# در هر فایل بالا:
- from config_simple import settings
+ from config import settings
```

**نکته مهم:** بعد از این تغییر، در فایل‌هایی که از `settings.ADMIN_IDS` به صورت string استفاده می‌کنند (مثلاً `settings.ADMIN_IDS.split(",")`)، باید از `settings.ADMIN_IDS_LIST` استفاده شود چون در `config.py` متغیر `ADMIN_IDS` نوع `str` دارد.

---

### تسک ۱.۲: اصلاح بررسی ادمین بودن کاربر ⬜

**باگ مرتبط:** BUG-02  
**مشکل:** `str(user_id) in settings.ADMIN_IDS` عملیات substring match انجام می‌دهد (ناامن).

**فایل‌های نیازمند اصلاح:**

| # | فایل | خط | تغییر | وضعیت |
|---|------|-----|-------|-------|
| 1 | `bot/handlers/start.py` | ۴۳ | `str(user_id) in settings.ADMIN_IDS` → `user_id in settings.ADMIN_IDS_LIST` | ⬜ |
| 2 | `bot/handlers/download_handler.py` | ۱۹۳ | `admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",")...]` → `admin_ids = settings.ADMIN_IDS_LIST` | ⬜ |
| 3 | `bot/filters/admin.py` | ۹ | بعد از تسک ۱.۱ بررسی شود | ⬜ |

**راه حل دقیق:**

```diff
# در start.py خط ۴۳:
- if str(user_id) in settings.ADMIN_IDS:
+ if user_id in settings.ADMIN_IDS_LIST:

# در download_handler.py خط ۱۹۳:
- admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
- if user_id not in admin_ids:
+ if user_id not in settings.ADMIN_IDS_LIST:
```

---

### تسک ۱.۳: فعال‌سازی سیستم واقعی دانلود ⬜

**باگ مرتبط:** DL-01  
**مشکل:** فایل `download.py` (سیستم واقعی با yt-dlp و Pro Cache) در لیست روترها ثبت نشده.

**فایل‌های نیازمند اصلاح:**

| # | فایل | تغییر | وضعیت |
|---|------|-------|-------|
| 1 | `bot/handlers/download.py` خط ۴۳ | فیلتر URL اضافه شود | ⬜ |
| 2 | `bot/handlers/__init__.py` | ایمپورت و ثبت `download_router` | ⬜ |

**راه حل دقیق:**

```diff
# در download.py خط ۴۳:
- @router.message()
+ @router.message(F.text.startswith("http"))
  async def handle_url(message: types.Message, state: FSMContext, session: AsyncSession):
```

```diff
# در __init__.py:
  from .channels import router as channels_router
  from .menu import router as menu_router
+ from .download import router as download_flow_router
  from .errors import router as errors_router

  routers = [
      start_router,
      url_router,
      ...
      menu_router,
+     download_flow_router,  # قبل از errors_router!
      errors_router,  # Must be last
  ]
```

---

### تسک ۱.۴: جداسازی پنل ادمین از download_handler ⬜

**باگ مرتبط:** ARCH-01  
**مشکل:** تابع `admin_panel` داخل `download_handler.py` قرار دارد که از `config_simple` ایمپورت می‌کند.

**اقدامات:**

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | ایجاد فایل جدید `bot/handlers/admin_panel.py` | ⬜ |
| 2 | انتقال تابع `admin_panel` و `admin_stats` به فایل جدید | ⬜ |
| 3 | اصلاح ایمپورت در `menu.py` | ⬜ |
| 4 | ثبت روتر جدید در `__init__.py` | ⬜ |

**راه حل دقیق:**

فایل جدید `bot/handlers/admin_panel.py`:
```python
"""Admin panel handler - separated from download_handler"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import settings
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """پنل ادمین"""
    if message.from_user.id not in settings.ADMIN_IDS_LIST:
        await message.answer("❌ شما مدیر نیستید!")
        return

    admin_text = (
        "⚙️ **پنل مدیریت پیشرفته**\n\n"
        "سلام مدیر عزیز!\n"
        "از دکمه‌های زیر استفاده کنید:"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار سریع", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 ارسال پیام همگانی", callback_data="broadcast_menu")],
    ])

    await message.answer(admin_text, reply_markup=kb)
```

```diff
# در menu.py:
- from bot.handlers.download_handler import admin_panel
+ from bot.handlers.admin_panel import admin_panel
```

---

### تسک ۱.۵: اصلاح هندلر catch-all (errors.py) ⬜

**باگ مرتبط:** BUG-03  
**مشکل:** پیام انگلیسی و نبود هوشمندی در تشخیص URL.

**راه حل دقیق:**
```diff
# در errors.py:
  @router.message()
  async def handle_errors(message: Message):
-     await message.reply(
-         "❌ Unknown command. Please use /help for available commands.",
-         parse_mode="Markdown"
-     )
+     text = message.text or ""
+     if text.startswith("http"):
+         await message.reply(
+             "⏳ لطفاً صبر کنید...\n"
+             "لینک شما در حال پردازش است.",
+         )
+     else:
+         await message.reply(
+             "❌ دستور ناشناخته.\n"
+             "برای مشاهده لیست دستورات از /help استفاده کنید.\n"
+             "یا یک لینک دانلود ارسال کنید.",
+         )
```

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | فارسی‌سازی پیام errors.py | ⬜ |
| 2 | افزودن تشخیص هوشمند URL | ⬜ |

---

### تسک ۱.۶: اصلاح پارامتر session/db در middleware ⬜

**باگ مرتبط:** DL-02  
**مشکل:** AuthMiddleware داده را با کلید `db` وارد data می‌کند اما download.py انتظار `session` دارد.

**راه حل دقیق:**
```diff
# در auth.py خط ۳۶:
  data["user"] = user
  data["db"] = session
+ data["session"] = session  # اضافه کردن نام دوم برای سازگاری
  return await handler(event, data)
```

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | افزودن `data["session"] = session` در auth.py | ⬜ |

---

## 🟡 فاز ۲: امنیت و پایداری (اولویت: بالا)

> **زمان تخمینی:** ۱-۲ ساعت  
> **هدف:** رفع حفره‌های امنیتی و جلوگیری از crash ناگهانی  
> **وابستگی:** فاز ۱ باید تکمیل شده باشد  
> **وضعیت کلی فاز:** ⬜ انجام نشده

---

### تسک ۲.۱: حذف IP سرور از کد منبع ⬜

**باگ مرتبط:** SEC-01, WEB-02

| # | فایل | خط | تغییر | وضعیت |
|---|------|-----|-------|-------|
| 1 | `download_handler.py` (یا فایل جدید admin_panel.py) | ۲۱۱ | IP را با متغیر محیطی جایگزین کنید | ⬜ |

**راه حل:**
```diff
# در admin_panel.py:
- url="http://135.181.198.243:8000/admin"
+ import os
+ server_ip = os.getenv("SERVER_IP", "localhost")
+ url=f"http://{server_ip}:8000/admin"
```

```diff
# در .env:
+ SERVER_IP=135.181.198.243
```

---

### تسک ۲.۲: اصلاح bare except در rate_limit.py ⬜

**باگ مرتبط:** SEC-03

```diff
# در rate_limit.py خط ۴۱:
- except:
-     pass
+ except Exception:
+     pass
```

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | تغییر `except:` به `except Exception:` | ⬜ |

---

### تسک ۲.۳: بهبود AuthMiddleware (session lifecycle) ⬜

**باگ مرتبط:** MW-01

**مشکل:** session در بلوک `async with` بسته می‌شود اما ممکن است هندلرهای بعدی هنوز نیاز داشته باشند.

**راه حل:** session را خارج از `async with` ایجاد و در `finally` ببندید:
```diff
  async def __call__(self, handler, event, data):
-     async with AsyncSessionLocal() as session:
-         # ...
-         data["db"] = session
-         return await handler(event, data)
+     session = AsyncSessionLocal()
+     try:
+         # ...
+         data["db"] = session
+         data["session"] = session
+         return await handler(event, data)
+     finally:
+         await session.close()
```

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | بازنویسی lifecycle سِشِن در auth.py | ⬜ |

---

## 🟠 فاز ۳: بهبود رابط کاربری (اولویت: متوسط-بالا)

> **زمان تخمینی:** ۳-۴ ساعت  
> **هدف:** تمام پیام‌ها فارسی، منوها کامل، تجربه کاربری حرفه‌ای  
> **وابستگی:** فاز ۱ باید تکمیل شده باشد  
> **وضعیت کلی فاز:** ⬜ انجام نشده

---

### تسک ۳.۱: فارسی‌سازی تمام پیام‌ها ⬜

**باگ مرتبط:** UI-01

| # | فایل | پیام فعلی (EN) | پیام جدید (FA) | وضعیت |
|---|------|----------------|----------------|-------|
| 1 | `help.py` | "Available Commands..." | "دستورات موجود..." | ⬜ |
| 2 | `profile.py` | "Your Profile..." | "پروفایل شما..." | ⬜ |
| 3 | `history.py` | "Your Recent Downloads" | "دانلودهای اخیر شما" | ⬜ |
| 4 | `history.py` | "No downloads yet" | "هنوز دانلودی ندارید" | ⬜ |
| 5 | `plans.py` | "Available Plans..." | "پلن‌های اشتراک..." | ⬜ |
| 6 | `referral.py` | "Your Referral Program" | "برنامه معرفی شما" | ⬜ |
| 7 | `errors.py` | "Unknown command" | "دستور ناشناخته" | ⬜ |

---

### تسک ۳.۲: تکمیل دکمه تنظیمات ⬜

**باگ مرتبط:** UI-02  
**مشکل:** دکمه "⚙️ تنظیمات" فقط پیام "به زودی" می‌دهد.

**اقدامات:**

| # | قابلیت | وضعیت |
|---|--------|-------|
| 1 | ایجاد فایل `bot/handlers/settings_handler.py` | ⬜ |
| 2 | پیاده‌سازی تغییر زبان (fa/en) | ⬜ |
| 3 | پیاده‌سازی تغییر کیفیت پیش‌فرض | ⬜ |
| 4 | ثبت روتر در `__init__.py` | ⬜ |
| 5 | اتصال دکمه تنظیمات در `menu.py` | ⬜ |

---

### تسک ۳.۳: بهبود پیام خوش‌آمدگویی /start ⬜

**اقدامات:**

| # | بهبود | وضعیت |
|---|-------|-------|
| 1 | افزودن تعداد کل دانلودها به پیام خوش‌آمدگویی | ⬜ |
| 2 | نمایش آخرین باری که کاربر فعال بوده | ⬜ |
| 3 | استفاده از نام ربات "Max Youtube Downloader" در تمام پیام‌ها | ⬜ |

---

## 🔵 فاز ۴: بهبود دیتابیس و مدل‌ها (اولویت: متوسط)

> **زمان تخمینی:** ۲-۳ ساعت  
> **هدف:** رفع مشکلات مدل‌ها و اطمینان از یکپارچگی دیتابیس  
> **وابستگی:** فاز ۱ و ۲ باید تکمیل شده باشند  
> **وضعیت کلی فاز:** ⬜ انجام نشده

---

### تسک ۴.۱: افزودن relationship به مدل Subscription ⬜

**باگ مرتبط:** DB-01

```diff
# در database/models/models.py، کلاس Subscription:
  class Subscription(Base):
      __tablename__ = "subscriptions"
      ...
      plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
+     plan = relationship("Plan", backref="subscriptions")
      ...
```

```diff
# در database/models/models.py، بالای فایل اضافه شود:
- from sqlalchemy.orm import relationship
  # این خط قبلاً وجود دارد ✅
```

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | افزودن `plan = relationship("Plan")` به مدل Subscription | ⬜ |

---

### تسک ۴.۲: بررسی یکپارچگی Base در مدل‌ها ⬜

**باگ مرتبط:** DB-02

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | بررسی `cached_download.py` که از همان `Base` ایمپورت می‌کند | ⬜ |
| 2 | اگر Base متفاوت است، اصلاح به `from database.models.models import Base` | ⬜ |
| 3 | تست `create_all()` برای ساخت تمام جداول | ⬜ |

---

### تسک ۴.۳: اصلاح Alembic migrations ⬜

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | حذف فایل‌های migration قبلی از `.gitignore` | ⬜ |
| 2 | اجرای `alembic revision --autogenerate` بعد از تغییرات مدل | ⬜ |
| 3 | Push فایل‌های migration به Git | ⬜ |

---

## 🟢 فاز ۵: پاکسازی و بهینه‌سازی نهایی (اولویت: پایین)

> **زمان تخمینی:** ۱-۲ ساعت  
> **هدف:** حذف فایل‌های اضافی، تمیزکاری کد  
> **وابستگی:** تمام فازهای قبلی تکمیل شده باشند  
> **وضعیت کلی فاز:** ⬜ انجام نشده

---

### تسک ۵.۱: حذف/انتقال فایل‌های اضافی ⬜

**باگ مرتبط:** ARCH-02

| # | فایل | اقدام | وضعیت |
|---|------|-------|-------|
| 1 | `config_simple.py` | انتقال به `archive/` | ⬜ |
| 2 | `bot/loader_professional_enhanced.py` | انتقال به `archive/` | ⬜ |
| 3 | `main_test.py` | انتقال به `archive/` | ⬜ |
| 4 | `database_user_model.py` | انتقال به `archive/` | ⬜ |
| 5 | `check.py` | انتقال به `archive/` | ⬜ |
| 6 | `deploy.py` | انتقال به `archive/` | ⬜ |
| 7 | `deploy_fix.py` | انتقال به `archive/` | ⬜ |
| 8 | `_fix_ds.py` | انتقال به `archive/` | ⬜ |
| 9 | `_fix_tasks.py` | انتقال به `archive/` | ⬜ |

---

### تسک ۵.۲: حذف download_handler.py ⬜

**وابستگی:** تسک ۱.۴ (جداسازی admin_panel) باید تکمیل شده باشد

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | بررسی تمام ایمپورت‌ها از `download_handler.py` | ⬜ |
| 2 | اطمینان از انتقال `admin_panel` و `admin_stats` | ⬜ |
| 3 | حذف از لیست روترها در `__init__.py` | ⬜ |
| 4 | انتقال فایل به `archive/` | ⬜ |

---

### تسک ۵.۳: بهبود لاگ‌گذاری ⬜

| # | اقدام | وضعیت |
|---|-------|-------|
| 1 | تغییر نام "DLBot" به "Max Youtube Downloader" در main.py | ⬜ |
| 2 | افزودن لاگ هنگام شناسایی ادمین | ⬜ |
| 3 | افزودن لاگ هنگام رسیدن لینک دانلود | ⬜ |

---

## 📋 خلاصه وضعیت کلی

| فاز | عنوان | تعداد تسک | وضعیت |
|-----|-------|-----------|-------|
| 🔴 فاز ۱ | رفع باگ‌های بحرانی | ۶ تسک (۱۹ آیتم) | ⬜ |
| 🟡 فاز ۲ | امنیت و پایداری | ۳ تسک (۴ آیتم) | ⬜ |
| 🟠 فاز ۳ | بهبود رابط کاربری | ۳ تسک (۱۵ آیتم) | ⬜ |
| 🔵 فاز ۴ | بهبود دیتابیس | ۳ تسک (۶ آیتم) | ⬜ |
| 🟢 فاز ۵ | پاکسازی نهایی | ۳ تسک (۱۴ آیتم) | ⬜ |
| **مجموع** | | **۱۸ تسک (۵۸ آیتم)** | ⬜ |

---

> [!IMPORTANT]
> **قانون طلایی:** هرگز فاز بعدی را شروع نکنید مگر فاز قبلی ۱۰۰٪ تکمیل و تست شده باشد.  
> بعد از هر فاز حتماً `docker compose up -d --build` بزنید و `/start` را تست کنید.

> [!TIP]
> **برای شروع:** فقط بگویید "فاز ۱ رو شروع کن" و من تمام ۶ تسک فاز ۱ را به ترتیب و با دقت اعمال می‌کنم.
