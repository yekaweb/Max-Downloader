# 📋 پرامپت جامع و کامل برای Cursor

---

> نکته مهم درباره 4GB: دوستت احتمالاً از Pyrogram (MTProto) استفاده می‌کنه نه Bot API معمولی. ما هم همین رویکرد رو در معماری می‌ریم — aiogram برای منطق ربات + Pyrogram برای آپلود فایل‌های بزرگ.

---

در ادامه پرامپت کامل آماده شده:

---

# 🤖 Professional Telegram Downloader Bot — Full Implementation Prompt

## Project Overview
Build a professional, production-grade, modular Telegram downloader bot
named "DLBot" with the following characteristics:
- Phase 1: YouTube downloader
- Future phases: Instagram, Twitter/X, TikTok, Spotify, direct link downloader
- Scalable from 10 to 100,000 concurrent users
- Fully async architecture
- Multi-language support (FA, EN, AR, RU, ZH)
- Monetization via subscription plans + referral/coin system
- Web + Telegram admin panel

---

## 🛠️ Tech Stack (Exact Versions)

### Core
- Python 3.11+
- aiogram==3.4.1 (Telegram bot interactions)
- pyrogram==2.0.106 + TgCrypto (large file uploads up to 4GB via MTProto)
- yt-dlp (latest) — YouTube downloading

### Database
- PostgreSQL 15 (primary database)
- Redis 7 (caching, rate limiting, task queue, sessions)
- SQLAlchemy 2.0 async (ORM)
- Alembic (migrations)
- asyncpg (async PostgreSQL driver)
- aioredis (async Redis driver)

### Task Queue
- Celery 5.x + Redis broker (download queue)
- flower (Celery monitoring, optional)

### Web Admin Panel
- FastAPI 0.110+
- Jinja2 (admin templates)
- Chart.js (dashboard charts, served via templates)
- python-jose (JWT auth)
- Uvicorn (ASGI server)

### Payments
- aiocryptopay (CryptoBot — Telegram native crypto payment)
- nowpayments-api (NOWPayments — crypto gateway)
- zarinpal-py (ZarinPal — Iranian Rial payment)
- aiohttp (async HTTP client)

### Utilities
- pydantic v2 (settings, validation)
- loguru (logging)
- python-dotenv (env management)
- humanize (human-readable sizes/times)
- Pillow (thumbnail processing)
- ffmpeg-python (media processing wrapper)
- aiofiles (async file I/O)
- APScheduler (scheduled tasks — subscription reminders, cleanup)

---

## 📁 Project Structure

