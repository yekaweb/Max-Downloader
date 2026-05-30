# 🤖 DLBot - ربات دانلود محتوا از تلگرام

> نسخه ساده‌شده برای سرور، با راهنمای مرحله‌به‌مرحله

---

## 📌 مقدمه سریع

**DLBot** ربات حرفه‌ای برای دانلود ویدیو و عکس از:
- 🎥 YouTube
- 📸 Instagram  
- 🐦 Twitter (X)
- و بسیاری دیگر...

---

## 🎯 شروع سریع

### ✅ بر روی کامپیوتر محلی

```powershell
# 1. پوشه پروژه
cd "d:\telgram bot md backup 2- Copy"

# 2. نصب Python (از https://python.org)
python --version  # باید Python 3.10+ باشد

# 3. نصب dependencies
pip install -r requirements.txt

# 4. تنظیم .env (ایمیل و توکن ربات)
# فایل .env.example را نگاه کن

# 5. اجرا
python main.py
```

### ✅ بر روی سرور

```bash
# 1. متصل شو
ssh root@SERVER_IP

# 2. Clone کن
cd /home && git clone https://github.com/USERNAME/dlbot-telegram.git

# 3. Setup
cd dlbot-telegram
pip3 install -r requirements.txt
nano .env  # مقادیر خود وارد کن

# 4. اجرا (دائم)
tmux new-session -d -s dlbot "python3 main.py"
```

---

## 📖 راهنماهای کامل

| فایل | توضیح |
|------|--------|
| **GITHUB_DEPLOYMENT_GUIDE.md** | روش upload روی GitHub و سرور |
| **QUICK_GIT_COMMANDS.md** | دستورات سریع Git |
| **.env.example** | نمونه تنظیمات (الگو) |

---

## 🔑 فایل‌های مهم

```
dlbot-telegram/
├── main.py                 # نقطه شروع
├── config_simple.py        # تنظیمات
├── requirements.txt        # وابستگی‌ها
├── .env                    # رازهای سرور (هرگز push نکن!)
├── .env.example            # نمونه تنظیمات
├── bot/                    # کد ربات
│   ├── loader_simple.py   # handlers و dispatcher
│   └── handlers/           # command handlers
├── database/               # دسترسی‌ها database
├── logs/                   # فایل‌های log
└── migrations/             # Alembic migrations
```

---

## ⚙️ تنظیمات سرور

### محتویات `.env`:

```
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ
ADMIN_IDS=123456789
BOT_USERNAME=mybot
DB_TYPE=sqlite
DB_PATH=./dlbot.db
APP_ENV=production
LOG_FILE=logs/dlbot.log
LOG_LEVEL=INFO
```

---

## 🧪 آزمایش ربات

1. ربات را شروع کن: `python main.py`
2. Telegram باز کن
3. ربات را جستجو کن: `@YOUR_BOT_USERNAME`
4. دستور `/start` بفرست
5. اگر پاسخ دهد: ✅ **کار می‌کند!**

---

## 🐛 مشکل‌ها

### مشکل: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### مشکل: "BOT_TOKEN not configured"
- فایل `.env` را بررسی کن
- `BOT_TOKEN` را در آن نوشته‌ای؟

### مشکل: "Cannot connect to Telegram"
- اتصال اینترنت را بررسی کن
- اگر ایران هستی، از سرور استفاده کن

---

## 📚 فایل‌های بیشتر

- `GITHUB_DEPLOYMENT_GUIDE.md` - راهنمای GitHub و سرور (کامل)
- `QUICK_GIT_COMMANDS.md` - دستورات سریع
- `.env.example` - الگوی تنظیمات

---

## 🆘 کمک دادن / مسائل

اگر مشکلی داشتی:
1. Logs را بررسی کن: `logs/dlbot.log`
2. Terminal خطا را بخوان
3. فایل‌های راهنما را بررسی کن

---

## 📝 نسخه

- **نسخه:** 1.0.0
- **آخرین آپدیت:** 2026-05-30
- **Python:** 3.10+

---

**🚀 برای شروع کامل: GITHUB_DEPLOYMENT_GUIDE.md را بخوان!**
