# 🚀 دستورات سریع: GitHub و سرور

## مرحله 1: اولین بار (یک بار)

```powershell
# 1. پوشه پروژه
cd "d:\telgram bot md backup 2- Copy"

# 2. تنظیم Git (یک بار برای همیشه)
git config --global user.name "yekaweb"
git config --global user.email "rezaandroid0914@gmail.com"

# 3. شروع Git
git init
git add .
git commit -m "Initial commit: DLBot v1.0.0"

# 4. اضافه کردن URL GitHub
git remote add origin https://github.com/yekaweb/dlbot-telegram.git
git branch -M main
git push -u origin main
```

---

## مرحله 2: اگر کد تغییر کرد

```powershell
# فقط این 3 دستور:
git add .
git commit -m "Update: description"
git push
```

---

## مرحله 3: روی سرور

### اولین بار:
```bash
cd /home
git clone https://github.com/yekaweb/dlbot-telegram.git
cd dlbot-telegram
pip3 install -r requirements.txt
nano .env  # محتویات .env خود را بسازی
python3 main.py
```

### برای آپدیت:
```bash
cd /home/dlbot-telegram
git pull
pip3 install -r requirements.txt
# دوباره start کن
```

---

## مرحله 4: اجرای دائم روی سرور (tmux)

```bash
# اولین بار
tmux new-session -d -s dlbot
tmux send-keys -t dlbot "cd /home/dlbot-telegram && python3 main.py" Enter

# بررسی وضعیت
tmux list-sessions

# دوباره وصل شو
tmux attach -t dlbot

# بیرون برو (Ctrl+B سپس D)
```

---

## 🛑 اهم نکات

❌ **هرگز push نکن:**
- `.env` (رازهای سرور)
- `*.db` (database)
- `__pycache__` (cache)
- `venv/` (virtual env)

✅ **پوش کن:**
- `*.py` (code)
- `requirements.txt` (dependencies)
- `*.md` (documentation)

---

## 🔑 Token GitHub

1. https://github.com/settings/tokens
2. **Generate new token (classic)**
3. انتخاب کن: `repo`, `workflow`
4. **Generate token**
5. **کپی کن** (دوباره نظر نخواهی کرد!)

---

## توضیح برای جاهای گیج‌کننده

**"Username" در Push:**
- نام کاربری GitHub (مثل: `ali1234`)

**"Password" در Push:**
- Token که ساختی (نه رمز حساب!)
- مثل: `ghp_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`

---

## مثال واقعی

```powershell
# کامپیوتر محلی
cd D:\project
git add .
git commit -m "Add new features"
git push

# سرور
ssh root@192.168.1.100
cd /home/dlbot-telegram
git pull
python3 main.py
```

---

**بیشتر کمک می‌خوای؟ بگو! 😊**
