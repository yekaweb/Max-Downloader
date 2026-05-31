#!/usr/bin/env python3
"""Test imports to identify issues"""

import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}\n")

# Test 1: Config
try:
    from config_simple import settings
    print("✅ config_simple imported")
    print(f"   BOT_TOKEN: {settings.BOT_TOKEN[:10]}...")
    print(f"   Languages: {settings.SUPPORTED_LANGUAGES}")
except Exception as e:
    print(f"❌ config_simple error: {e}")
    sys.exit(1)

# Test 2: Validators
try:
    from utils.validators import is_valid_url
    print("✅ utils.validators imported")
except Exception as e:
    print(f"❌ utils.validators error: {e}")
    sys.exit(1)

# Test 3: States
try:
    from bot.states.download import DownloadStates
    print("✅ bot.states.download imported")
except Exception as e:
    print(f"❌ bot.states.download error: {e}")
    sys.exit(1)

# Test 4: Aiogram
try:
    from aiogram import Bot, Dispatcher, F
    from aiogram.fsm.storage.memory import MemoryStorage
    print("✅ aiogram imported")
except Exception as e:
    print(f"❌ aiogram error: {e}")
    sys.exit(1)

# Test 5: yt-dlp
try:
    import yt_dlp
    print("✅ yt-dlp imported")
except Exception as e:
    print(f"❌ yt-dlp error: {e}")

# Test 6: Pyrogram
try:
    from pyrogram import Client
    print("✅ pyrogram imported")
except Exception as e:
    print(f"❌ pyrogram error: {e}")

# Test 7: Bot initialization
try:
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    from aiogram import Dispatcher
    dp = Dispatcher(storage=storage)
    print("✅ Bot and Dispatcher initialized")
except Exception as e:
    print(f"❌ Bot/Dispatcher error: {e}")
    sys.exit(1)

# Test 8: Full loader import
try:
    from bot.loader_professional_enhanced import bot as bot2, dp as dp2
    print("✅ bot.loader_professional_enhanced imported")
    print(f"   Handlers registered: {len(dp2.filters_update_handler)}")
except Exception as e:
    print(f"❌ bot.loader_professional_enhanced error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful!")
