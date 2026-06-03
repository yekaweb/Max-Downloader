# 🚀 راه‌اندازی ربات - از این پوشه

**این راهنما برای پوشه‌ای که الآن هستید:**
```
d:\telgram bot md backup 2- Copy\
```

---

## ✅ چیزهایی که ایجاد شده‌اند:

✅ `main.py` - برنامه ربات  
✅ `requirements.txt` - لیست برنامه‌های لازم  
✅ `config.py` - تنظیمات  
✅ `bot/` - فایل‌های ربات  
✅ `modules/` - دانلودرها (YouTube, Instagram, Twitter)  
✅ `services/` - سرویس‌های پرداخت و دیگری  
✅ `database/` - مدل‌های دیتابیس  
✅ `locales/` - ترجمه‌های ۵ زبان  
✅ `migrations/` - فایل‌های دیتابیس  

---

## 📋 مراحل راه‌اندازی (برای این پوشه):

### **مرحله ۱: فایل `.env` را تنظیم کنید**

فایل `.env` در این پوشه وجود دارد:
```
d:\telgram bot md backup 2- Copy\.env
```

**باز کنید و این‌ها را وارد کنید:**

```env
# توکن ربات از BotFather
TELEGRAM_BOT_TOKEN=توکن_شما_اینجا

# App ID و Hash از my.telegram.org
TELEGRAM_APP_ID=123456
TELEGRAM_APP_HASH=abcdef123456

# آیدی شما
ADMIN_ID=آیدی_شما

# دیتابیس (الآن SQLite)
DATABASE_URL=sqlite:///dlbot.db
```

**مثال واقعی:**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGhijklmnopqrstuvwxyz
TELEGRAM_APP_ID=123456
TELEGRAM_APP_HASH=abcdef1234567890abcdef1234567890
ADMIN_ID=987654321
DATABASE_URL=sqlite:///dlbot.db
```

---

### **مرحله ۲: VS Code را باز کنید**

1. **VS Code را باز کنید**
2. **File > Open Folder** کلیک کنید
3. **این پوشه را انتخاب کنید:**
   ```
   d:\telgram bot md backup 2- Copy\
   ```
4. **Select Folder** کلیک کنید

---

### **مرحله ۳: Terminal را باز کنید**

در VS Code:
- **View > Terminal** کلیک کنید
- یا `Ctrl + ~` کلیک کنید

باید نشان دهد:
```
d:\telgram bot md backup 2- Copy>
```

---

### **مرحله ۴: برنامه‌ها را نصب کنید**

**در Terminal کپی و پیست کنید:**

```bash
pip install -r requirements.txt
```

**انتظار بکشید** (۵-۱۰ دقیقه)

---

### **مرحله ۵: دیتابیس را تنظیم کنید**

**در Terminal کپی و پیست کنید:**

```bash
alembic upgrade head
```

اگر خطا داد، این را تلاش کنید:
```bash
python -m alembic upgrade head
```

---

### **مرحله ۶: ربات را اجرا کنید**

**در Terminal کپی و پیست کنید:**

```bash
python main.py
```

اگر درست شد، نشان می‌دهد:
```
Bot started successfully!
Listening for messages...
```

---

## 🧪 تست کنید

1. **تلگرام را باز کنید**
2. **ربات خود را جستجو کنید**
3. **/start کلیک کنید**
4. **ربات باید پاسخ دهد** ✅

---

## 🛑 اگر خطا داد:

### خطا: `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

### خطا: `Database error`
```bash
alembic upgrade head
```

### خطا: `Bot token invalid`
- فایل `.env` را بررسی کنید
- توکن درست است؟

---

## 📁 فایل‌های مهم در این پوشه:

| فایل | استفاده |
|------|---------|
| `.env` | تنظیمات (توکن، کلید‌ها) |
| `main.py` | برنامه اصلی |
| `requirements.txt` | برنامه‌های لازم |
| `config.py` | تنظیمات سیستم |
| `alembic.ini` | تنظیمات دیتابیس |
| `bot/` | فایل‌های ربات |
| `modules/` | دانلودرها |
| `services/` | سرویس‌ها |
| `database/` | مدل‌ها |
| `migrations/` | شماتیک دیتابیس |

---

## 🔧 دستورات مفید:

### ربات را متوقف کنید
```
Ctrl + C
```

### ربات را دوباره شروع کنید
```bash
python main.py
```

### دیتابیس را پاک کنید (برای تست)
```bash
del dlbot.db
alembic upgrade head
python main.py
```

### تست‌ها را اجرا کنید
```bash
pytest
```

---

## ✅ چک‌لیست نهایی:

- [ ] `.env` تنظیم شد
- [ ] پوشه در VS Code باز است
- [ ] Terminal در VS Code است
- [ ] `pip install -r requirements.txt` انجام شد
- [ ] `alembic upgrade head` انجام شد
- [ ] `python main.py` کار می‌کند
- [ ] ربات در تلگرام پاسخ می‌دهد

**اگر همه ✅ هستند = تمام!** 🎉

---

## 🆘 سؤال؟

- **مسیر پوشه اشتباه است؟** - از فایل منیجر Windows پوشه را باز کنید
- **Terminal باز نشد؟** - `Ctrl + ~` دوباره تلاش کنید
- **`.env` نمی‌دانید کجاست؟** - در پوشه اصلی است
- **توکن نمی‌دانید؟** - DEPLOYMENT_GUIDE_FARSI.md بخش ۲ را بخوانید

---

**بسیار ساده است!** فقط ۶ مرحله.

**حالا شروع کنید** → `.env` را تنظیم کنید ✅
