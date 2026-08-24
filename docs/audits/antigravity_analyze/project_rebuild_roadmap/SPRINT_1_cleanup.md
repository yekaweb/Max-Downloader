# 🧹 Sprint 1 — پاکسازی و ساختار تمیز
**مدت:** ۳ روز | **اولویت:** 🔴 بحرانی | **پیش‌نیاز:** هیچ

> این Sprint پایه همه چیز است. بدون اینجا، هیچ Sprint دیگری معنا ندارد.

---

## 🎯 اهداف این Sprint

1. حذف تمام کد مرده (~200KB)
2. تبدیل God File (1763 خط) به فایل‌های کوچک
3. بازنویسی `config.py` با Pydantic v2
4. راه‌اندازی `alembic.ini` و migration اول
5. تبدیل `MemoryStorage` به `RedisStorage`
6. تعیین یک `loader.py` تمیز

---

## 📋 Task List

### ✅ Task 1.1 — حذف فایل‌های loader اضافه
**زمان:** 30 دقیقه

فایل‌های زیر باید **حذف** شوند (هیچ جا استفاده نمی‌شوند):
```
bot/loader.py                      ← خالی است، حذف + بازنویسی
bot/loader_simple.py               ← حذف
bot/loader_complete.py             ← حذف
bot/loader_final_fixed.py          ← حذف
bot/loader_fsm.py                  ← حذف
bot/loader_fsm_complete_fixed.py   ← حذف
bot/loader_fsm_exact.py            ← حذف
bot/loader_professional.py         ← حذف
```

> `loader_professional_enhanced.py` فعلاً نگه داشته می‌شود تا کدش استخراج شود

**دستور PowerShell:**
```powershell
cd "D:\Max Downloader\Max-Downloader\bot"
Remove-Item loader_simple.py, loader_complete.py, loader_final_fixed.py, loader_fsm.py, loader_fsm_complete_fixed.py, loader_fsm_exact.py, loader_professional.py
```

---

### ✅ Task 1.2 — حذف فایل‌های garbage دیگر
**زمان:** 20 دقیقه

```
database/models/cached_download_old_backup.py  ← حذف
debug_dict_issue.ipynb                          ← حذف
debug_imports.ipynb                             ← حذف
_fix_ds.py                                     ← حذف
_fix_tasks.py                                  ← حذف
check.py                                       ← حذف (یا به tests/ منتقل)
test_imports.py                                ← حذف (یا به tests/ منتقل)
COMPLETION_STATUS.txt                          ← حذف
FINAL_SESSION_REPORT.txt                       ← حذف
FINAL_UPDATE_REPORT.txt                        ← حذف
PHASE_2_FINAL_COMPLETION_REPORT.txt           ← حذف
SESSION_FINAL_SUMMARY.txt                      ← حذف
DOCUMENTATION_SYNCHRONIZATION_CERTIFICATE.txt ← حذف
PHASES_INTEGRATION_COMPLETE.md                ← حذف
INTEGRATION_COMPLETION_REPORT.md              ← حذف
```

---

### ✅ Task 1.3 — یکپارچه‌سازی keyboards
**زمان:** 30 دقیقه

**مشکل:** دو نسخه keyboard موجود است:
- `bot/keyboards.py` (فایل مجزا)
- `bot/keyboards/` (پوشه با inline/)

**راه‌حل:**
```python
# bot/keyboards.py را بررسی کن
# محتوای منحصربه‌فردش را به bot/keyboards/inline/ منتقل کن
# سپس bot/keyboards.py را حذف کن
```

---

### ✅ Task 1.4 — بازنویسی config.py با Pydantic v2
**زمان:** 1 ساعت

**فایل هدف:** `config.py` (بازنویسی کامل — `config_simple.py` حذف می‌شود)

