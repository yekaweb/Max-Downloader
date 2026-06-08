# 🎯 Quick Start Guide - نقشه راه سریع

## 5 دقیقه خلاصه

### چه چیزی می‌خواهیم انجام دهیم؟
```
دو برابر سریع‌تر + 40% کوچک‌تر + 60% کم‌تر انتظار = 🚀 سیستم بهتر
```

---

## 🚀 فازهای اصلی

### Phase 1: 🔵 Caching - فایل‌های تکراری (هفته 1-2)
**مسئله:** دوباره دانلود می‌شود
**حل:** ذخیره file_id تلگرام

```
قبل: User A → 2min → دانلود → آپلود
      User B → 2min → دانلود (دوباره!)
      
بعد:  User A → 2min → دانلود → آپلود
      User B → 0.5s → از حافظه
```

**کار:** 
- [ ] Database model برای کش
- [ ] Check cache قبل از دانلود
- [ ] Clean up قدیمی‌ها

**فایلها:** `database/models/cached_download.py`, `services/cache_service.py`

---

### Phase 2: 🟡 Parallel Download - دانلود همزمان (هفته 2-3)
**مسئله:** یکی پس از یکی دانلود می‌شود
**حل:** 3 دانلود همزمان

```
قبل: File1 (2min) → File2 (2min) → File3 (2min) = 6 minutes
      
بعد:  File1 (2min)
      File2 (2min) 🔄 همزمان
      File3 (2min)
      ────────────
      2 minutes total ⚡⚡
```

**کار:**
- [ ] ThreadPoolExecutor برای 3 workers
- [ ] Queue برای ترتیب
- [ ] Progress tracking

**فایلها:** `services/parallel_download_service.py`

---

### Phase 3: 🟢 Stream Upload - آپلود جریانی (هفته 3-4)
**مسئله:** تمام فایل دانلود شود، سپس آپلود شود
**حل:** حین دانلود آپلود کن

```
قبل: Download [████████] → Upload [████████] = 4 minutes
      
بعد:  Download [████████]
      Upload      [████████] 🔄 همزمان
      ────────────────────── = 2.5 minutes ⚡⚡
```

**کار:**
- [ ] Read file in chunks
- [ ] Upload while downloading
- [ ] Memory management

**فایلها:** `services/stream_upload_service.py`

---

### Phase 4: 🟠 Compression - کمپرس (هفته 4-5)
**مسئله:** فایل‌های بزرگ
**حل:** FFmpeg کمپرس هوشمند

```
قبل: 100MB → Upload (طولانی)
      
بعد:  100MB → Compress → 60MB → Upload (سریع‌تر) 📉
```

**کار:**
- [ ] FFmpeg wrapper
- [ ] Adaptive compression برای platforms مختلف
- [ ] Quality preservation

**فایلها:** `services/compression_service.py`

---

### Phase 5: 🔴 Queue Management - مدیریت صف (هفته 5-6)
**مسئله:** 30 دقیقه انتظار
**حل:** Priority queue + resource management

```
قبل: 30 users × 2min = 60 minutes انتظار = 😱
      
بعد:  3 concurrent × 2min + smart queuing = 10 minutes ⚡⚡⚡
```

**کار:**
- [ ] Priority queue
- [ ] Resource monitoring
- [ ] User notifications

**فایلها:** `services/queue_service.py`, `bot/handlers/queue_status.py`

---

## 📊 نتیجه نهایی

| Feature | قبل | بعد | بهبود |
|---------|-----|-----|-------|
| دانلود مجدد | 2min | 0.5s | ✨ 99% |
| 3 فایل | 6min | 2min | ⚡ 67% |
| اندازه فایل | 100MB | 60MB | 📉 40% |
| انتظار | 30min | 10min | 🎯 67% |

---

## 🎬 شروع فوری

### گام 1: شاخه جدید
```bash
cd /home/reza/Max-Downloader
git checkout -b feature/enhancements-v2
```

### گام 2: Requirements
```bash
# بیفزایید به requirements_enhancements.txt:
psutil>=5.9.0
aiofiles>=0.8.0
yt-dlp>=2023.01.01
```

### گام 3: شروع Phase 1
```bash
# ایجاد فایل مدل
touch database/models/cached_download.py
```

### گام 4: Test
```bash
pytest tests/ -v
```

### گام 5: Push
```bash
git add .
git commit -m "feat: Phase 1 - Caching system"
git push origin feature/enhancements-v2
```

---

## 📈 Performance Dashboard

```
Current System:
┌──────────────────────────────────────┐
│ Cache Hit Time      : N/A           │
│ Parallel Downloads  : 1 only        │
│ Upload Speed        : 1x            │
│ File Size           : 100MB avg     │
│ Queue Wait          : 30 min avg    │
│ Total Throughput    : 0.5 files/min │
└──────────────────────────────────────┘

After All Phases:
┌──────────────────────────────────────┐
│ Cache Hit Time      : 0.5s ✨       │
│ Parallel Downloads  : 3 concurrent  │
│ Upload Speed        : 1.5x ⚡      │
│ File Size           : 60MB avg 📉   │
│ Queue Wait          : 10 min avg 🎯 │
│ Total Throughput    : 1.5 files/min │
└──────────────────────────────────────┘
```

---

## ⚠️ مهم

1. **Phase 1** می‌تواند جدا اجرا شود
2. **Phase 2** بهتر است بعد از Phase 1
3. **Phase 3** نیاز به Phase 2 دارد
4. **Phase 4** می‌تواند هر زمان اضافه شود
5. **Phase 5** تمام phases را یکی‌کند

---

## 🆘 اگر مشکل داشتید

1. **Logs را بخوانید:**
   ```bash
   tail -f logs/bot.log | grep -i error
   ```

2. **Database را بررسی کنید:**
   ```bash
   sqlite3 db.sqlite3 "SELECT * FROM cached_downloads LIMIT 5;"
   ```

3. **Resources را بررسی کنید:**
   ```bash
   top
   ```

4. **Rollback کنید (اگر لازم بود):**
   ```bash
   git revert <commit-hash>
   ```

---

## 📞 سوالات متداول

**Q: چقدر زمان می‌برد؟**
A: ~ 8-10 هفته برای تمام phases (می‌تونی هر فاز رو جدا انجام دهی)

**Q: رول‌بک آسان است؟**
A: بله! هر phase بصورت مستقل است

**Q: باید تمام phase‌ها انجام دهم؟**
A: نه! می‌تونی Phase 1 و 2 رو شروع کنی، Phase 5 اختیاری است

**Q: آیا کوالیتی کاهش می‌یابد؟**
A: نه! کمپرس بصورت هوشمند است (تقریبا بدون تغییر)

---

## 🎯 Checklist برای شروع

- [ ] Read ROADMAP.md کامل
- [ ] Create feature branch
- [ ] Install dependencies
- [ ] Create unit tests
- [ ] Start Phase 1
- [ ] Deploy to staging
- [ ] Test thoroughly
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Move to Phase 2

---

**نوشته شده:** 8 June 2026
**نسخه:** 1.0
