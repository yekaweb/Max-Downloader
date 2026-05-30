# 🚀 شروع سریع (Quick Start)

**فقط ۵ مرحله:**

## 1️⃣ نصب Python
```
پیوند: www.python.org/downloads
✅ Add to PATH تیک بزنید!
```

## 2️⃣ توکن را از BotFather بگیرید
```
تلگرام: @BotFather
/newbot را بنویسید
نام و نام کاربری وارد کنید
توکن را کپی کنید
```

## 3️⃣ فایل `.env` را ایجاد کنید
```
TELEGRAM_BOT_TOKEN=توکن_شما
TELEGRAM_APP_ID=app_id_شما
TELEGRAM_APP_HASH=app_hash_شما
ADMIN_ID=آیدی_شما
DATABASE_URL=sqlite:///dlbot.db
```

## 4️⃣ برنامه‌ها را نصب کنید
```bash
pip install -r requirements.txt
alembic upgrade head
```

## 5️⃣ ربات را اجرا کنید
```bash
python main.py
```

---

**تمام!** ✅ ربات آماده است!

برای توضیحات کامل: **DEPLOYMENT_GUIDE_FARSI.md** را بخوانید
