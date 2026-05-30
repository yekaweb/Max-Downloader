# 🚀 راهنمای کامل: از صفر تا اجرای ربات روی سرور (برای مبتدیان)

---

## 📋 فهرست

1. [قدم 1: ایجاد حساب GitHub](#قدم-1-ایجاد-حساب-github)
2. [قدم 2: ایجاد Repository](#قدم-2-ایجاد-repository)
3. [قدم 3: آماده‌سازی فایل‌ها](#قدم-3-آماده‌سازی-فایل‌ها)
4. [قدم 4: Push کردن کد به GitHub](#قدم-4-push-کردن-کد-به-github)
5. [قدم 5: دسترسی به سرور](#قدم-5-دسترسی-به-سرور)
6. [قدم 6: Clone کردن Repository روی سرور](#قدم-6-clone-کردن-repository-روی-سرور)
7. [قدم 7: اجرای ربات](#قدم-7-اجرای-ربات)

---

## قدم 1: ایجاد حساب GitHub

### ✅ مرحله 1: رفتن به وب‌سایت GitHub

1. مرورگر را باز کن
2. به این آدرس برو: **https://github.com**
3. دکمه **Sign up** (ثبت نام) را کلیک کن

### ✅ مرحله 2: تکمیل فرم ثبت نام

- **Email**: `rezaandroid0914@gmail.com`
- **Password**: یک رمز قوی انتخاب کن
- **Username**: `yekaweb` (یا یک نام دیگر)

### ✅ مرحله 3: تأیید ایمیل

- GitHub ایمیل تأیید برایت می‌فرستد
- به ایمیلت برو و لینک تأیید را کلیک کن

**حالا حساب GitHub داری! ✅**

---

## قدم 2: ایجاد Repository

### ✅ مرحله 1: ایجاد Repository جدید

1. وارد حساب GitHub خود شو
2. در گوشه سمت چپ پایین، **New** را کلیک کن
3. یا به این آدرس برو: **https://github.com/new**

### ✅ مرحله 2: تنظیمات Repository

| تنظیم | مقدار |
|--------|--------|
| **Repository name** | `dlbot-telegram` |
| **Description** | `DLBot - ربات حرفه‌ای دانلود محتوا` |
| **Public/Private** | Public (برای اینکه سرور بتواند دسترسی داشته باشد) |
| **Initialize with README** | نه (بعدا خود ما اضافه می‌کنیم) |

### ✅ مرحله 3: ایجاد Repository

دکمه **Create repository** را کلیک کن

**حالا Repository ایجاد شد! ✅**

پس از ایجاد، GitHub صفحه‌ای نشان می‌دهد که چگونه کد را آپلود کنی.

---

## قدم 3: آماده‌سازی فایل‌ها

### ✅ مرحله 1: نصب Git روی کامپیوتر

اگر Git ندارید:

1. به **https://git-scm.com** برو
2. **Download** را کلیک کن
3. نسخه Windows را دانلود و نصب کن
4. Next، Next، Finish کن

### ✅ مرحله 2: باز کردن Terminal/PowerShell

1. به پوشه پروژه برو:
   ```powershell
   cd "d:\telgram bot md backup 2- Copy"
   ```

### ✅ مرحله 3: اولین بار Git را تنظیم کن

**یک بار برای همیشه:**

```powershell
git config --global user.name "yekaweb"
git config --global user.email "rezaandroid0914@gmail.com"
```

✅ **حالا Git تنظیم شد!**

### ✅ مرحله 4: شروع Git در پوشه پروژه

```powershell
git init
git add .
git commit -m "Initial commit: DLBot v1.0.0"
```

---

## قدم 4: Push کردن کد به GitHub

### ✅ مرحله 1: اتصال به Repository

**دستورات دقیق برای شما:**

```powershell
git branch -M main
git remote add origin https://github.com/yekaweb/dlbot-telegram.git
git push -u origin main
```

✅ **کد به GitHub رفت!**

### ✅ مرحله 2: وارد کردن Username و Token

GitHub از تو می‌خواهد که Login کنی:

1. هنگام `git push`، GitHub می‌خواهد **Username** و **Password** (یا Token)
2. **Username** = نام کاربری GitHub
3. **Password** = یک Token خاص (نه رمز حساب)

#### 🔑 چگونه Token بسازی:

1. وارد GitHub شو
2. بروی **Settings** → **Developer settings** → **Personal access tokens**
3. **Generate new token** را کلیک کن
4. نام: `DLBot`
5. **Scopes**: انتخاب کن:
   - ✅ repo (همه چیز)
   - ✅ workflow
6. **Generate token** را کلیک کن
7. **Token را کپی کن** (دوباره نظر نخواهی کرد!)

#### 📌 اگر Git از Password می‌خواهد:

```
Username: ali1234
Password: (Token را که ساختی اینجا بچسب)
```

### ✅ مرحله 3: تأیید Upload

اگر درست باشد، می‌بینی:
```
 ✔ Everything up-to-date
```

**حالا کد روی GitHub است! ✅**

---

## قدم 5: دسترسی به سرور

### ✅ اختیار 1: سرور Linux + SSH

اگر سرور Linux داری، باید:

1. **SSH Key** یا **Username/Password** داشته باشی
2. **IP Address** سرور را بدانی

مثال:
```powershell
ssh root@192.168.1.100
```

یا اگر Password ندارید:
```powershell
ssh -i private_key.pem root@192.168.1.100
```

### ✅ اختیار 2: سرویس ابری (VPS)

اگر از **Linode**، **DigitalOcean**، یا **Hetzner** استفاده می‌کنی:

1. لاگین کن
2. **SSH Console** یا **Terminal** را باز کن
3. یا با SSH متصل شو:
   ```powershell
   ssh root@VPS_IP
   ```

### ✅ اختیار 3: سرور Windows

اگر سرور Windows است:
- اگر RDP Access داری، Remote Desktop را استفاده کن
- یا PowerShell Remoting استفاده کن

**فرض می‌کنم Linux است!** ✅

---

## قدم 6: Clone کردن Repository روی سرور

### ✅ مرحله 1: متصل شدن به سرور

```powershell
ssh root@YOUR_SERVER_IP
```

جایگزین کن: `YOUR_SERVER_IP` = IP سرور

مثال:
```powershell
ssh root@192.168.1.50
```

### ✅ مرحله 2: نصب Git روی سرور (اگر نیست)

```bash
apt update
apt install -y git python3 python3-pip
```

### ✅ مرحله 3: Clone Repository

```bash
cd /home
git clone https://github.com/yekaweb/dlbot-telegram.git
cd dlbot-telegram
```

**حالا کد روی سرور است! ✅**

---

## قدم 7: اجرای ربات

### ✅ مرحله 1: نصب Python Dependencies

```bash
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

**صبر کن 2-5 دقیقه تا تمام پکیج‌ها نصب شوند...**

### ✅ مرحله 2: تنظیم .env

ابتدا `.env` فایل خود را آپلود کن:

#### 💡 روش 1: SCP (ساده‌ترین)

**روی کامپیوتر خود:**
```powershell
scp "d:\telgram bot md backup 2- Copy\.env" root@YOUR_SERVER_IP:/home/dlbot-telegram/.env
```

#### 💡 روش 2: Editor روی سرور

```bash
nano .env
```

بعد محتویات `.env` خود را کپی و بچسب:

```bash
BOT_TOKEN=123456789:ABCdefGHIjklmnOPqrsTUVwxyzABCdef
ADMIN_IDS=123456789,987654321
BOT_USERNAME=dlbot
DB_TYPE=sqlite
DB_PATH=./dlbot.db
APP_ENV=production
...
```

Save کن: `Ctrl+X` → `Y` → `Enter`

### ✅ مرحله 3: ایجاد Directories

```bash
mkdir -p logs temp_downloads cached_files
```

### ✅ مرحله 4: اجرای ربات

```bash
python3 main.py
```

اگر درست باشد، می‌بینی:
```
2026-05-30 19:07:05 | INFO | DLBot - Professional Telegram Downloader
2026-05-30 19:07:05 | INFO | 🤖 Starting DLBot v1.0.0
2026-05-30 19:07:07 | INFO | 🚀 Starting bot polling...
2026-05-30 19:07:07 | INFO | 📡 Bot is listening for updates...
```

**ربات روی سرور اجرا می‌شود! ✅**

---

## مرحله اضافی: اجرای پیوسته (Daemon)

اگر می‌خواهی ربات برای همیشه اجرا شود (حتی پس از بستن SSH):

### ✅ استفاده از `tmux` (بهترین روش)

```bash
# نصب tmux
apt install -y tmux

# ایجاد session
tmux new-session -d -s dlbot

# اجرای ربات در background
tmux send-keys -t dlbot "cd /home/dlbot-telegram && python3 main.py" Enter

# بررسی وضعیت
tmux list-sessions
```

### ✅ استفاده از `systemd` (حرفه‌ای)

```bash
cat > /etc/systemd/system/dlbot.service << EOF
[Unit]
Description=DLBot Telegram
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/dlbot-telegram
ExecStart=/usr/bin/python3 /home/dlbot-telegram/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# فعال کردن
systemctl enable dlbot
systemctl start dlbot
systemctl status dlbot
```

---

## 🆘 مشکل‌گیری

### مشکل: Git authentication ناکام

**حل:**
```powershell
git config --global credential.helper store
git push  # دوباره سعی کن
```

### مشکل: Permission denied (SSH key)

**حل:**
```bash
chmod 600 ~/.ssh/private_key
```

### مشکل: Module not found

**حل:**
```bash
pip3 install -r requirements.txt --upgrade
```

### مشکل: Bot not responding

**حل:**
```bash
# بررسی logs
tail -f logs/dlbot.log

# reboot the server
reboot
```

---

## ✅ خلاصه فرآیند

| مرحله | دستور | نتیجه |
|------|--------|--------|
| 1 | GitHub ثبت نام | حساب فعال |
| 2 | Repository ایجاد | Repository خالی |
| 3 | `git init` | Git آماده |
| 4 | `git push` | کد روی GitHub |
| 5 | `ssh` | متصل به سرور |
| 6 | `git clone` | کد روی سرور |
| 7 | `python3 main.py` | ربات اجرا می‌شود |

---

## 🎯 بعد از اجرا

### ✅ تست ربات

1. Telegram را باز کن
2. ربات را جستجو کن: `@YOUR_BOT_USERNAME`
3. `/start` را ارسال کن
4. اگر پاسخ دهد: **ربات کار می‌کند! ✅**

### ✅ Update کردن کد

اگر کد را تغییر دادی و می‌خواهی Update کنی:

**روی کامپیوتر خود:**
```powershell
git add .
git commit -m "Update: new features"
git push
```

**روی سرور:**
```bash
git pull
# اگر نیاز است:
pip3 install -r requirements.txt
# دوباره start کن
```

---

## 📞 نکات مهم

⚠️ **رازهای سرور:**
- `BOT_TOKEN` را **هیچ‌کجا** share نکن!
- `.env` را روی GitHub **push نکن!**
- IP سرور را محفوظ نگاه دار

⚠️ **آپدیت کردن کد:**
- ابتدا روی کامپیوتر test کن
- سپس روی GitHub push کن
- بعد روی سرور pull کن

✅ **بهتر شده:**
- ربات **24/7** اجرا می‌شود
- در ایران کار می‌کند
- آپدیت آسان است

---

**🎉 تمام! حالا ربات برای همیشه روی سرور اجرا می‌شود!**

اگر مشکلی داشتی، سؤال کن! 😊
