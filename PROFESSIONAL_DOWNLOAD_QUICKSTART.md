# 🚀 Professional Download System - Quick Start

**Just deployed a complete rewrite with Pyrogram support!**

---

## ⚡ What's New?

✅ Auto-detect URL platform (YouTube, Instagram, Twitter)  
✅ Direct URL support (no buttons required)  
✅ Real-time progress updates (one message, updated)  
✅ Pyrogram upload support (NO 50MB limit!)  
✅ 8-step FSM flow (per specification)  
✅ Exact file sizes for each codec  
✅ Automatic cleanup of temp files  

---

## 🔧 Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install pyrogram==2.0.106
pip install TgCrypto
pip install yt-dlp
```

### 2. Get Pyrogram Credentials
Go to **https://my.telegram.org**:
- Click "API development tools"
- Fill form (name: "dlbot", short name: "dlbot")
- Get your **APP_ID** and **APP_HASH**

### 3. Update `.env`
```env
PYROGRAM_APP_ID=123456789
PYROGRAM_APP_HASH=your_app_hash_here
PYROGRAM_SESSION_NAME=dlbot_session
```

### 4. Create Temp Directory
```bash
mkdir -p temp_downloads
```

### 5. Restart Bot
```bash
python main.py
```

---

## 🧪 Quick Test

Send to bot:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Expected flow:
1. Bot detects YouTube
2. Bot shows video info
3. Bot asks: Video or Audio?
4. Bot shows qualities with file sizes
5. Bot asks for codec
6. Bot downloads with progress updates
7. Bot uploads (auto-uses Pyrogram for large files)
8. ✅ Done!

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot write to closing transport" | Restart bot, clear `__pycache__` |
| "Request Entity Too Large" | Pyrogram not configured - check `.env` |
| Progress not updating | Normal (throttled to 1-2 sec updates) |
| File not uploaded | Check logs, Pyrogram might need auth |
| > 2GB file fails | Limit of Pyrogram, use smaller quality |

---

## 📊 Upload Limits

| Size | Method | Limit |
|------|--------|-------|
| < 50MB | aiogram | ✅ Works |
| 50-2000MB | Pyrogram | ✅ Works |
| 2-4GB | Pyrogram | ✅ Works |
| > 4GB | None | ❌ Not supported |

---

## 📝 Files Modified

- ✅ `bot/loader_professional.py` — NEW (complete rewrite)
- ✅ `main.py` — Updated import to new loader
- ✅ `PUSH_PROFESSIONAL.bat` — NEW (deployment script)

---

## 🚀 Deploy to Server

### Option 1: Manual
```bash
git add -A
git commit -m "feat: Professional download system"
git push origin main

# On server:
git pull origin main
python main.py
```

### Option 2: Use Deploy Script
```bash
./PUSH_PROFESSIONAL.bat
```

---

## ✅ Verification

After starting bot, check logs:

```
✅ Pyrogram client initialized (unlimited file uploads)
✅ Bot components loaded successfully (Professional Download System)
🚀 Bot starting (Professional Download System)...
📡 Bot is listening for updates...
```

If you see these messages, you're good to go!

---

## 🎯 Features Per Specification

| Feature | Status |
|---------|--------|
| STEP 1: URL Validation | ✅ Auto-detects platform |
| STEP 2: Fetch Media Info | ✅ Shows thumbnail, duration, views |
| STEP 3: Format Selection | ✅ Video/Audio |
| STEP 4A: Quality Selection | ✅ With exact file sizes |
| STEP 4B: Audio Format | ✅ MP3, AAC, OPUS options |
| STEP 5: Codec Selection | ✅ H.264, AV1, VP9 |
| STEP 6: Subtitle Selection | ✅ Multiple languages |
| STEP 7: Send As | ✅ Video/File |
| STEP 8: Progress Updates | ✅ Real-time, single message |

---

## 🔐 Security

- No credentials in code
- Temp files auto-deleted
- Proper error handling
- No stack traces to users

---

**Questions?** Check `PROFESSIONAL_DOWNLOAD_SYSTEM.md` for detailed docs.

**Status:** Ready to Deploy! 🎉
