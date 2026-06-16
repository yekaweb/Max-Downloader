"""
Max Youtube Downloader Main Entry Point
Professional Telegram Downloader Bot
"""

import asyncio
import logging
import sys
from pathlib import Path
from loguru import logger
from config import settings

# ── Create logs directory ────────────────────────────────────────────────────
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

# ── Bridge standard logging → loguru ────────────────────────────────────────
class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
for _log in ("uvicorn", "uvicorn.error", "uvicorn.access", "aiogram", "sqlalchemy.engine"):
    logging.getLogger(_log).handlers = [_InterceptHandler()]

# ── Remove default loguru sink ────────────────────────────────────────────────
logger.remove()

# Sink 1: Console (coloured, human-readable)
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Sink 2: Rotating daily log file (all levels)
logger.add(
    str(log_dir / "dlbot_{time:YYYY-MM-DD}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
    rotation="00:00",      # New file each day
    retention="14 days",   # Keep 2 weeks
    compression="zip",     # Compress old files
    level="DEBUG",
    enqueue=True,          # Thread-safe async writing
)

# Sink 3: Separate ERROR-only file for alerting / monitoring
logger.add(
    str(log_dir / "dlbot_errors.log"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}\n{exception}",
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    level="ERROR",
    enqueue=True,
    backtrace=True,   # Full traceback in errors
    diagnose=False,   # ← Security: disable variable values in tracebacks (production)
)


async def main():
    """Main async entry point"""
    logger.info(f"🤖 Starting Max Youtube Downloader v{settings.APP_VERSION}")
    logger.info(f"📊 Environment: {settings.APP_ENV}")
    logger.info(f"🌐 Default Language: {settings.DEFAULT_LANGUAGE}")
    
    # Validate bot token
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "":
        logger.error("❌ BOT_TOKEN not configured in .env file")
        logger.error("   Please add BOT_TOKEN=your_token_here to .env file")
        return
    
    logger.info(f"✅ Bot token found: {str(settings.BOT_TOKEN)[:15]}...")
    
    # Import bot components (lazy import)
    try:
        logger.info("📦 Loading bot components...")
        from bot.loader import bot, dp

        if not bot:
            raise ImportError("Bot initialization failed - bot is None")
        if not dp:
            raise ImportError("Dispatcher initialization failed - dp is None")

        logger.info("✅ Bot components loaded successfully")
        logger.info(f"📡 Bot username: {settings.BOT_USERNAME}")

    except ImportError as e:
        logger.error(f"❌ Import error - Failed to load bot components: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    except Exception as e:
        logger.error(f"❌ Unexpected error during bot initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # Initialize Pyrogram
    pyrogram_client = None
    if settings.PYROGRAM_APP_ID and settings.PYROGRAM_APP_HASH:
        from pyrogram import Client
        logger.info("🚀 Initializing Pyrogram client for large file uploads...")
        try:
            pyrogram_client = Client(
                name=settings.PYROGRAM_SESSION_NAME,
                api_id=settings.PYROGRAM_APP_ID,
                api_hash=settings.PYROGRAM_APP_HASH,
                bot_token=settings.BOT_TOKEN,
                in_memory=True
            )
            await pyrogram_client.start()
            logger.info("✅ Pyrogram client started successfully")
            
            # Make it globally accessible for handlers if needed
            import bot.loader as bot_loader
            bot_loader.pyrogram_client = pyrogram_client
        except Exception as e:
            logger.error(f"❌ Failed to start Pyrogram client: {e}")

    # Initialize Database Tables
    logger.info("🛠️ Initializing database tables...")
    try:
        from database.connection import engine
        from database.models.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables verified/created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")

    # Start polling once (no retry loop) so handlers respond promptly.
    try:
        logger.info("🚀 Starting bot polling...")
        logger.info("📡 Bot is listening for updates...")
        logger.info("💡 Send /start command to the bot to test")
        resolved_updates = dp.resolve_used_update_types()
        logger.info(f"📨 Allowed updates for polling: {resolved_updates}")

        await dp.start_polling(bot, skip_updates=True)

        logger.info("⏹️  Bot polling stopped normally")

    except KeyboardInterrupt:
        logger.info("⏹️  Bot stopped by user")
    except Exception as e:
        logger.critical(f"💥 Critical error during polling: {e}", exc_info=True)
    finally:
        try:
            sess = getattr(bot, "session", None)
            if sess and not callable(sess):
                try:
                    await sess.close()
                except Exception:
                    pass

            logger.info("✅ Bot session closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing bot session: {e}")
            
        try:
            if pyrogram_client and pyrogram_client.is_initialized:
                logger.info("⏹️ Stopping Pyrogram client...")
                await pyrogram_client.stop()
        except Exception as e:
            logger.warning(f"⚠️ Error stopping Pyrogram client: {e}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Max Youtube Downloader - Professional Telegram Downloader")
    logger.info("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✅ Max Youtube Downloader shutdown complete")
    except Exception as e:
        logger.critical(f"💥 Critical error: {e}", exc_info=True)
