# 🚀 Download Bot - Caching & Cleanup System

## 📋 نمای کلی (Overview)

این ربات یک سیستم **حرفه‌ای برای دانلود و کش‌سازی** دارد که شامل:

### ✨ ویژگی‌های اصلی

1. **Exact File Sizes** ✅
   - دقیق حجم فایل را قبل از دانلود نشان می‌دهد
   - نه تخمینی!

2. **Smart Caching** 💾
   - اگر کاربری دوباره همان لینک بفرستد، فایل‌های قبلی را پیشنهاد می‌دهد
   - هیچ دانلود تکراری نخواهد بود

3. **File Cleanup** 🗑️
   - بعد از آپلود موفق به تلگرام، فایل محلی حذف می‌شود
   - صرفه‌جویی در فضای سرور

4. **Beautiful UI** 🎨
   - دکمه‌های شیشه‌ای برای انتخاب فایل‌های کش‌شده
   - نمایش دقیق اطلاعات (کیفیت، حجم، تاریخ، وضوح)

---

## 🗂️ ساختار فایل‌ها

### Database Models
```
database/models/
├── cached_download.py      ← جدول ذخیره‌ی فایل‌های کش‌شده
```

**Table: `cached_downloads`**
```sql
- id: Primary Key
- source_url: URL منبع (YouTube, Instagram, Twitter)
- source_platform: Platform (youtube, instagram, twitter)
- media_title: عنوان ویدیو
- telegram_file_id: شناسه فایل در تلگرام
- file_size: حجم دقیق (بایت)
- file_type: نوع MIME (video/mp4, audio/mpeg)
- quality: کیفیت (1080p, 720p, 320kbps)
- format_codec: کدک (h264, mp3, opus)
- format_container: ظرف (mp4, mkv, m4a)
- resolution_width/height: وضوح ویدیو
- media_duration: مدت زمان (ثانیه)
- download_count: تعداد دفعات استفاده
- created_at: زمان کش‌سازی
- last_used_at: آخرین استفاده
```

### Utilities
```
utils/
├── cache_handler.py        ← مدیریت کش
├── file_cleanup.py         ← حذف فایل‌های محلی
└── format_sizes.py         ← محاسبه حجم دقیق
```

### Bot Handlers
```
bot/handlers/
├── cache_handler.py        ← مدیریت جریان کش
```

### Keyboards
```
bot/keyboards/inline/
├── cached_files.py         ← دکمه‌های انتخاب فایل‌های کش‌شده
```

### States
```
bot/states/download.py      ← FSM states (با cache states جدید)
```

---

## 🔄 جریان کار (Workflow)

### سناریو 1: اولین دانلود
```
1. کاربر URL می‌فرستد
2. ربات چک می‌کند: آیا این URL قبلاً دانلود شده؟
   - NO → ادامه جریان عادی
3. کاربر کیفیت/فرمت را انتخاب می‌کند
4. دانلود + آپلود
5. ✅ بعد از آپلود موفق:
   - فایل محلی حذف می‌شود
   - file_id و metadata در database ذخیره می‌شود
```

### سناریو 2: دانلود تکراری (Cached)
```
1. کاربر URL می‌فرستد
2. ربات چک می‌کند: آیا این URL قبلاً دانلود شده؟
   - YES ✅ → نمایش فایل‌های کش‌شده
3. کاربر یک گزینه انتخاب می‌کند یا "🆕 فرمت جدید"
4. اگر انتخاب شده:
   - ⚡ بدون دانلود دوباره، فایل ارسال می‌شود
   - دریافت از تلگرام cache (بسیار سریع!)
5. اگر "🆕 فرمت جدید":
   - جریان عادی دانلود شروع می‌شود
```

---

## 💻 استفاده در کد

### 1️⃣ Check Cache
```python
from bot.handlers.cache_handler import check_and_show_cache

# When URL is received:
has_cache = await check_and_show_cache(
    user_id=message.from_user.id,
    source_url=url,
    message=message,
    state=state,
    db_session=db_session
)

if has_cache:
    # Show cached files - user will select one
    return

# No cache - continue normal flow
```

### 2️⃣ Save to Cache (after successful upload)
```python
from bot.handlers.cache_handler import cleanup_and_save_cache

# After message.reply_video() or message.reply_document() succeeds:
await cleanup_and_save_cache(
    file_path="/path/to/downloaded/file.mp4",
    telegram_file_id=sent_message.video.file_id,  # from Telegram response
    source_url="https://youtube.com/watch?v=xxx",
    source_platform="youtube",
    media_info={
        "title": "Video Title",
        "duration": 348,
        "width": 1920,
        "height": 1080,
        "uploader": "Uploader Name",
    },
    quality="1080p",
    format_codec="h264",
    format_container="mp4",
    db_session=db_session
)
```

### 3️⃣ Handle Cached File Selection
```python
from bot.handlers.cache_handler import handle_cached_file_selection

@dp.callback_query(F.data.startswith("cache_select:"))
async def on_cache_select(query: CallbackQuery, state: FSMContext):
    await handle_cached_file_selection(query, state, db_session)
```

### 4️⃣ Deliver Cached File
```python
from bot.handlers.cache_handler import deliver_cached_file

@dp.callback_query(F.data == "cache_download")
async def on_cache_download(query: CallbackQuery, state: FSMContext):
    await deliver_cached_file(query, state, bot, db_session)
```

### 5️⃣ File Cleanup
```python
from utils.file_cleanup import FileCleanup

# Delete file after upload (called automatically in cleanup_and_save_cache)
await FileCleanup.cleanup_after_upload(
    file_path="/path/to/file.mp4",
    delay_seconds=5  # Wait 5 seconds before deleting
)

# Or cleanup old temp files (background task)
deleted_count = await FileCleanup.cleanup_temp_directory(max_age_hours=48)
```

---

## 🎨 UI Example

### فایل‌های کش‌شده برای یک لینک
```
✅ 2 فایل داخل دیتابیس پیدا شد

برای ادامه و دریافت فرمت های بیشتر روی دکمه 🆕 کلیک کنید.

شماره: 1
اسم: معماری تونل ریورس پنل به پنل ثنایی
اندازه: 10.68 MB
دانلود شده در: 2026-05-26 10:47:28
زمان: 00:05:48
نوع: video/x-matroska
کیفیت: 720p | کدک: vp9
وضوح: 1280x720
تعداد دفعات استفاده: 3
────────────────

شماره: 2
اسم: معماری تونل ریورس پنل به پنل ثنایی
اندازه: 14.62 MB
دانلود شده در: 2026-05-12 23:14:46
زمان: 00:05:48
نوع: video/mp4
کیفیت: 1080p | کدک: h264
وضوح: 1920x1080
تعداد دفعات استفاده: 5
────────────────

[1️⃣ 1080p  ] [2️⃣ 720p]
[🆕 فرمت جدید] [❌ لغو]
```

### بعد از انتخاب فایل
```
✅ فایل انتخاب شد

📺 نام: معماری تونل ریورس...
📊 کیفیت: 1080p
💾 حجم: 14.62 MB
🎬 نوع: video/mp4

اکنون می‌توانید:
1. ✅ دانلود - فایل کش‌شده را ارسال کنید
2. 🔄 فرمت دیگر - کیفیت یا فرمت جدیدی دانلود کنید
3. ❌ حذف - این کش را حذف کنید

[✅ دانلود] [🔄 فرمت دیگر] [❌ حذف]
[◀️ برگشت]
```

---

## 📊 Database Schema

```sql
CREATE TABLE cached_downloads (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    source_url VARCHAR(2048) NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    media_title VARCHAR(500) NOT NULL,
    telegram_file_id VARCHAR(255) UNIQUE NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    quality VARCHAR(100) NOT NULL,
    format_codec VARCHAR(50) NOT NULL,
    format_container VARCHAR(20) NOT NULL,
    resolution_width INT,
    resolution_height INT,
    media_duration INT,
    media_uploader VARCHAR(255),
    download_count INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    INDEX(source_url),
    INDEX(source_platform),
    INDEX(telegram_file_id),
    INDEX(created_at)
);
```

---

## 🔒 بهترین‌الممارسات (Best Practices)

### 1. Always Cleanup Files ✅
```python
# GOOD - Async cleanup after upload
try:
    sent = await bot.send_video(chat_id, video=file_path)
    await cleanup_and_save_cache(file_path, sent.video.file_id, ...)
except Exception as e:
    logger.error(f"Upload failed: {e}")
    # Still cleanup failed file
    await FileCleanup.cleanup_after_upload(file_path)
```

### 2. Store EXACT file_id ✅
```python
# From Telegram send response:
sent_message = await bot.send_video(...)
telegram_file_id = sent_message.video.file_id  # IMPORTANT: Get from response

# Store this exact file_id for later use
await cache_manager.save_cached_download(..., telegram_file_id=telegram_file_id)
```

### 3. Use Cached file_id for Delivery ✅
```python
# DON'T re-download and re-send
# Instead, use cached file_id:
await bot.send_video(
    chat_id=user_id,
    video=cached.telegram_file_id  # ⚡ Much faster!
)
```

### 4. Run Cleanup Scheduler
```python
# In main.py, start background cleanup:
from utils.file_cleanup import start_cleanup_scheduler

asyncio.create_task(start_cleanup_scheduler(interval_minutes=60))
```

---

## ⚠️ Common Issues

### Issue: "File not found" when cleanup
**Solution:** File already deleted or path error
```python
# Use proper path handling:
from pathlib import Path
file_path = Path(filename)
if file_path.exists():
    file_path.unlink()
```

### Issue: Cache not showing for same URL
**Solution:** Check source_url matches exactly
```python
# URL with query parameters:
https://youtube.com/watch?v=xxx&t=10  # Different URL!
https://youtube.com/watch?v=xxx       # Different from above

# Normalize URLs:
source_url = url.split('&')[0]  # Remove query params
```

### Issue: Cached file_id becomes invalid
**Solution:** Telegram file_id can expire after 24 hours if not used
```python
# Re-download if file_id fails:
try:
    await bot.send_video(chat_id, video=cached.telegram_file_id)
except Exception:
    # File_id expired - delete from cache and re-download
    await cache_manager.delete_cached_download(cached.id)
```

---

## 📈 Performance Benefits

### Before (No Caching)
- 10 users, same video: 10x downloads (10 GB)
- Each delivery: ~5 minutes

### After (With Caching)
- 10 users, same video: 1x download (1 GB)
- Each delivery: ~5 seconds (from Telegram cache)

**Savings: 90% bandwidth, 99% faster delivery!** 🚀

---

## 🎯 Next Steps

1. Integrate cache check into `loader_fsm_exact.py`
2. Add database migration for `cached_downloads` table
3. Run background cleanup scheduler
4. Monitor cache size and auto-cleanup if needed
5. Add analytics (most cached videos, cache hit rate, etc)

---

## 📞 Support

- **Issues with cleanup?** Check file permissions and paths
- **Cache not working?** Verify database connection
- **Telegram file_id expired?** Implement re-download fallback
- **Out of disk space?** Increase cleanup frequency

**Remember:** Cache is optional - bot works fine without it. But with cache, you get 10x better performance! 🔥
