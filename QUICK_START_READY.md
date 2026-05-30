# 🚀 DLBot - آماده برای اجرا

**بات داونلودر یوتیوب و اینستاگرام برای تلگرام**

---

## ⚡ شروع سریع (۱۰ ثانیه!)

### **گام ۱: فایل اسکریپت را باز کن**
```
START_BOT.bat
```

### **گام ۲: دوبار کلیک کن** 🖱️
- تمام مراحل خودکار انجام می‌شه
- صبر کن تا ربات شروع بشه

### **گام ۳: تست کن** 
- به بات در تلگرام بنویس: `/start`
- باید جواب بده ✅

---

## 📋 فایلهای راهنما

| فایل | توضیح |
|------|-------|
| **RUN_BOT_EASILY.md** | راهنمای کامل (سادگی و سرعت) |
| **HOW_TO_RUN_SIMPLE.md** | تفصیل کامل برای مبتدیان |
| **DEPLOYMENT_GUIDE_FARSI.md** | راه‌اندازی روی سرور |
| **ENV_SETUP_GUIDE.md** | تنظیم متغیرهای محیطی |

---

## 🛠️ فایلهای اجرایی

| فایل | نقش |
|------|-----|
| **START_BOT.bat** 🔥 | شروع خودکار (بهترین) |
| **verify_deployment.py** | تست محیط |
| **deploy.py** | استقرار خودکار |
| **test_env.py** | تشخیص مشکلات |

---

## 📁 ساختار پروژه

```
📦 DLBot
├── 📄 START_BOT.bat          ← شروع کن!
├── 📄 RUN_BOT_EASILY.md      ← راهنما
│
├── 📂 bot/                   ← منطق بات
│   ├── loader.py             ← بات و dispatcher
│   ├── states/               ← FSM states
│   └── handlers/             ← دستورات
│
├── 📂 database/              ← داتابیس
│   ├── connection.py         ← اتصال
│   ├── models/               ← مدل‌های SQLAlchemy
│   └── repositories/         ← CRUD operations
│
├── 📂 modules/               ← ماژول‌های دانلود
│   ├── youtube/              ← یوتیوب
│   ├── instagram/            ← اینستاگرام
│   ├── twitter/              ← توییتر
│   └── registry.py           ← ثبت‌نام ماژول‌ها
│
├── 📂 services/              ← سرویس‌های تجاری
│   ├── download.py           ← دانلود
│   ├── cache.py              ← کش
│   ├── referral.py           ← سیستم دعوت
│   └── payment.py            ← پرداخت
│
├── 📂 migrations/            ← مایگریشن‌های DB
│   └── versions/             ← نسخه‌های مایگریشن
│
├── 📂 locales/               ← ترجمه‌ها
│   ├── fa/messages.json      ← فارسی
│   ├── en/messages.json      ← انگلیسی
│   └── ...
│
├── 📄 config.py              ← تنظیمات
├── 📄 main.py                ← نقطه ورود
├── 📄 .env                   ← متغیرهای محیط
├── 📄 requirements.txt        ← نیازمندی‌ها
└── 📄 alembic.ini            ← تنظیمات Alembic
```

---

## ✨ ویژگی‌ها

### دانلود
- ✅ یوتیوب (ویدیو + صدا)
- ✅ اینستاگرام (عکس + فیلم)
- ✅ توییتر (ویدیو)
- ✅ سایز تا 4GB با Pyrogram

### سیستم کسب سکه
- ✅ سیستم دعوت (referral)
- ✅ کسب سکه از دانلود
- ✅ ایجاد فرصت‌های خریدی

### پرداخت
- ✅ CryptoBot (پرداخت رمز)
- ✅ NOWPayments (کریپتو)
- ✅ ZarinPal (ریال ایرانی)

### مدیریت
- ✅ پنل Admin (FastAPI)
- ✅ Broadcast پیام‌ها
- ✅ شماره‌گیری و آمار

### بین‌المللی
- ✅ ۵ زبان: فارسی، انگلیسی، عربی، روسی، چینی
- ✅ پشتیبانی RTL

---

## 🔧 تنظیمات پایه

### `.env` فایل
```env
# بات
BOT_TOKEN=YOUR_TOKEN_HERE
ADMIN_IDS=ID1,ID2
BOT_USERNAME=your_bot_username

# داتابیس (SQLite برای شروع)
DB_TYPE=sqlite
DB_PATH=./dlbot.db

# زبان
DEFAULT_LANGUAGE=fa
```

---

## 📊 سیستم‌های فناور

- **Framework**: Aiogram (Telegram Bot)
- **ORM**: SQLAlchemy
- **Database**: SQLite / PostgreSQL
- **Task Queue**: Celery
- **Admin Panel**: FastAPI
- **Logging**: Loguru
- **Downloader**: yt-dlp

---

## 🚨 شروع کن

```bash
# گزینه 1: خودکار (بهترین)
START_BOT.bat

# گزینه 2: دستی
python main.py
```

---

## 🆘 کمک

### خطا دارم!
1. ببینم `verify_deployment.py` چی می‌گه:
   ```bash
   python verify_deployment.py
   ```

2. فایل راهنما چک کن:
   - `RUN_BOT_EASILY.md` - سریع
   - `HOW_TO_RUN_SIMPLE.md` - تفصیلی

3. اگه نشد، `logs/dlbot.log` رو ببینید

---

## 📱 استفاده

وقتی شروع شد:

```
/start           ← شروع
/help            ← کمک
/youtube         ← دانلود از یوتیوب
/instagram       ← دانلود از اینستاگرام
/stats           ← آمار شخصی
/refer           ← کد دعوت
```

---

## 🎯 وضعیت پروژه

- [x] PHASE 1: تصحیح مستندات
- [x] PHASE 2: معماری و API
- [x] PHASE 3: تست و محلی‌سازی
- [x] نصب و تنظیم
- [ ] اجرا روی سرور (بعدی)

---

## 📞 پشتیبانی

**اگه مشکل داشتی:**

1. `verify_deployment.py` را اجرا کن
2. خطا را دقیق کپی کن
3. فایل‌های راهنما را چک کن

---

## ©️ حقوق

تمام کد و منابع برای این پروژه ایجاد شده‌اند.

---

**حاضرید؟ شروع کنید! 🚀**

```
دوبار روی START_BOT.bat کلیک کن و تمام شد!
```