dlbot/
├── .env
├── .env.example
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── README.md
│
├── main.py                          # Entry point
├── config.py                        # Pydantic settings
│
├── bot/
│   ├── __init__.py
│   ├── loader.py                    # Bot + Dispatcher initialization
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── auth.py                  # User registration middleware
│   │   ├── i18n.py                  # Language middleware
│   │   ├── rate_limit.py            # Rate limiting middleware
│   │   ├── subscription.py          # Force-join channel check
│   │   └── throttle.py              # Anti-spam throttle
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py                 # /start, language selection
│   │   ├── download.py              # Main download flow handler
│   │   ├── history.py               # User download history
│   │   ├── referral.py              # Referral & coins system
│   │   ├── plans.py                 # Subscription plans & payment
│   │   ├── profile.py               # User profile & stats
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py         # Admin stats
│   │   │   ├── users.py             # User management
│   │   │   ├── broadcast.py         # Mass messaging
│   │   │   ├── plans.py             # Plan management
│   │   │   └── channels.py          # Force-join management
│   │   └── errors.py                # Global error handler
│   │
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline/
│   │   │   ├── language.py          # Language selection keyboard
│   │   │   ├── download.py          # Quality, format, subtitle keyboards
│   │   │   ├── plans.py             # Plans & payment keyboards
│   │   │   ├── referral.py          # Referral keyboards
│   │   │   └── admin.py             # Admin keyboards
│   │   └── reply/
│   │       ├── main_menu.py         # Main menu keyboard
│   │       └── admin_menu.py        # Admin menu keyboard
│   │
│   ├── states/
│   │   ├── __init__.py
│   │   ├── download.py              # Download flow FSM states
│   │   ├── admin.py                 # Admin FSM states
│   │   └── payment.py               # Payment FSM states
│   │
│   └── filters/
│       ├── __init__.py
│       ├── admin.py                 # IsAdmin filter
│       └── url.py                   # URL detection filter
│
├── modules/                         # 🔌 PLUGGABLE DOWNLOAD MODULES
│   ├── __init__.py                  # Module auto-discovery & registry
│   ├── base.py                      # BaseDownloader abstract class
│   ├── youtube/
│   │   ├── __init__.py
│   │   ├── downloader.py            # YouTube download logic
│   │   ├── parser.py                # Quality/format parser
│   │   └── config.py                # YouTube-specific config
│   ├── instagram/                   # Phase 2 (placeholder)
│   │   ├── __init__.py
│   │   └── downloader.py
│   ├── twitter/                     # Phase 2 (placeholder)
│   │   ├── __init__.py
│   │   └── downloader.py
│   └── direct_link/                 # Phase 3 (placeholder)
│       ├── __init__.py
│       └── downloader.py
│
├── services/
│   ├── __init__.py
│   ├── download_service.py          # Orchestrates download flow
│   ├── cache_service.py             # Redis caching logic
│   ├── file_service.py              # File management & Pyrogram uploader
│   ├── user_service.py              # User CRUD & plan management
│   ├── referral_service.py          # Referral & coin system
│   ├── payment_service.py           # Payment gateway integration
│   ├── notification_service.py      # Scheduled notifications
│   ├── stats_service.py             # Statistics & analytics
│   └── channel_service.py           # Force-join channel checks
│
├── tasks/
│   ├── __init__.py
│   ├── celery_app.py                # Celery app configuration
│   ├── download_tasks.py            # Async download tasks
│   └── cleanup_tasks.py             # File cleanup tasks
│
├── database/
│   ├── __init__.py
│   ├── connection.py                # DB engine & session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   ├── download.py              # Download history model
│   │   ├── cached_file.py           # Cached Telegram file_id model
│   │   ├── plan.py                  # Subscription plan model
│   │   ├── subscription.py          # User subscription model
│   │   ├── referral.py              # Referral model
│   │   ├── coin_transaction.py      # Coin transactions model
│   │   ├── payment.py               # Payment transactions model
│   │   └── channel.py               # Force-join channels model
│   └── repositories/
│       ├── __init__.py
│       ├── user_repo.py
│       ├── download_repo.py
│       ├── cached_file_repo.py
│       ├── subscription_repo.py
│       ├── referral_repo.py
│       └── payment_repo.py
│
├── web/                             # FastAPI Admin Panel
│   ├── __init__.py
│   ├── app.py                       # FastAPI app initialization
│   ├── auth.py                      # JWT auth for web panel
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── dashboard.py             # Stats & charts API
│   │   ├── users.py                 # User management API
│   │   ├── broadcast.py             # Broadcast API
│   │   ├── plans.py                 # Plan management API
│   │   ├── payments.py              # Payment history API
│   │   └── settings.py              # Bot settings API
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── broadcast.html
│   │   └── settings.html
│   └── static/
│       ├── css/
│       └── js/
│
├── locales/                         # i18n translations
│   ├── fa/messages.json             # Persian (default)
│   ├── en/messages.json             # English
│   ├── ar/messages.json             # Arabic
│   ├── ru/messages.json             # Russian
│   └── zh/messages.json             # Chinese
│
├── utils/
│   ├── __init__.py
│   ├── progress.py                  # Beautiful progress bar generator
│   ├── formatters.py                # Size, time, number formatters
│   ├── validators.py                # URL validators
│   └── helpers.py                   # Misc utilities
│
└── migrations/
    ├── env.py
    └── versions/

---

## 🔌 Module System (CRITICAL — Read Carefully)

### Base Module Class (modules/base.py)
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class MediaInfo:
    url: str
    title: str
    thumbnail_url: Optional[str]
    duration: int  # seconds
    view_count: Optional[int]
    uploader: Optional[str]
    formats: list["FormatInfo"]

@dataclass
class FormatInfo:
    format_id: str
    quality_label: str     # "1080p", "720p", "MP3 320kbps"
    ext: str               # mp4, webm, mp3, m4a
    codec: str             # h264, av1, vp9, aac, opus
    filesize_approx: int   # bytes
    is_audio_only: bool
    has_video: bool
    fps: Optional[int]

@dataclass
class DownloadResult:
    file_path: str
    filename: str
    filesize: int
    format_info: FormatInfo
    thumbnail_path: Optional[str]

