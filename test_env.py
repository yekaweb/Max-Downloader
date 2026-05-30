#!/usr/bin/env python3
"""
Test script to verify environment setup before running bot
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test critical imports"""
    print("🔍 Testing imports...")
    try:
        import aiogram
        print("  ✅ aiogram")
        import pyrogram
        print("  ✅ pyrogram")
        import sqlalchemy
        print("  ✅ sqlalchemy")
        import alembic
        print("  ✅ alembic")
        import pydantic
        print("  ✅ pydantic")
        import dotenv
        print("  ✅ python-dotenv")
        import loguru
        print("  ✅ loguru")
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_env():
    """Test .env file"""
    print("\n🔍 Testing .env configuration...")
    from dotenv import load_dotenv
    
    # Load .env
    env_file = Path(".env")
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file.absolute()}")
        return False
    
    load_dotenv(env_file)
    
    # Check required variables
    required_vars = [
        "BOT_TOKEN",
        "ADMIN_IDS",
        "BOT_USERNAME",
        "DB_TYPE",
        "DB_PATH",
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"❌ Missing environment variable: {var}")
            return False
        print(f"  ✅ {var}")
    
    print("✅ All environment variables configured!")
    return True

def test_directories():
    """Test required directories"""
    print("\n🔍 Testing directories...")
    required_dirs = [
        Path("logs"),
        Path("temp_downloads"),
        Path("cached_files"),
        Path("migrations"),
        Path("bot"),
        Path("database"),
        Path("modules"),
        Path("locales"),
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"  ⚠️  Creating {dir_path}/")
            dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    print("✅ All directories ready!")
    return True

def test_config():
    """Test config loading"""
    print("\n🔍 Testing config module...")
    try:
        from config import settings
        print(f"  ✅ Config loaded")
        print(f"    - Environment: {settings.env}")
        print(f"    - Bot Token: {settings.telegram.bot_token[:20]}...")
        print(f"    - Database: {settings.database.db_type}")
        print(f"    - Language: {settings.localization.default_language}")
        print("✅ Config module working!")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def main():
    print("=" * 60)
    print("DLBot Environment Test")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Environment": test_env(),
        "Directories": test_directories(),
        "Config": test_config(),
    }
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("=" * 60)
    
    if all_passed:
        print("✅ Environment is ready! You can run: python main.py")
        return 0
    else:
        print("❌ Fix the errors above before running the bot")
        return 1

if __name__ == "__main__":
    sys.exit(main())
