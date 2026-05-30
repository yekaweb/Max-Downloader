# ✅ راه‌اندازی ربات - سریع و آسان

**انتخاب کنید که چطور شروع کنید:**

---

## 🔥 **روش 1: خودکار (توصیه می‌شود!)**

### فقط این کار کن:
1. **فایل اسکریپت:** `START_BOT.bat`
2. **دوبار روی آن کلیک کن** (Double Click)
3. **انتظار بکش** - تمام مراحل خودکار انجام می‌شه

### خروجی اگه درست باشه:
```
[1/5] Testing environment... ✅
[2/5] Installing dependencies... ✅
[3/5] Creating directories... ✅
[4/5] Setting up database... ✅
[5/5] Starting bot...
   🤖 Starting DLBot v1.0.0
   ✅ Bot components loaded successfully
```

---

## 📱 **روش 2: دستی (اگر روش 1 کار نکرد)**

### پیش‌نیاز:
- **Windows Terminal** یا **PowerShell** یا **CMD** باز کن
- **مسیر:** `d:\telgram bot md backup 2- Copy\`

```powershell
# کپی و پیست کن:
cd "d:\telgram bot md backup 2- Copy"
```

### مرحله به مرحله:

#### ✅ **گام ۱: نصب نیازمندی‌ها** (۲-۵ دقیقه)
```powershell
pip install -r requirements.txt
```

اگر خطا داد: `pip install --upgrade pip` بعد دوباره سعی کن

#### ✅ **گام ۲: داتابیس** (۳۰ ثانیه)
```powershell
alembic upgrade head
```

اگر خطا داد:
```powershell
python -m alembic upgrade head
```

#### ✅ **گام ۳: شروع ربات!**
```powershell
python main.py
```

### ✨ انتظار بکش تا ببینی:
```
2026-05-30 00:30:00 | INFO     | 🤖 Starting DLBot v1.0.0
2026-05-30 00:30:00 | INFO     | ✅ Bot components loaded successfully
2026-05-30 00:30:00 | INFO     | 🔌 Connecting to database...
2026-05-30 00:30:00 | INFO     | ✅ Database connected
```

---

## 🧪 **روش 3: اول تست کن (اختیاری)**

اگر می‌خوای مطمئن باشی محیط درست هست:

```powershell
python test_env.py
```

باید بگه:
```
✅ Imports: PASS
✅ Environment: PASS
✅ Directories: PASS
✅ Config: PASS
```

---

## 🎮 **تست ربات بعد از شروع**

وقتی ربات شروع شد:

1. **به تلگرام برو**
2. **جستجو کن:** `Max_youtube_downloader_bot`
3. **شروع کن:** `/start`
4. **باید جواب بده** ✅

---

## ⚠️ **حل مشکلات**

### ❌ "Python not found"
```
نصب Python:
1. python.org برو
2. Download Python 3.10+
3. دوباره تلاش کن
```

### ❌ "pip install failed"
```powershell
# دوباره سعی کن با upgrade
pip install --upgrade pip
pip install -r requirements.txt
```

### ❌ "alembic not found"
```powershell
# دوباره رو نصب کن:
pip install alembic
alembic upgrade head
```

### ❌ "BOT_TOKEN is not specified"
```
✅ فایل .env درست هست (روی شما ویرایش شده)
اگه مشکل بود: ببینید BOT_TOKEN داخلش هست
```

---

## 📁 **فایلهای مهم**

| فایل | توضیح |
|------|-------|
| `START_BOT.bat` 🔥 | دوبار‌کلیک کن - خودکار! |
| `.env` | تنظیمات (ربات، دیتابیس، ...) |
| `requirements.txt` | لیست نیازمندی‌ها |
| `main.py` | نقطه شروع ربات |
| `test_env.py` | تست محیط |

---

## 🎯 **خلاصه:**

```
یک‌جمله: دوبار روی START_BOT.bat کلیک کن و صبر کن! ✅
```

### هیچ چیز دیگه نیاز نیست! 🚀

---

## 📚 **اگه می‌خوای بیشتر بدونی:**

- `HOW_TO_RUN_SIMPLE.md` - تفصیلی (برای مبتدیان)
- `DEPLOYMENT_GUIDE_FARSI.md` - سرور (پیشرفته)
- `ENV_SETUP_GUIDE.md` - تنظیمات محیط

---

**سوالی داری؟** - اگه خطا داد، دقیق متن خطا رو کپی کن و چک کن.

**آماده‌ای؟ شروع کن! 🎉**
