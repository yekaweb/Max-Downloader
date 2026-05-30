# 🔧 راهنمای نهایی - Fix کامل ربات

## 📍 کامپیوتر محلی

### 1. حذف فایل مشکل‌دار

```cmd
cd "d:\telgram bot md backup 2- Copy"
del bot\keyboards\inline.py
```

### 2. Commit و Push

```powershell
git status
git add -A
git commit -m "Fix: Remove duplicate inline.py"
git push
```

**بگو اگر:** 
```
✅ [main xxxxx] Fix: Remove duplicate inline.py
1 file changed, 1 deletion(-)
✅ To https://github.com/yekaweb/dlbot-telegram.git
```

---

## 🖥️ سرور

### 1. SSH

```bash
ssh root@turkeyserver
```

### 2. Update کد

```bash
cd /home/dlbot-telegram

# Kill old
pkill -9 -f "python3 main.py"

# Latest
git fetch origin
git reset --hard origin/main
git pull
```

### 3. Verify

```bash
# Check files
ls -la bot/keyboards/inline/
ls -la bot/handlers/download_handler.py
```

**باید دیدی:**
```
__init__.py (با دکمه‌های back)
download_handler.py (با handlers)
```

### 4. Start

```bash
python3 main.py
```

**باید دیدی:**
```
2026-05-30 | INFO | 🤖 Starting DLBot
2026-05-30 | INFO | ✅ Bot components loaded
2026-05-30 | INFO | 🚀 Starting bot polling...
```

---

## 📱 Test

1. `/start` ✅
2. روی "📥 دانلود ویدیو" بزن ✅ → **منوی پلتفرم ظاهر شود**
3. روی "🎥 YouTube" بزن ✅ → **منتظر URL**
4. روی "🔙 بازگشت" بزن ✅ → **منوی اصلی**

---

**اگر مشکل بود:** `tail -20 logs/dlbot.log`
