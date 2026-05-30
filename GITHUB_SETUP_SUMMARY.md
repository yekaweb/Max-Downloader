# 🎯 GITHUB SETUP - خلاصه برای yekaweb

---

## 👤 اطلاعات شما

| مورد | مقدار |
|-----|--------|
| **Email** | rezaandroid0914@gmail.com |
| **Username** | yekaweb |
| **Repository** | dlbot-telegram |

---

## 🚀 مراحل (25 دقیقه)

### 1️⃣ ثبت نام GitHub (5 دقیقه)

```
بروی: https://github.com/signup
Email: rezaandroid0914@gmail.com
Username: yekaweb
Password: [انتخاب کن]
```

✅ **ایمیل تأیید کن**

---

### 2️⃣ Repository ایجاد (3 دقیقه)

```
بروی: https://github.com/new
یا بعد از Login: + New
```

**تنظیمات:**
```
Repository name: dlbot-telegram
Description: DLBot - ربات حرفه‌ای دانلود محتوا
Public: ✅ YES
```

✅ **Create repository**

---

### 3️⃣ Push کردن کد (5 دقیقه)

**PowerShell (Windows):**

```powershell
cd "d:\telgram bot md backup 2- Copy"

# یک بار تنظیم کن:
git config --global user.name "yekaweb"
git config --global user.email "rezaandroid0914@gmail.com"

# شروع:
git init
git add .
git commit -m "Initial commit: DLBot v1.0.0"

# متصل کن و push کن:
git remote add origin https://github.com/yekaweb/dlbot-telegram.git
git branch -M main
git push -u origin main
```

**اگر از Username/Password پرسید:**

1. GitHub Login کن
2. بروی **Settings** → **Developer settings** → **Personal access tokens**
3. **Generate new token**
4. Scopes: ✅ repo, ✅ workflow
5. **Generate token**
6. **Copy کن** و اینجا بچسب

```
Username: yekaweb
Password: (Token)
```

✅ **کد روی GitHub!**

---

### 4️⃣ Clone روی سرور (5 دقیقه)

**SSH به سرور:**

```bash
ssh root@SERVER_IP
```

**Setup:**

```bash
cd /home
git clone https://github.com/yekaweb/dlbot-telegram.git
cd dlbot-telegram

# نصب
pip3 install -r requirements.txt

# تنظیم .env
nano .env
```

**محتویات .env (نمونه):**

```
BOT_TOKEN=123456789:ABCdefGHIjklmnOPqrsTUVwxyzABCdef
ADMIN_IDS=987654321
BOT_USERNAME=mybot
DB_TYPE=sqlite
DB_PATH=./dlbot.db
APP_ENV=production
LOG_FILE=logs/dlbot.log
LOG_LEVEL=INFO
SUPPORTED_LANGUAGES=fa,en
DEFAULT_LANGUAGE=fa
```

**Save:** Ctrl+X → Y → Enter

✅ **سرور آماده!**

---

### 5️⃣ اجرای ربات (2 دقیقه)

**گزینه 1: Test سریع**

```bash
python3 main.py
```

✅ **باید این را ببینی:**
```
INFO     | 🤖 Starting DLBot v1.0.0
INFO     | 🚀 Starting bot polling...
INFO     | 📡 Bot is listening for updates...
```

**Ctrl+C برای متوقف کردن**

---

**گزینه 2: اجرای دائم (بهتر)**

```bash
tmux new-session -d -s dlbot "python3 main.py"
```

**بررسی:**
```bash
tmux list-sessions
```

---

## 📋 Checklist

- [ ] GitHub Account ایجاد شد
- [ ] Repository ایجاد شد
- [ ] Git تنظیم شد (`git config`)
- [ ] `git push` انجام شد
- [ ] سرور SSH شد
- [ ] `git clone` انجام شد
- [ ] `.env` بسازی
- [ ] `pip3 install` انجام شد
- [ ] `python3 main.py` تست شد
- [ ] `tmux` شروع شد

✅ **همه انجام شد! ربات کار می‌کند!**

---

## 🔑 نکات مهم

### ❌ **هرگز push نکن:**
- `.env` (رازهای سرور!)
- `*.db` (database files)
- `__pycache__/` (Python cache)
- `venv/` (virtual environment)

### ✅ **همیشه push کن:**
- `*.py` (کد)
- `requirements.txt` (dependencies)
- `*.md` (مستندات)

---

## 🆘 مشکلات

### ❌ "fatal: not a git repository"

```powershell
git init
```

### ❌ "Permission denied (publickey)"

```bash
# SSH key problem
# استفاده کن از HTTPS:
git remote set-url origin https://github.com/yekaweb/dlbot-telegram.git
```

### ❌ "Module not found"

```bash
pip3 install -r requirements.txt --upgrade
```

### ❌ "Bot not responding"

```bash
# بررسی logs
tail -f logs/dlbot.log

# یا restart
tmux kill-session -t dlbot
tmux new-session -d -s dlbot "python3 main.py"
```

---

## 📚 فایل‌های مرجع

| فایل | هدف |
|------|------|
| `GITHUB_DEPLOYMENT_GUIDE.md` | راهنمای مفصل |
| `QUICK_GIT_COMMANDS.md` | دستورات سریع |
| `.env.example` | الگوی کامل |
| `README_SIMPLE.md` | معلومات سریع |

---

## 🎉 بعد از Setup

### آپدیت کردن کد

**روی کامپیوتر:**
```powershell
git add .
git commit -m "Update: new features"
git push
```

**روی سرور:**
```bash
git pull
pip3 install -r requirements.txt
tmux kill-session -t dlbot
tmux new-session -d -s dlbot "python3 main.py"
```

---

**🚀 حالا ربات برای همیشه اجرا می‌شود!**

**سؤال‌های دیگر؟ → GITHUB_DEPLOYMENT_GUIDE.md**
