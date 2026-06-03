# PHASE 3 — Merged Reference

Last updated: 2026-05-25

این فایل مرجع، تمام اسناد و گزارش‌های Phase 3 را بر حسب آخرین تغییرات دریافت‌شده ادغام و خلاصه می‌کند. هدف: یک منبع واحد و مرتب برای همه مدارک Phase 3 و پاک‌سازی فایل‌های پراکنده از پوشه پروژه.

---

**فهرست محتوا**
- خلاصه اجرایی
- وضعیت توسعه و پیشرفت هر ماژول
- جزئیات پیاده‌سازی و وابستگی‌ها
- تست‌ها و دستور اجرای آن‌ها
- قدم‌های بعدی و چک‌لیست استقرار
- فهرست فایل‌های ادغام‌شده

---

## خلاصه اجرایی

- وضعیت کلی Phase 3: پیاده‌سازی‌های اصلی (Instagram, TikTok, Twitter) تکمیل یا در وضعیت production-ready قرار دارند؛ مستندات و تست‌ها ایجاد شده‌اند. (گزارش‌ها بین 80% تا 100% می‌گویند؛ وضعیت نهایی وابسته به ایجاد دایرکتوری‌ها و اجرای تست‌های نهایی و تنظیم کلیدهای API است.)
- هدف این مرحله: افزودن دانلود چندسکویی به بات، با ماژول‌های خودثبت‌شونده و تست‌شده.

## وضعیت ماژول‌ها (خلاصه)

- Instagram: پیاده‌سازی واقعی با `instagrapi` — fetch metadata, عکس/ویدیو، reels، carousels، IGTV، خطاگیری برای حساب‌های خصوصی.
- TikTok: پیاده‌سازی با `yt-dlp` — استخراج metadata، دانلود و گزینه حذف watermark، انتخاب کیفیت، پشتیبانی از لینک‌های کوتاه.
- Twitter/X: اسکلت `tweepy` آماده، پشتیبانی از دانلود ویدیوها/تصاویر، thread/quote handling، normalization از x.com.
- Module system: auto-discovery و اولویت‌بندی روی ماژول‌ها؛ اگر لایبرری نصب نباشد با graceful fallback کار می‌کند.

## وابستگی‌ها

- در `requirements.txt` اضافه شده یا بررسی شود:
  - instagrapi==2.0.0
  - tweepy==4.14.0
  - yt-dlp==2024.5.27

نصب:
```bash
pip install -r requirements.txt
```

## تست‌ها

- فایل تست اصلی: `test_phase3_modules.py` شامل حدود 37 تست (URL detection, module registration, auto-discovery, format parsing).
- اجرای تست‌ها:
```bash
pytest test_phase3_modules.py -v
# انتظار: همه تست‌ها پاس شوند (در صورت ایجاد دایرکتوری TikTok)
```

## استقرار و آماده‌سازی

1. ایجاد ساختار دایرکتوری (در صورت نیاز):
```bash
cd "d:\telgram bot md backup 2- Copy"
python init_project.py
```
2. اجرای تست‌ها و بررسی registry ماژول‌ها:
```bash
python -c "from modules import get_all_downloaders; print(list(get_all_downloaders().keys()))"
```
3. به‌روزرسانی `bot/handlers/download.py` برای بهره‌گیری از `get_downloader()` و پردازش جدید کیفیت/دانلود طبق راهنمای ادغام.

## فایل‌های ادغام‌شده

این فایل مرجع از محتوای کامل یا خلاصه‌ی این فایل‌ها ساخته شد:
- PHASE_3_BOT_INTEGRATION_GUIDE.md
- PHASE_3_COMPLETION_FINAL.md
- PHASE_3_DEVELOPMENT_STATUS.md
- PHASE_3_DOCUMENTATION_INDEX.md
- PHASE_3_EXECUTIVE_SUMMARY.md
- PHASE_3_IMPLEMENTATION_COMPLETE.md
- PHASE_3_NEXT_STEPS.md
- PHASE_3_QUICK_REFERENCE.md
- PHASE_3_STARTER_GUIDE.md

## پیشنهادات و گام بعدی

1. اگر می‌خواهید فایل‌های اصلی حذف کامل شوند، هم‌اکنون این کار را انجام می‌دهم — در صورت تمایل می‌توانم به‌جای حذف، آن‌ها را در `archive/phase3/` منتقل کنم.
2. اجرای تست‌های نهایی و اتصال بات به ماژول‌ها (20–45 دقیقه). برای تست‌های زنده Instagram/Twitter نیاز به اعتبارنامه (credentials) دارید.

---

فایل مرجع ایجاد شد. اگر تأیید کنید، می‌توانم باقی عملیات (حذف یا آرشیو) را انجام دهم و `todo` را به‌روز کنم.