class BaseDownloader(ABC):
    """
    All downloader modules MUST inherit from this class.
    The module auto-discovery system finds classes that inherit BaseDownloader.
    """
    
    # Module metadata
    NAME: str = ""           # e.g., "YouTube"
    ICON: str = ""           # e.g., "▶️"
    SUPPORTED_DOMAINS: list[str] = []  # e.g., ["youtube.com", "youtu.be"]
    VERSION: str = "1.0.0"
    ENABLED: bool = True
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Check if this module can handle the given URL"""
        for domain in cls.SUPPORTED_DOMAINS:
            if domain in url:
                return True
        return False
    
    @abstractmethod
    async def get_media_info(self, url: str) -> MediaInfo:
        """Fetch media info without downloading"""
        pass
    
    @abstractmethod
    async def download(
        self,
        url: str,
        format_id: str,
        output_dir: str,
        progress_callback: callable
    ) -> DownloadResult:
        """Download the media and return result"""
        pass
    
    @abstractmethod
    async def get_subtitles(self, url: str) -> dict[str, str]:
        """Return available subtitles: {'en': 'English', 'fa': 'Persian'}"""
        pass
    
    async def cleanup(self, file_path: str) -> None:
        """Delete downloaded file from server"""
        import aiofiles.os
        try:
            await aiofiles.os.remove(file_path)
        except FileNotFoundError:
            pass

### Module Auto-Discovery (modules/__init__.py)
```python
import importlib
import pkgutil
import os
from pathlib import Path
from .base import BaseDownloader
from loguru import logger

class ModuleRegistry:
    """
    Automatically discovers and registers all downloader modules.
    When a new module folder is added, it's automatically detected.
    No manual registration needed.
    """
    
    def __init__(self):
        self._modules: list[type[BaseDownloader]] = []
        self._discover_modules()
    
    def _discover_modules(self):
        modules_path = Path(__file__).parent
for finder, name, ispkg in pkgutil.iter_modules([str(modules_path)]):
            if ispkg and name not in ('pycache',):
                try:
                    module = importlib.import_module(f"modules.{name}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseDownloader) and 
                            attr is not BaseDownloader and
                            attr.ENABLED):
                            self._modules.append(attr)
                            logger.info(f"✅ Module loaded: {attr.NAME} v{attr.VERSION}")
                except Exception as e:
                    logger.error(f"❌ Failed to load module {name}: {e}")
    
    def get_handler(self, url: str) -> type[BaseDownloader] | None:
        for module in self._modules:
            if module.can_handle(url):
                return module
        return None
    
    def get_all_modules(self) -> list[type[BaseDownloader]]:
        return self._modules

# Global registry instance
registry = ModuleRegistry()

```

---

## 🗄️ Database Models (Complete)

### User Model
```python
# database/models/user.py
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, Enum
from sqlalchemy.sql import func
import enum

class UserLanguage(str, enum.Enum):
    FA = "fa"
    EN = "en"
    AR = "ar"
    RU = "ru"
    ZH = "zh"

class UserPlanType(str, enum.Enum):
    FREE = "free"
    SILVER = "silver"
    GOLD = "gold"

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)  # Telegram user_id
    username = Column(String(64), nullable=True)
    full_name = Column(String(256))
    language = Column(Enum(UserLanguage), default=UserLanguage.FA)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(String(512), nullable=True)
    
    # Plan
    current_plan = Column(Enum(UserPlanType), default=UserPlanType.FREE)
    plan_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Coins (referral reward)
    coins = Column(Integer, default=0)
    
    # Daily usage tracking
    daily_downloads = Column(Integer, default=0)
    daily_reset_at = Column(DateTime(timezone=True), nullable=True)
    
    # Referral
    referred_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    referral_code = Column(String(16), unique=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))
    
    # Relations
    subscriptions = relationship("Subscription", back_populates="user")
    downloads = relationship("Download", back_populates="user")
    referrals = relationship("Referral", foreign_keys="Referral.referrer_id")

### CachedFile Model
```python
# database/models/cached_file.py
# This is the CORE of smart caching system
class CachedFile(Base):
    __tablename__ = "cached_files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Source identification
    source_url = Column(String(2048))       # Original URL
    url_hash = Column(String(64), index=True, unique=False)  # SHA256 of normalized URL
    platform = Column(String(32))           # "youtube", "instagram", etc.
    video_id = Column(String(128))          # Platform-specific video ID
    
    # Format info
    format_id = Column(String(64))          # yt-dlp format_id
    quality_label = Column(String(32))      # "1080p", "720p", "MP3 320kbps"
    ext = Column(String(16))                # "mp4", "mp3"
    codec = Column(String(32))              # "h264", "av1", "vp9"
    is_audio_only = Column(Boolean, default=False)
    filesize = Column(BigInteger)           # actual file size in bytes
    
    # Telegram file reference
    telegram_file_id = Column(String(256))  # Telegram file_id for re-sending
    telegram_file_unique_id = Column(String(128))  # Unique ID
    sent_as_document = Column(Boolean, default=False)  # document vs video
    
    # Cache validity
    is_valid = Column(Boolean, default=True)  # Set False when expired
    last_verified_at = Column(DateTime(timezone=True))
    
    # Subtitle info (if embedded)
    subtitle_lang = Column(String(8), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    table_args = (
        Index('ix_cached_files_lookup', 'url_hash', 'format_id', 'codec'),
    )

### Plan Model
```python
class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64))               # "Free", "Silver", "Gold"
    plan_type = Column(Enum(UserPlanType), unique=True)
    
    # Limits
    daily_download_limit = Column(Integer, default=5)     # -1 = unlimited
    max_file_size_mb = Column(Integer, default=500)       # -1 = unlimited
    max_resolution = Column(Integer, default=720)         # pixels height
    
    # Pricing (USD)
    price_usd_monthly = Column(Float, default=0.0)
    
    # Referral unlock thresholds
    referral_unlock_count = Column(Integer, nullable=True)  # 20 refs = silver
    
    # Coin cost (alternative to payment)
    coin_cost = Column(Integer, nullable=True)  # coins needed to activate
    
    # Display
    description_key = Column(String(128))   # i18n key
    icon = Column(String(8))                # "🆓", "🥈", "🥇"
    features = Column(JSON)                  # list of feature strings (i18n keys)
    
    is_active = Column(Boolean, default=True)

### Referral & Coin Models
```python
class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger, ForeignKey("users.id"))
    referred_id = Column(BigInteger, ForeignKey("users.id"), unique=True)
    coins_awarded = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)  # False if referred user banned
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    amount = Column(Integer)                # positive = earn, negative = spend
    transaction_type = Column(String(32))   # "referral", "plan_upgrade", "admin_gift"
    description = Column(String(256))
    reference_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

---

## 🎬 Download Flow (Step-by-Step FSM)

### States (bot/states/download.py)
```python
from aiogram.fsm.state import State, StatesGroup

class DownloadStates(StatesGroup):
    WAITING_URL = State()
    SELECTING_FORMAT_TYPE = State()   # Video or Audio?
    SELECTING_QUALITY = State()        # Quality selection
    SELECTING_CODEC = State()          # h264 / av1 / vp9
    SELECTING_SUBTITLE = State()       # Subtitle language or skip
    SELECTING_SEND_AS = State()        # As Video (streamable) or File
    DOWNLOADING = State()              # In progress
    COMPLETED = State()
```

### Complete Download Flow Handler (bot/handlers/download.py)
Implement the following complete flow:

STEP 1 — URL Received:
- Validate URL via `registry.get_handler(url)`
- If no handler found: send error with list of supported platforms
- Check user rate limits & plan restrictions
- Check cached files for this URL:
  - If cached files exist with VALID telegram_file_id: 
    Show beautiful message with video thumbnail, title, duration
    Show list of previously downloaded qualities as inline buttons
    Add "🔄 Fresh Search" button to re-fetch from source
  - If no cache or all expired: proceed to fresh fetch

STEP 2 — Fetch Media Info:
Send animated progress message:
⏳ در حال دریافت اطلاعات...
━━━━━━━━━━━━━━━━━━━━
🎬 لطفاً صبر کنید
Call downloader.get_media_info(url) and show:
- Video thumbnail (as photo)
- Title (truncated to 60 chars)
- Duration (formatted as HH:MM:SS)
- Views count (humanized)
- Uploader name

STEP 3 — Select Format Type:
🎯 نوع فایل دریافتی را انتخاب کنید:

[🎬 ویدیو]  [🎵 صدا (Audio)]
[❌ انصراف]
STEP 4A — If Video Selected (Quality Selection):
Show ALL available video qualities grouped:
📺 کیفیت ویدیو را انتخاب کنید:

━━━━ کیفیت بالا ━━━━
[🔵 4K (2160p) • ~2.1GB]
[🟢 1080p • ~850MB]

━━━━ کیفیت متوسط ━━━━  
[🟡 720p • ~420MB] ✅ پیشنهاد
[🟠 480p • ~200MB]

━━━━ کیفیت پایین ━━━━
[🔴 360p • ~95MB]
[⚫ 240p • ~45MB]

[◀️ برگشت]
Note: Show lock icon 🔒 on qualities restricted by user's plan

STEP 4B — If Audio Selected:
Show audio formats:
🎵 فرمت صوتی را انتخاب کنید:

[🎼 MP3 320kbps • ~8MB/min]
[🎼 MP3 128kbps • ~4MB/min]
[🎧 AAC 256kbps • ~7MB/min]
[🎧 M4A 128kbps • ~3.5MB/min]
[🔊 OPUS (بهترین کیفیت/حجم) • ~3MB/min]

[◀️ برگشت]
STEP 5 — Codec Selection (only for Video):
🎞️ کدک ویدیو را انتخاب کنید:

[H.264 | MP4 ✅ سازگار با همه دستگاه‌ها]
[AV1 | WebM 🏆 بهترین کیفیت/حجم]
[VP9 | WebM ⚡ سبک و کارآمد]

ℹ️ اگر مطمئن نیستید H.264 را انتخاب کنید

[◀️ برگشت]
STEP 6 — Subtitle Selection:
📝 زیرنویس می‌خواهید؟

زیرنویس‌های موجود:
[🇮🇷 فارسی]  [🇺🇸 English]
[🇸🇦 عربی]   [🇷🇺 Russian]

[✅ بدون زیرنویس]  [◀️ برگشت]
STEP 7 — Send As:
📤 نحوه دریافت فایل:

[📹 ویدیو (قابل پخش در تلگرام)]
[📁 فایل (دانلود کامل)]

[◀️ برگشت]
STEP 8 — Download & Progress:
Show REAL-TIME updating progress message:

# utils/progress.py
def generate_progress_message(
    title: str,
    progress_percent: float,
    downloaded_mb: float,
    total_mb: float,
    speed_mbps: float,
    eta_seconds: int,
    queue_position: int = 0,
    phase: str = "download"  # "download", "upload", "processing"
) -> str:
    
    bar_length = 20
    filled = int(bar_length * progress_percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    phase_icons = {
        "download": "⬇️",
        "upload": "⬆️", 
        "processing": "⚙️"
    }
    
    phase_labels = {
        "download": "در حال دانلود",
        "upload": "در حال ارسال به تلگرام",
        "processing": "در حال پردازش"
    }
    
    eta_str = format_eta(eta_seconds)
    
    message = f"""
{phase_icons[phase]} <b>{phase_labels[phase]}</b>

