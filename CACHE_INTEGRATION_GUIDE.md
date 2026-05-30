# 🔧 Integration Instructions - Cache System into Bot

## 📌 Quick Integration Checklist

- [ ] Add database model imports to `bot/loader_fsm_exact.py`
- [ ] Add cache check in URL handler
- [ ] Add cache selection handlers
- [ ] Add cleanup after successful upload
- [ ] Create database migration
- [ ] Test end-to-end

---

## 1️⃣ Update Imports in `bot/loader_fsm_exact.py`

Add these imports at the top:

```python
from bot.handlers.cache_handler import (
    check_and_show_cache,
    handle_cached_file_selection,
    deliver_cached_file,
    cleanup_and_save_cache,
)
from utils.cache_handler import CacheManager
from database.connection import SessionLocal  # or your DB connection
```

---

## 2️⃣ Modify URL Handler to Check Cache

In the `@dp.message(Command("download"))` or URL handler:

**BEFORE:**
```python
@dp.message(DownloadStates.waiting_for_url)
async def handle_url(message: Message, state: FSMContext):
    url = message.text.strip()
    
    # Validate and proceed...
    await state.set_state(DownloadStates.selecting_format_type)
    await message.answer("Select format...")
```

**AFTER:**
```python
@dp.message(DownloadStates.waiting_for_url)
async def handle_url(message: Message, state: FSMContext):
    url = message.text.strip()
    
    # ✅ Check cache first!
    db_session = SessionLocal()  # Get DB session
    has_cache = await check_and_show_cache(
        user_id=message.from_user.id,
        source_url=url,
        message=message,
        state=state,
        db_session=db_session
    )
    db_session.close()
    
    if has_cache:
        # User will select from cache or request new format
        return
    
    # No cache - proceed with normal flow
    await state.set_state(DownloadStates.selecting_format_type)
    await message.answer("Select format...")
```

---

## 3️⃣ Add Cache Selection Handlers

Add these handlers to `bot/loader_fsm_exact.py`:

```python
from bot.handlers.cache_handler import handle_cached_file_selection, deliver_cached_file

# Handler for selecting a cached file
@dp.callback_query(DownloadStates.selecting_cached_file, F.data.startswith("cache_select:"))
async def on_select_cached(query: CallbackQuery, state: FSMContext):
    """User selected a cached file"""
    db_session = SessionLocal()
    await handle_cached_file_selection(query, state, db_session)
    db_session.close()

# Handler for "🆕 دانلود فرمت جدید"
@dp.callback_query(F.data == "cache_new_format")
async def on_new_format(query: CallbackQuery, state: FSMContext):
    """User wants to download new format"""
    await query.message.edit_text(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard()
    )
    await state.set_state(DownloadStates.selecting_format_type)
    await query.answer()

# Handler for delivering cached file
@dp.callback_query(F.data == "cache_download")
async def on_download_cached(query: CallbackQuery, state: FSMContext):
    """User wants to download cached file"""
    db_session = SessionLocal()
    await deliver_cached_file(query, state, bot, db_session)
    db_session.close()

# Handler for deleting cached file
@dp.callback_query(F.data == "cache_delete")
async def on_delete_cached(query: CallbackQuery, state: FSMContext):
    """User wants to delete cached file"""
    session_data = await state.get_data()
    cached_file = session_data.get("selected_cached_file")
    
    if cached_file:
        db_session = SessionLocal()
        cache_manager = CacheManager(db_session)
        success = await cache_manager.delete_cached_download(cached_file.get("id"))
        db_session.close()
        
        if success:
            await query.answer("✅ فایل کش حذف شد", show_alert=False)
            await query.message.delete()
        else:
            await query.answer("❌ خطا", show_alert=True)
    
    await state.clear()

# Handler for cancel
@dp.callback_query(F.data == "download_cancel")
async def on_cancel(query: CallbackQuery, state: FSMContext):
    """Cancel operation"""
    await query.message.delete()
    await query.answer("✅ لغو شد")
    await state.clear()
```

---

## 4️⃣ Add Cleanup After Upload

After successful video/audio upload to Telegram:

**BEFORE:**
```python
# Upload video
sent_message = await message.reply_video(video=file_path)
# File still on server!
```

**AFTER:**
```python
# Upload video
sent_message = await message.reply_video(video=file_path)

# ✅ Save to cache and cleanup
if sent_message.video:
    db_session = SessionLocal()
    await cleanup_and_save_cache(
        file_path=file_path,
        telegram_file_id=sent_message.video.file_id,
        source_url=session["url"],
        source_platform="youtube",  # or detected platform
        media_info={
            "title": media_info.get("title"),
            "duration": media_info.get("duration"),
            "width": media_info.get("width"),
            "height": media_info.get("height"),
            "uploader": media_info.get("uploader"),
        },
        quality=session["quality"],
        format_codec=session["codec"],
        format_container="mp4",  # based on quality/codec
        db_session=db_session
    )
    db_session.close()
```

---

## 5️⃣ Create Database Migration

If using Alembic:

```bash
cd /path/to/project

# Generate migration
alembic revision --autogenerate -m "Add cached_downloads table"

# Edit migration file and verify

# Apply
alembic upgrade head
```

Or manually create table:

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

## 6️⃣ Background Cleanup Scheduler

Add to `main.py`:

```python
import asyncio
from utils.file_cleanup import start_cleanup_scheduler

async def main():
    # ... existing code ...
    
    # Start background cleanup (runs every 60 minutes)
    asyncio.create_task(start_cleanup_scheduler(interval_minutes=60))
    
    # Run bot
    await dp.start_polling(bot)
```

---

## 7️⃣ Testing

**Test Case 1: First Download (No Cache)**
```
1. Send URL: /start → /download → "https://youtube.com/watch?v=xxx"
2. Should show: "Select format (Video/Audio)"
3. Select Video → Select Quality → Select Codec
4. Bot downloads and uploads to Telegram
5. Check: temp file deleted, cache record created
```

**Test Case 2: Same URL Again (Cache Hit)**
```
1. Send same URL again
2. Should show: "2 فایل داخل دیتابیس پیدا شد"
3. Select cached version
4. Should get: ⚡ instant delivery (from Telegram)
5. Check: download_count incremented, last_used_at updated
```

**Test Case 3: New Format for Cached URL**
```
1. Send same URL again
2. Select cached version → Click "🆕 دانلود فرمت جدید"
3. Select different quality/codec
4. Bot downloads new format
5. Check: new cache record created
```

---

## ✅ Verification Checklist

- [ ] Can see exact file sizes
- [ ] Cache shows for repeated URLs
- [ ] Can deliver cached file instantly
- [ ] Temp files are deleted after upload
- [ ] Database has cached records
- [ ] Can download new format from cached URL
- [ ] Old temp files auto-cleanup (after 48h)

---

## 🐛 Troubleshooting

### Cache not showing for same URL
- Check: `source_url` matches exactly (without query params)
- Solution: Normalize URL before saving

### Temp file not deleted
- Check: File permissions
- Solution: Run cleanup manually: `FileCleanup.cleanup_temp_directory()`

### Cached file_id becomes invalid
- Telegram file_id can expire after 24h
- Solution: Re-download and update cache

### Database connection fails
- Check: Database is running
- Solution: Use `SessionLocal()` properly with try/except

---

## 📚 Related Files

- Full guide: `CACHING_AND_CLEANUP_GUIDE.md`
- Models: `database/models/cached_download.py`
- Utils: `utils/cache_handler.py`, `utils/file_cleanup.py`
- Handlers: `bot/handlers/cache_handler.py`
- Keyboards: `bot/keyboards/inline/cached_files.py`

---

## 🚀 Deploy

When done with integration:

```bash
# Run deployment script
.\FINAL_DEPLOYMENT.bat

# Or manually:
git add -A
git commit -m "Integrate cache system"
git push origin main

# On server:
ssh root@turkeyserver
cd /home/dlbot-telegram
git pull origin main
pkill -9 -f "python.*main.py"
python3 main.py
```

---

**Status: ✅ Ready for Integration**

All files created and documented. Just follow the 7 steps above to integrate into your bot!