```python
# config.py — نسخه نهایی
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from pathlib import Path
from typing import Optional
import os

class Settings(BaseSettings):
    # ─── Telegram ───────────────────────────────────────────
    BOT_TOKEN: str
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    ADMIN_IDS: list[int] = []
    BOT_USERNAME: str = "dlbot"

    # ─── Database ───────────────────────────────────────────
    DB_TYPE: str = "sqlite"           # "sqlite" یا "postgresql"
    DB_PATH: str = "./dlbot.db"       # برای sqlite
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "dlbot_user"
    DB_PASSWORD: str = ""
    DB_NAME: str = "dlbot_db"

    # ─── Redis ──────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # ─── Pyrogram ───────────────────────────────────────────
    PYROGRAM_SESSION_NAME: str = "dlbot_session"

    # ─── Payment Gateways ───────────────────────────────────
    CRYPTOBOT_TOKEN: str = ""
    NOWPAYMENTS_API_KEY: str = ""
    ZARINPAL_MERCHANT_ID: str = ""

    # ─── Storage ────────────────────────────────────────────
    DOWNLOAD_DIR: Path = Path("./temp_downloads")
    CACHE_DIR: Path = Path("./cached_files")
    LOG_DIR: Path = Path("./logs")
    MAX_CONCURRENT_DOWNLOADS: int = 3
    FILE_CLEANUP_AFTER_HOURS: int = 2

    # ─── Feature Flags ──────────────────────────────────────
    FORCE_JOIN_ENABLED: bool = False
    REFERRAL_ENABLED: bool = True
    MAINTENANCE_MODE: bool = False
    REFERRAL_COINS_PER_INVITE: int = 10

    # ─── i18n ───────────────────────────────────────────────
    DEFAULT_LANGUAGE: str = "fa"
    SUPPORTED_LANGUAGES: list[str] = ["fa", "en", "ar", "ru", "zh"]

    # ─── Web Panel ──────────────────────────────────────────
    ADMIN_WEB_PASSWORD: str = "admin123"
    WEB_SECRET_KEY: str = "change-me-in-production"
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000

    # ─── App ────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_VERSION: str = "2.0.0"
    LOG_LEVEL: str = "INFO"

    @field_validator("BOT_TOKEN")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError("BOT_TOKEN is required and must be valid")
        return v

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip().isdigit()]
        return v or []

    @field_validator("SUPPORTED_LANGUAGES", mode="before")
    @classmethod
    def parse_languages(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v or ["fa", "en"]

    @model_validator(mode="after")
    def create_directories(self) -> "Settings":
        for d in [self.DOWNLOAD_DIR, self.CACHE_DIR, self.LOG_DIR]:
            d.mkdir(parents=True, exist_ok=True)
        return self

    @property
    def database_url(self) -> str:
        if self.DB_TYPE == "sqlite":
            path = str(self.DB_PATH).replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            return f"sqlite:///{path}"
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_async_url(self) -> str:
        if self.DB_TYPE == "sqlite":
            path = str(self.DB_PATH).replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            return f"sqlite+aiosqlite:///{path}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

---

### ✅ Task 1.5 — بازنویسی bot/loader.py
**زمان:** 45 دقیقه

```python
# bot/loader.py — تنها loader پروژه (تمیز و کوتاه)
"""
DLBot Loader — Bot and Dispatcher initialization ONLY.
All handlers are registered via include_router() in separate files.
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from config import settings

# ─── Bot Instance ───────────────────────────────────────────
bot = Bot(
    token=settings.BOT_TOKEN,
    session=AiohttpSession(timeout=120),
)

# ─── FSM Storage ────────────────────────────────────────────
# از Redis برای persistence (در صورت restart ربات session ها حفظ می‌شوند)
try:
    from aiogram.fsm.storage.redis import RedisStorage
    storage = RedisStorage.from_url(settings.redis_url)
    logger.info("✅ FSM Storage: Redis")
except Exception as e:
    logger.warning(f"⚠️ Redis unavailable, using MemoryStorage: {e}")
    storage = MemoryStorage()

# ─── Dispatcher ─────────────────────────────────────────────
dp = Dispatcher(storage=storage)

# ─── Pyrogram Client (for large file uploads) ────────────────
pyrogram_client = None

async def init_pyrogram():
    """Initialize Pyrogram client for large file uploads (>50MB)"""
    global pyrogram_client
    try:
        from pyrogram import Client
        if settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH:
            pyrogram_client = Client(
                name=settings.PYROGRAM_SESSION_NAME,
                bot_token=settings.BOT_TOKEN,
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                no_updates=True,
                workdir=".",
            )
            await pyrogram_client.start()
            logger.info("✅ Pyrogram client initialized (large file uploads enabled)")
        else:
            logger.warning("⚠️ TELEGRAM_API_ID/HASH not set — large file uploads disabled")
    except Exception as e:
        logger.warning(f"⚠️ Pyrogram failed to start: {e}")
        pyrogram_client = None
```

---

### ✅ Task 1.6 — بازنویسی main.py
**زمان:** 30 دقیقه

```python
# main.py — entry point تمیز
"""
DLBot v2.0 — Professional Telegram Downloader
Entry point: initializes all components and starts polling.
"""
import asyncio
from pathlib import Path
from loguru import logger
from config import settings

# ─── Logging Setup ──────────────────────────────────────────
logger.remove()
logger.add(
    str(settings.LOG_DIR / "dlbot.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
    rotation="100 MB",
    retention="14 days",
    level=settings.LOG_LEVEL,
    encoding="utf-8",
)
logger.add(
    lambda msg: print(msg.rstrip()),
    format="{time:HH:mm:ss} | {level:<8} | {message}",
    level="INFO",
    colorize=True,
)


async def on_startup():
    """Run on bot startup"""
    from bot.loader import bot, dp, init_pyrogram
    from database.connection import create_tables

    logger.info(f"🚀 DLBot v{settings.APP_VERSION} starting...")
    logger.info(f"📊 Environment: {settings.APP_ENV}")

    # Init database
    await create_tables()
    logger.info("✅ Database ready")

    # Init Pyrogram
    await init_pyrogram()

    # Register all handlers
    await register_routers(dp)
    logger.info("✅ All handlers registered")


async def register_routers(dp):
    """Register all routers — each handler in its own file"""
    from bot.handlers.start import router as start_router
    from bot.handlers.url_handler import router as url_router
    from bot.handlers.format_handler import router as format_router
    from bot.handlers.download_exec import router as download_router
    from bot.handlers.cache_handler import router as cache_router
    from bot.handlers.profile import router as profile_router
    from bot.handlers.referral import router as referral_router
    from bot.handlers.plans import router as plans_router
    from bot.handlers.admin import router as admin_router
    from bot.handlers.errors import router as errors_router

    # Register middlewares
    from bot.middlewares.auth import AuthMiddleware
    from bot.middlewares.i18n import I18nMiddleware
    from bot.middlewares.rate_limit import RateLimitMiddleware

    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Include routers (order matters!)
    dp.include_router(start_router)
    dp.include_router(url_router)
    dp.include_router(format_router)
    dp.include_router(download_router)
    dp.include_router(cache_router)
    dp.include_router(profile_router)
    dp.include_router(referral_router)
    dp.include_router(plans_router)
    dp.include_router(admin_router)
    dp.include_router(errors_router)  # باید آخر باشد (catch-all)


async def on_shutdown():
    """Cleanup on shutdown"""
    from bot.loader import bot, pyrogram_client

    logger.info("🛑 Shutting down DLBot...")

    if pyrogram_client and pyrogram_client.is_connected:
        await pyrogram_client.stop()
        logger.info("✅ Pyrogram disconnected")

    session = getattr(bot, "session", None)
    if session and not callable(session):
        await session.close()

    logger.info("✅ DLBot shutdown complete")


async def main():
    from bot.loader import bot, dp

    await on_startup()

    try:
        logger.info("📡 Starting polling...")
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("⏹️ Stopped by user")
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

---

### ✅ Task 1.7 — راه‌اندازی Alembic واقعی
**زمان:** 45 دقیقه

```bash
# 1. rename alembic.example.ini → alembic.ini
# 2. ویرایش alembic.ini:
#    sqlalchemy.url = sqlite:///./dlbot.db  (یا از .env بخوانید)

# 3. ویرایش migrations/env.py:
from config import settings
from database.models.models import Base

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata

# 4. ایجاد اولین migration:
alembic revision --autogenerate -m "initial_schema"

# 5. اجرا:
alembic upgrade head
```

---

### ✅ Task 1.8 — استخراج handler ها از God File

**فایل‌هایی که باید از `loader_professional_enhanced.py` استخراج شوند:**

| Handler | فایل مقصد | خطوط تقریبی |
|---------|-----------|-------------|
| `cmd_start`, `cmd_download` | `bot/handlers/start.py` | 40 خط |
| `handle_url_input`, `run_fresh_download_flow` | `bot/handlers/url_handler.py` | 150 خط |
| `handle_format_type`, `handle_codec`, `handle_video_quality`, `handle_subtitle`, `handle_send_as`, `handle_audio_format` | `bot/handlers/format_handler.py` | 200 خط |
| `start_download` | `bot/handlers/download_exec.py` | 250 خط |
| `handle_send_cached`, `handle_fresh_download_search`, `handle_cancel_download_cache` | `bot/handlers/cache_handler.py` | 100 خط |
| Keyboard functions | `bot/keyboards/inline/download.py` | 150 خط |
| Utility functions | `utils/progress.py` (موجود، اصلاح) | — |
| Session management | `utils/session_manager.py` | 60 خط |

---

## 📝 Checklist پایان Sprint 1

```
[ ] تمام loader های اضافه حذف شدند
[ ] garbage files حذف شدند
[ ] keyboards دوتایی یکی شد
[ ] config.py با Pydantic v2 بازنویسی شد
[ ] config_simple.py حذف شد
[ ] bot/loader.py تمیز و کوچک است (فقط init)
[ ] main.py بازنویسی شد
[ ] alembic.ini واقعی ایجاد شد
[ ] migration اول generate شد
[ ] ربات با `python main.py` start می‌شود
[ ] /start جواب می‌دهد
```

---

**بعدی:** [`SPRINT_2_core_fix.md`](./SPRINT_2_core_fix.md)