🎬 <code>{title[:45]}...</code>

[{bar}] {progress_percent:.1f}%

📦 حجم: {downloaded_mb:.1f} / {total_mb:.1f} MB
⚡ سرعت: {speed_mbps:.2f} MB/s
⏱ زمان باقی‌مانده: {eta_str}
"""
    if queue_position > 0:
        message += f"\n📋 موقعیت در صف: {queue_position}"
    
    message += "\n\n<i>⚠️ لطفاً صبر کنید، ربات در حال کار است...</i>"
    return message
Update progress message every 3 seconds (not on every chunk to avoid flood).

---

## 💰 Plans & Limits System

### Plan Definitions (seed data)
FREE Plan:
- daily_download_limit: 5
- max_file_size_mb: 500
- max_resolution: 720
- price: FREE
- referral_unlock: N/A

SILVER Plan (🥈):  
- daily_download_limit: 20
- max_file_size_mb: 2048 (2GB)
- max_resolution: 1080
- price: $5.99/month
- referral_unlock: 20 referrals OR 500 coins
- coin_cost: 500

GOLD Plan (🥇):
- daily_download_limit: -1 (unlimited)
- max_file_size_mb: -1 (Telegram limit only)
- max_resolution: -1 (unlimited)
- price: $9.99/month
- referral_unlock: 50 referrals (→ 1 month free)
- coin_cost: 1000

### Referral Milestones & Coins
1 referral = 10 coins
5 referrals = 50 coins + "دوستیابی 🌟" badge in profile
10 referrals = 100 coins
20 referrals = Silver plan activated automatically
50 referrals = 1-month Gold plan offered (notification sent)

Coin redemption:
- 500 coins → Silver plan (1 month)
- 1000 coins → Gold plan (1 month)
- 100 coins → 50 extra MB file size limit for 24h
- 50 coins → 5 extra downloads today
---

## 🌍 i18n System

### Implementation
Use fluent.runtime or simple JSON-based translation.
Language selection happens on FIRST /start:

👋 Welcome / خوش آمدید

Please select your language:

[🇮🇷 فارسی]  [🇺🇸 English]
[🇸🇦 العربية] [🇷🇺 Русский]
[🇨🇳 中文]
Store selected language in:
1. Database (User.language field)
2. Redis cache (user_lang:{user_id}) for fast access

Language middleware (bot/middlewares/i18n.py):
- Intercepts every update
- Reads language from Redis (fallback to DB)
- Injects _() translation function into handler data
- Supports RTL detection for FA and AR (add \u200f direction marks)

---

## 👑 Referral System (Beautiful & Professional)

### User Profile / Referral Panel
👤 پروفایل من

━━━━━━━━━━━━━━━━━━━━━━━━
🆔 شناسه: @username
📊 پلن فعلی: 🥈 نقره‌ای
📅 انقضای پلن: ۱۴ روز دیگر
🪙 سکه‌های من: 350 سکه
━━━━━━━━━━━━━━━━━━━━━━━━

📥 دانلودهای امروز: 7 / 20
📦 آمار کلی: 143 دانلود

━━━━━━━━━━━━━━━━━━━━━━━━
👥 سیستم دعوت

🔗 لینک اختصاصی شما:
t.me/dlbot?start=ref_ABC123XY

📊 تعداد دعوت‌شدگان: 12 نفر
🪙 سکه کسب‌شده: 120 سکه

پیشرفت تا پلن طلایی:
[████████░░░░░░░░░░░░] 12/50

━━━━━━━━━━━━━━━━━━━━━━━━

[🪙 کیف سکه‌ام]  [🎁 ارتقای پلن]
[📜 تاریخچه دانلود]  [💳 خرید پلن]
[👥 لیست دعوت‌شدگان]
### Coin Wallet
🪙 کیف سکه من

موجودی فعلی: 350 سکه

━━━━ تاریخچه تراکنش ━━━━
✅ +10 | دعوت ali_user   | دیروز
✅ +10 | دعوت reza_1234  | ۳ روز پیش
✅ +100| جایزه ۱۰ دعوت  | ۵ روز پیش
❌ -50 | خرید دانلود اضافه| ۱ هفته پیش

━━━━ خرید با سکه ━━━━
[🥈 پلن نقره‌ای — 500 سکه]
[🥇 پلن طلایی — 1000 سکه]
[⬇️ 5 دانلود اضافه — 50 سکه]
[📦 +50MB حجم (24h) — 100 سکه]
---

## 🔔 Notification System

### Scheduled Notifications (APScheduler jobs)

# services/notification_service.py

# Job 1: Subscription expiry warning
# Run: every day at 10:00 UTC
# Logic: Find users where plan_expires_at is between now+7days and now+8days
# Send: "⚠️ اشتراک شما 7 روز دیگر منقضی می‌شود..."

# Job 2: Subscription expiry warning (1 day)
# Run: every day at 10:00 UTC
# Logic: Find users where plan_expires_at is between now+1day and now+2days
# Send: "🚨 اشتراک شما فردا منقضی می‌شود! همین الان تمدید کنید."

# Job 3: Daily stats to admin
# Run: every day at 00:00 UTC
# Send to admin: daily downloads count, new users, revenue

# Job 4: File cleanup
# Run: every 30 minutes
# Logic: Delete files in /tmp/downloads/ older than 2 hours
---

## 💳 Payment System

### Supported Gateways

# services/payment_service.py

class PaymentGateway(str, enum.Enum):
    CRYPTO_BOT = "cryptobot"      # Telegram native, easiest
    NOW_PAYMENTS = "nowpayments"  # Wide crypto support
    ZARINPAL = "zarinpal"         # Iranian Rial (IRR)

class PaymentService:
    async def create_invoice(
        self,
        user_id: int,
        plan_type: UserPlanType,
        gateway: PaymentGateway,
        currency: str = "USDT"
    ) -> str:
        """Returns payment URL"""
    
    async def verify_payment(
        self,
        payment_id: str,
        gateway: PaymentGateway
    ) -> bool:
        """Verify payment and activate plan"""
    
    async def handle_webhook(self, data: dict, gateway: PaymentGateway):
        """Handle payment gateway webhooks"""
### Payment Selection UI
💳 خرید پلن 🥈 نقره‌ای

قیمت: $5.99 / ماه

درگاه پرداخت را انتخاب کنید:

[₿ CryptoBot (تلگرام)]
[💰 NOWPayments (ارز دیجیتال)]
[🇮🇷 زرین‌پال (ریال ایران)]

[◀️ برگشت]
---

## 🔐 Force-Join System

### Implementation
```python
# bot/middlewares/subscription.py
class ForceJoinMiddleware(BaseMiddleware):
    """
    If force-join is enabled for any channel,
    check user membership before processing any message.
    If not member: show join prompt with verify button.
    Skip check for /start command.
    """
    
    async def call(self, handler, event, data):
        # 1. Get active force-join channels from Redis cache
        # 2. For each channel, check user membership via bot.get_chat_member()
        # 3. If not member in any: send join prompt
        # 4. If member in all: proceed
        
        # Join prompt example:
        """
        🔒 برای استفاده از ربات باید عضو کانال‌های زیر باشید:
        
        1. کانال اصلی → [عضو شو]
        2. کانال اخبار → [عضو شو]
        
        بعد از عضویت:
        [✅ عضو شدم، ادامه بده]
        """

---

## 🛡️ Admin System (Telegram)

### Admin Handlers (bot/handlers/admin/)

**Dashboard:**
📊 پنل مدیریت

━━━━ آمار امروز ━━━━
👥 کاربران جدید: 47
⬇️ دانلودها: 1,284
💰 درآمد: $23.50

━━━━ کل ━━━━
👥 کل کاربران: 15,432
🥈 پلن نقره: 234
🥇 پلن طلایی: 89

━━━━ سرور ━━━━
💾 فضای آزاد: 18.4 GB
🖥️ CPU: 23%
📡 Uptime: 12d 4h

[📢 ارسال پیام همگانی]
[👤 مدیریت کاربران]
[🔧 تنظیمات ربات]
[📋 گزارش‌ها]

**Broadcast System:**
📢 ارسال پیام

هدف ارسال را انتخاب کنید:

[👥 همه کاربران (15,432)]
[🥈 پلن نقره (234)]
[🥇 پلن طلایی (89)]
[🆓 پلن رایگان (15,109)]
[🔍 کاربر خاص (وارد کردن آیدی)]

Broadcast implementation:
- Use asyncio.gather with semaphore (max 25 concurrent sends)
- Rate: 30 messages/second to avoid Telegram limits
- Show real-time progress: "ارسال شد: 1,234 / 15,432"
- Failed sends logged and retried

---

## 🌐 Web Admin Panel (FastAPI)

### Dashboard Features:
- Real-time stats (users, downloads, revenue) — refresh every 30s
- Chart.js graphs: 
  - Daily downloads (last 30 days)
  - New users (last 30 days)
  - Revenue by gateway (last 30 days)
  - Top downloaded videos
- User table with pagination, search, filter by plan
- Quick actions: ban/unban, upgrade/downgrade plan, gift coins
- Broadcast form with HTML message editor
- Force-join channel management
- System health: CPU/RAM/disk from psutil

### Authentication:
- JWT-based auth
- Single admin user (configured via .env ADMIN_WEB_PASSWORD)
- 24h token expiry

---

## 📁 File Management & Pyrogram Large File Upload

### Strategy for Files > 2GB

```python
# services/file_service.py
from pyrogram import Client
from pyrogram.types import Message

class FileService:
    def init(self):
        # Pyrogram client for large file uploads
        # Uses MTProto directly — supports up to 4GB
        self.pyro_client = Client(
            "dlbot_uploader",
            bot_token=settings.BOT_TOKEN,
            api_id=settings.TELEGRAM_API_ID,      # Get from my.telegram.org
            api_hash=settings.TELEGRAM_API_HASH,   # Get from my.telegram.org
        )
    
    async def send_file(
        self,
        chat_id: int,
        file_path: str,
        caption: str,
        as_document: bool = False,
        thumbnail: str = None,
        progress_callback: callable = None
    ) -> tuple[str, str]:
        """
        Send file using Pyrogram (MTProto).
        Returns (file_id, file_unique_id) for caching.
        Files up to 4GB supported.
        """
        if as_document:
            msg = await self.pyro_client.send_document(
                chat_id=chat_id,
                document=file_path,
                caption=caption,
                progress=progress_callback,
                thumb=thumbnail
            )
        else:
            msg = await self.pyro_client.send_video(
                chat_id=chat_id,
                video=file_path,
                caption=caption,
                progress=progress_callback,
                thumb=thumbnail,
                supports_streaming=True
            )
        
        media = msg.video or msg.document
        return media.file_id, media.file_unique_id
```

**Important**: Requires `api_id` and `api_hash` from https://my.telegram.org

---

## ⚙️ Configuration (config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    ADMIN_IDS: list[int] = []
    
    # Database
    DATABASE_URL: str  # postgresql+asyncpg://...
    REDIS_URL: str = "redis://localhost:6379"
    
    # Payments
    CRYPTOBOT_TOKEN: str = ""
    NOWPAYMENTS_API_KEY: str = ""
    ZARINPAL_MERCHANT_ID: str = ""
    
    # Storage
    DOWNLOAD_DIR: str = "/tmp/downloads"
    MAX_CONCURRENT_DOWNLOADS: int = 3
    FILE_CLEANUP_AFTER_HOURS: int = 2
    
    # Feature flags
    FORCE_JOIN_ENABLED: bool = False
    MAINTENANCE_MODE: bool = False
    REFERRAL_COINS_PER_INVITE: int = 10
    
    # Web panel
    ADMIN_WEB_PASSWORD: str
    WEB_SECRET_KEY: str
    WEB_PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🚀 Deployment (Ubuntu 22.04)

### Docker Compose
version: '3.8'
services:
  bot:
    build: .
    restart: always
    depends_on: [postgres, redis]
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./downloads:/tmp/downloads
      - ./.env:/app/.env
    
  worker:
    build: .
    command: celery -A tasks.celery_app worker --loglevel=info --concurrency=3
    restart: always
    depends_on: [postgres, redis]
  
  web:
    build: .
    command: uvicorn web.app:app --host 0.0.0.0 --port 8000
    restart: always
    ports:
      - "8000:8000"
  
  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: dlbot
      POSTGRES_USER: dlbot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
---

## 🎯 Implementation Priorities

### Phase 1 (MVP — Build First):
1. Database models + migrations
2. Module system (auto-discovery)
3. YouTube module (yt-dlp)
4. Basic download flow (URL → quality → download → send)
5. File caching system (file_id storage/lookup)
6. Multi-language support (FA + EN)
7. Basic plans (Free/Silver/Gold) with limits
8. Admin basic commands

### Phase 2:
1. Referral system + coins
2. Beautiful progress messages
3. Subtitle support
4. Payment integration (CryptoBot first)
5. Web admin panel
6. Force-join system
7. Broadcast system
8. Subscription reminders

### Phase 3:
1. Instagram module
2. Twitter/X module
3. TikTok module
4. ZarinPal integration
5. Direct link downloader
6. Advanced admin analytics

---

## 📝 Critical Implementation Notes

1. File cleanup: ALWAYS delete local file AFTER successfully getting
   file_id from Telegram. Use try/finally to guarantee cleanup.

2. Progress updates: Throttle to max 1 update per 3 seconds.
   Use asyncio.Lock to prevent concurrent progress message edits.

3. Queue system: Use Redis-backed queue. Max 3 concurrent downloads.
   Show queue position to user ("شما نفر 4 در صف هستید، ~8 دقیقه").

4. file_id expiry: When sending cached file_id fails with BadRequest,
   set is_valid=False in DB, re-download, update with new file_id.

5. Rate limiting: Per user: max 1 download request per 30 seconds.
   Use Redis with sliding window algorithm.

6. Error messages: ALL errors must be user-friendly and translated.
   Never show raw Python exceptions to users.

7. Pyrogram session: Initialize Pyrogram client on startup and keep
   alive. Handle reconnection gracefully.

8. Scalability: All state in Redis/PostgreSQL (stateless bot process).
   Can run multiple bot instances behind a load balancer when needed.

9. Logging: Use loguru with rotation. Log all downloads with user_id,
   url, quality, filesize for analytics. Never log sensitive data.

10. yt-dlp cookies: Support optional cookies.txt for age-restricted
    or members-only videos. Configure via .env YTDLP_COOKIES_PATH.
`

---

## ✅ جمع‌بندی نهایی

این پرامپت رو کامل داری. برای استفاده در Cursor: