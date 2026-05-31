# 🚀 DLBot - Production Deployment Guide

**Status:** ✅ Fixed & Ready for Production  
**Updated:** 2026-05-31  
**Version:** 3.0 Enhanced Professional  

---

## ⚡ Quick Start (5 minutes)

### For Server/Production:
```bash
# 1. Clone project
git clone https://github.com/yekaweb/dlbot-telegram.git
cd dlbot-telegram

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies (clean, production-only)
pip install -r requirements_production.txt

# 4. Verify configuration
cat .env | grep -E "BOT_TOKEN|PYROGRAM"

# 5. Test imports
python3 test_imports.py

# 6. Start bot
python3 main.py
```

If bot responds to `/start` command, you're ready! 🎉

---

## 🔧 Issues & Fixes

### Issue 1: Bot doesn't respond to `/start`
**Status:** ✅ FIXED

**Changes Made:**
1. Enhanced logging in `main.py` - now shows detailed startup info
2. Improved error handling in `cmd_start` handler (loader)
3. Added try-catch blocks with meaningful error messages
4. Better import validation

**How to Verify:**
```bash
tail -50 logs/dlbot.log | grep -i start
# Should show: ✅ /start command received
```

### Issue 2: Python dependencies conflicts
**Status:** ✅ FIXED

**Changes Made:**
1. Created `requirements_production.txt` with only essential packages
2. Removed problematic packages (passlib 1.7.4, ffmpeg-python)
3. Tested on Python 3.10, 3.11, 3.12

**Install Clean:**
```bash
pip install -r requirements_production.txt
```

### Issue 3: Button handlers not working
**Status:** ✅ FIXED

**Changes Made:**
1. Added 6 callback_query handlers:
   - `handle_download_menu` - 📥 دانلود ویدیو
   - `handle_profile` - 👤 پروفایل
   - `handle_settings` - ⚙️ تنظیمات
   - `handle_guide` - 📚 راهنما
   - `handle_about` - ❓ درباره
   - `handle_back_main` - Back to menu

2. All handlers properly registered with `@dp.callback_query(F.data == "...")`

**How to Test:**
1. Send `/start` command
2. Click on any button
3. Should see relevant response

---

## 📂 Files Modified/Created

| File | Type | Status | Description |
|------|------|--------|-------------|
| `main.py` | Modified | ✅ Fixed | Enhanced error logging, better startup messages |
| `bot/loader_professional_enhanced.py` | Modified | ✅ Fixed | Added button handlers, improved /start logging |
| `requirements_production.txt` | Created | ✅ NEW | Clean production dependencies |
| `test_imports.py` | Created | ✅ NEW | Dependency validation script |
| `DEPLOYMENT_AND_FIXING_GUIDE.md` | Created | ✅ NEW | Complete deployment guide |
| `BUTTON_HANDLERS_IMPLEMENTATION.md` | Created | ✅ NEW | Button handlers documentation |
| `deploy_and_push.bat` | Created | ✅ NEW | Windows deployment script |
| `deploy_and_push.sh` | Created | ✅ NEW | Linux deployment script |

---

## 🎯 How to Deploy Properly

### Step 1: Test Locally First
```bash
python3 test_imports.py
python3 main.py
# Send /start to bot, verify it responds
```

### Step 2: Commit Changes
```bash
# Option A: Automatic (Recommended)
bash deploy_and_push.sh          # Linux/Mac
deploy_and_push.bat              # Windows

# Option B: Manual
git add .
git commit -m "fix: /start command handler and button callbacks

- Added logging to diagnose startup issues
- Implemented all 6 menu button handlers
- Created clean production requirements
- Enhanced error handling throughout

Fixes: Bot not responding to /start"

git push origin main
```

### Step 3: Deploy to Server
```bash
# SSH into server
ssh user@server.ip

# Navigate to project
cd /path/to/dlbot-telegram

# Pull latest changes
git pull origin main

# Reinstall dependencies (just in case)
pip install -r requirements_production.txt

# Start bot with systemd (recommended)
sudo systemctl restart dlbot

# Check logs
journalctl -u dlbot -f
```

---

## 🖥️ Server Setup (First Time)

### Create systemd Service File
```bash
sudo nano /etc/systemd/system/dlbot.service
```

**Paste:**
```ini
[Unit]
Description=DLBot - Telegram Downloader Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dlbot-telegram
ExecStart=/home/ubuntu/dlbot-telegram/venv/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable dlbot
sudo systemctl start dlbot
sudo systemctl status dlbot

# View real-time logs
sudo journalctl -u dlbot -f

# Stop bot
sudo systemctl stop dlbot
```

---

## 📊 Testing Checklist

Before deployment, verify all items:

- [ ] **Import Test:** `python3 test_imports.py` passes
- [ ] **Bot Token:** `echo $BOT_TOKEN | head -c 20` shows token
- [ ] **Bot Startup:** `python3 main.py` starts without errors
- [ ] **/start Command:** Responds with menu in Telegram
- [ ] **Menu Buttons:** All 5 buttons respond when clicked
- [ ] **Download Flow:** Can submit URL and download
- [ ] **Large Files:** >50MB files upload via Pyrogram
- [ ] **Logs:** No ERROR or CRITICAL messages
- [ ] **Performance:** Bot responds within 1 second
- [ ] **Cleanup:** Temp files are deleted after download

---

## 🚨 Troubleshooting

### Bot Starts But Doesn't Respond
```bash
# Check logs
tail -100 logs/dlbot.log

# Verify token is valid
curl "https://api.telegram.org/bot{TOKEN}/getMe"

# Restart bot
pkill -f "python3 main.py"
sleep 2
python3 main.py
```

### Import Errors
```bash
# Clean install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_production.txt
```

### Pyrogram Session Issues
```bash
# Remove old sessions
rm -f *.session*
rm -f *.session-journal

# Restart - will create new session
python3 main.py
```

### Memory/CPU Issues
```bash
# Check resource usage
htop

# Kill hanging processes
pkill -9 python3

# Restart systemd service
sudo systemctl restart dlbot
```

---

## 🔍 Monitoring

### Real-time Logs
```bash
# Docker
docker logs -f dlbot

# Systemd
sudo journalctl -u dlbot -f

# Direct file
tail -f logs/dlbot.log
```

### Performance
```bash
# Check if bot is running
ps aux | grep "python3 main.py"

# Check resource usage
ps aux | grep dlbot | awk '{print $2, $6, $7}'  # PID, Memory, CPU Time
```

---

## 🔐 Security Notes

✅ **Safe Practices:**
- BOT_TOKEN never in code, only in .env
- .env never committed to git (.gitignore has it)
- PYROGRAM credentials only in .env
- Logs don't contain sensitive data
- File uploads cleaned up automatically

---

## 📞 Need Help?

1. **Check logs first:** `tail -100 logs/dlbot.log`
2. **Run test:** `python3 test_imports.py`
3. **Check connectivity:** `curl https://api.telegram.org`
4. **Review guide:** `DEPLOYMENT_AND_FIXING_GUIDE.md`

---

## 🎉 What's Working

✅ Auto-detect platform (YouTube, Instagram, Twitter, etc.)  
✅ 8-step FSM download flow  
✅ Real-time progress updates  
✅ Multiple quality/codec options  
✅ Subtitle detection  
✅ Exact file size display  
✅ Unlimited file uploads (Pyrogram)  
✅ Temp file cleanup  
✅ Full error handling  
✅ Comprehensive logging  
✅ All menu buttons functional  

---

**Status: PRODUCTION READY** ✅

