# 🗺️ نقشه راه بازسازی حرفه‌ای پروژه DLBot
**پوشه:** `antigravity_analyze/project_rebuild_roadmap/`  
**هدف:** تبدیل skeleton فعلی به محصول تجاری قابل فروش بر اساس `We want build this.md`  
**تاریخ شروع:** ۲۰۲۶-۰۶-۱۰

---

## 📂 ساختار این پوشه

```
project_rebuild_roadmap/
├── 00_MASTER_ROADMAP.md          ← این فایل — نقشه کلی
├── SPRINT_1_cleanup.md           ← Sprint 1: پاکسازی و refactor
├── SPRINT_2_core_fix.md          ← Sprint 2: اصلاح هسته دانلود
├── SPRINT_3_features.md          ← Sprint 3: ویژگی‌های اصلی
├── SPRINT_4_monetization.md      ← Sprint 4: سیستم پرداخت و اشتراک
├── SPRINT_5_platforms.md         ← Sprint 5: پلتفرم‌های بیشتر
└── SPRINT_6_production.md        ← Sprint 6: آماده‌سازی production
```

---

## 🏗️ معماری هدف (بر اساس We want build this.md)

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Bot (aiogram 3.4.1)              │
│                                                             │
│  bot/loader.py ← تنها یک loader تمیز                        │
│  bot/handlers/ ← handler های مجزا و کوچک                   │
│  bot/middlewares/ ← auth, i18n, rate_limit, force_join      │
│  bot/keyboards/ ← inline + reply keyboards                  │
│  bot/states/ ← FSM states                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Business Logic Layer                      │
│                                                             │
│  services/download_service.py  ← orchestrator اصلی         │
│  services/cache_service.py     ← Redis + DB cache           │
│  services/file_service.py      ← Pyrogram uploader          │
│  services/user_service.py      ← user CRUD + plan check     │
│  services/referral_service.py  ← coins + referral           │
│  services/payment_service.py   ← real payment gateways      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Module Layer (Pluggable)                  │
│                                                             │
│  modules/youtube/    ← yt-dlp integration                  │
│  modules/instagram/  ← instagrapi                           │
│  modules/twitter/    ← yt-dlp + Tweepy                     │
│  modules/tiktok/     ← yt-dlp                              │
│  modules/direct_link/← generic HTTP                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Infrastructure                            │
│                                                             │
│  PostgreSQL 15  ← primary DB                               │
│  Redis 7        ← cache + sessions + rate limit + queue     │
│  Celery 5       ← background tasks                          │
│  Docker         ← deployment                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 وضعیت فعلی در یک نگاه

| بخش | وضعیت | اولویت اصلاح |
|-----|--------|--------------|
| Architecture | ⚠️ God File دارد | 🔴 فوری |
| Dead Code | ❌ ~200KB کد مرده | 🔴 فوری |
| Download Logic | ❌ Quality selection کار نمی‌کند | 🔴 فوری |
| Config System | ⚠️ بدون validation | 🔴 فوری |
| FSM Storage | ❌ Memory (نه Redis) | 🔴 فوری |
| Payment | ❌ Fake URL | 🔴 فوری |
| TikTok | ❌ وجود ندارد | 🟡 مهم |
| i18n | ❌ Hardcoded strings | 🟡 مهم |
| Subscription Enforce | ❌ اجرا نمی‌شود | 🟡 مهم |
| Tests | ❌ تقریباً صفر | 🟡 مهم |
| File Cleanup | ⚠️ ناقص | 🟢 متوسط |
| Web Panel | ⚠️ Skeleton | 🟢 متوسط |
| Alembic | ❌ خالی | 🔴 فوری |

---

## 🗓️ Sprint Timeline

```
Sprint 1  (روز 1-3):   پاکسازی + ساختار تمیز
Sprint 2  (روز 4-7):   هسته دانلود واقعی
Sprint 3  (روز 8-12):  ویژگی‌های MVP
Sprint 4  (روز 13-17): پرداخت + اشتراک
Sprint 5  (روز 18-22): پلتفرم‌های بیشتر
Sprint 6  (روز 23-27): Production + تست
────────────────────────
مجموع:    ~27 روز کاری
```

---

## ✅ قوانین طلایی این بازسازی

1. **یک loader، یک مسئولیت** — `loader.py` فقط init می‌کند
2. **هر handler در فایل خودش** — max 200 خط per file
3. **هیچ string فارسی در کد** — همه از locale files
4. **هر feature تست دارد** — minimum happy path
5. **Session در Redis** — هرگز در memory
6. **Cleanup در finally** — همیشه فایل‌ها پاک می‌شوند
7. **خطاها categorize می‌شوند** — user error vs system error
8. **Quality selection واقعی** — انتخاب کاربر به yt-dlp منتقل می‌شود

---

## 📁 ساختار هدف پروژه (Final Target)

