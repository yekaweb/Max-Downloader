"""
DLBot Main Entry Point
Professional Telegram Downloader Bot
"""

import asyncio
import logging
from pathlib import Path
from loguru import logger
from config_simple import settings

# Create logs directory
Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

# Remove default logger
logging.getLogger().handlers = []

# Configure loguru
logger.remove()
logger.add(
    str(settings.LOG_FILE),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="500 MB",
    retention="7 days",
    level=settings.LOG_LEVEL,
)
logger.add(
    lambda msg: print(msg.rstrip()),  # Enable console output for debugging
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level=settings.LOG_LEVEL,
)


async def main():
    """Main async entry point"""
    logger.info(f"🤖 Starting DLBot v{settings.APP_VERSION}")
    logger.info(f"📊 Environment: {settings.APP_ENV}")
    logger.info(f"🌐 Default Language: {settings.DEFAULT_LANGUAGE}")
    
    # Validate bot token
    if not settings.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not configured in .env file")
        return
    
    # Import bot components (lazy import)
    try:
        from bot.loader_complete import bot, dp
        if not bot or not dp:
            raise ImportError("Bot or Dispatcher initialization failed")
        logger.info("✅ Bot components loaded successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to load bot components: {e}")
        return
    
    try:
        # Start bot polling
        logger.info("🚀 Starting bot polling...")
        logger.info("📡 Bot is listening for updates...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("⏹️  Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("DLBot - Professional Telegram Downloader")
    logger.info("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✅ DLBot shutdown complete")
    except Exception as e:
        logger.critical(f"💥 Critical error: {e}", exc_info=True)
