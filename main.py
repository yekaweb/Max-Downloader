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
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "":
        logger.error("❌ BOT_TOKEN not configured in .env file")
        logger.error("   Please add BOT_TOKEN=your_token_here to .env file")
        return
    
    logger.info(f"✅ Bot token found: {settings.BOT_TOKEN[:15]}...")
    
    # Import bot components (lazy import)
    try:
        logger.info("📦 Loading bot components...")
        from bot.loader_professional_enhanced import bot, dp
        
        if not bot:
            raise ImportError("Bot initialization failed - bot is None")
        if not dp:
            raise ImportError("Dispatcher initialization failed - dp is None")
            
        logger.info("✅ Bot components loaded successfully (Enhanced Professional Download System)")
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
    
    try:
        # Start bot polling
        logger.info("🚀 Starting bot polling...")
        logger.info("📡 Bot is listening for updates...")
        logger.info("💡 Send /start command to the bot to test")
        resolved_updates = dp.resolve_used_update_types()
        logger.info(f"📨 Allowed updates for polling: {resolved_updates}")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️  Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error during polling: {e}", exc_info=True)
    finally:
        try:
            await bot.session.close()
            logger.info("✅ Bot session closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing bot session: {e}")


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