```
dlbot/
├── .env                          ✅ موجود (اصلاح نیاز دارد)
├── .env.example                  ✅ موجود
├── requirements.txt              ✅ موجود (نیاز به تمیزکاری)
├── docker-compose.yml            ✅ موجود
├── Dockerfile                    ✅ موجود
├── alembic.ini                   🔴 باید ایجاد شود (example موجود)
├── README.md                     ✅ موجود
├── main.py                       ⚠️ نیاز به اصلاح
├── config.py                     🔴 باید با Pydantic v2 بازنویسی شود
│
├── bot/
│   ├── __init__.py
│   ├── loader.py                 🔴 باید تمیز و کوچک باشد (فقط init)
│   ├── middlewares/
│   │   ├── auth.py               ✅ موجود (بررسی نیاز)
│   │   ├── i18n.py               🔴 باید پیاده‌سازی شود
│   │   ├── rate_limit.py         🔴 باید با Redis پیاده‌سازی شود
│   │   └── subscription.py       ⚠️ موجود (بررسی نیاز)
│   ├── handlers/
│   │   ├── start.py              ⚠️ موجود (اصلاح نیاز)
│   │   ├── url_handler.py        🔴 باید از loader استخراج شود
│   │   ├── format_handler.py     🔴 باید از loader استخراج شود
│   │   ├── download_exec.py      🔴 باید از loader استخراج شود
│   │   ├── cache_handler.py      🔴 باید از loader استخراج شود
│   │   ├── referral.py           ✅ موجود
│   │   ├── plans.py              ✅ موجود
│   │   ├── profile.py            ✅ موجود
│   │   └── admin/                ✅ موجود (بررسی نیاز)
│   ├── keyboards/
│   │   └── inline/
│   │       ├── download.py       ⚠️ موجود (اصلاح نیاز)
│   │       └── plans.py          ⚠️ موجود
│   └── states/
│       └── download.py           ✅ موجود
│
├── modules/
│   ├── __init__.py               ⚠️ موجود (اصلاح priority logic)
│   ├── base.py                   ✅ موجود
│   ├── youtube/                  ⚠️ موجود (format selection باید fix شود)
│   ├── instagram/                ⚠️ موجود (credential handling نیاز)
│   ├── twitter/                  ⚠️ موجود (URL normalization fix)
│   ├── tiktok/                   🔴 باید ایجاد شود
│   └── direct_link/              ✅ موجود
│
├── services/
│   ├── download_service.py       🔴 بازنویسی با format passthrough
│   ├── cache_service.py          ⚠️ موجود (اصلاح نیاز)
│   ├── file_service.py           ⚠️ موجود (session leak باید fix)
│   ├── user_service.py           ⚠️ موجود (subscription check باید add)
│   ├── referral_service.py       ✅ موجود
│   ├── payment_service.py        🔴 پیاده‌سازی واقعی gateway ها
│   ├── notification_service.py   ⚠️ موجود (APScheduler jobs)
│   └── stats_service.py          ⚠️ موجود
│
├── database/
│   ├── connection.py             ✅ موجود
│   ├── models/                   ✅ موجود (یک مدل اضافی دارد)
│   └── repositories/             ✅ موجود
│
├── tasks/
│   ├── celery_app.py             🔴 باید ایجاد شود
│   ├── download_tasks.py         🔴 باید ایجاد شود
│   └── cleanup_tasks.py          🔴 باید ایجاد شود
│
├── locales/
│   ├── fa/messages.json          🔴 باید کامل شود
│   ├── en/messages.json          🔴 باید کامل شود
│   └── ...
│
├── utils/
│   ├── progress.py               ⚠️ موجود (real values نیاز)
│   ├── formatters.py             ✅ موجود
│   └── validators.py             ✅ موجود
│
├── web/                          ⚠️ موجود (backend-template integration)
└── migrations/                   🔴 باید generate شود
```

---

## 🔗 وابستگی بین Sprint ها

```
Sprint 1 (پاکسازی)
    ↓
Sprint 2 (هسته دانلود)
    ↓
Sprint 3 (MVP Features) ─── نیاز به Sprint 1+2
    ↓
Sprint 4 (Payment) ─── نیاز به Sprint 3
    ↓
Sprint 5 (Platforms) ─── می‌تواند موازی با Sprint 4 باشد
    ↓
Sprint 6 (Production) ─── نیاز به همه Sprint ها
```

---

**فایل‌های بعدی این پوشه را مطالعه کنید:**
- [`SPRINT_1_cleanup.md`](./SPRINT_1_cleanup.md) — شروع کنید اینجا
- [`SPRINT_2_core_fix.md`](./SPRINT_2_core_fix.md)
- [`SPRINT_3_features.md`](./SPRINT_3_features.md)
- [`SPRINT_4_monetization.md`](./SPRINT_4_monetization.md)
- [`SPRINT_5_platforms.md`](./SPRINT_5_platforms.md)
- [`SPRINT_6_production.md`](./SPRINT_6_production.md)
