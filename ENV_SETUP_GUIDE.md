# ✅ تنظیمات `.env` - چیزهای لازم برای شروع

**فایل `.env` تقریباً آماده است!**

## 🔧 ۲ کار باقی‌مانده:

### 1️⃣ BOT_TOKEN را وارد کنید

**فایل: `.env` خط ۴**

```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
```

**جایگزین کنید با:**

```
BOT_TOKEN=توکن_شما_اینجا
```

**کجا می‌گیرید؟**
- تلگرام: @BotFather
- دستور: `/newbot`
- نام ربات وارد کنید
- نام کاربری وارد کنید
- **توکن کپی کنید و اینجا بگذارید**

---

### 2️⃣ ADMIN_ID را وارد کنید

**فایل: `.env` خط ۵**

```
ADMIN_IDS=123456789
```

**جایگزین کنید با:**

```
ADMIN_IDS=آیدی_شما
```

**کجا می‌گیرید؟**
- تلگرام: @userinfobot
- دستور: `/start`
- **آیدی نشان می‌دهد - کپی کنید**

---

## ✨ چیزهایی که از قبل تنظیم شده:

✅ **Pyrogram API ID**: `38449735`  
✅ **Pyrogram API Hash**: `30c6936b37f0767f3c3f128df9b2ca00`  
✅ **Session Name**: `my_youtube_uploader`  
✅ **Database**: SQLite (بدون نیاز به سرور)  
✅ **Language**: فارسی (فا)  

---

## 🚀 بعد از تنظیم:

```bash
pip install -r requirements.txt
alembic upgrade head
python main.py
```

---

## 📋 چک‌لیست:

- [ ] BOT_TOKEN وارد شد
- [ ] ADMIN_ID وارد شد
- [ ] `.env` ذخیره شد
- [ ] pip install انجام شد
- [ ] alembic upgrade انجام شد
- [ ] python main.py کار می‌کند

**تمام!** 🎉

---

**توضیح**: همه تنظیمات برای **توسعه و تست** بهینه‌شده است. بعداً برای **تولید** باید تغییر دهید.
