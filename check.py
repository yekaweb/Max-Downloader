#!/usr/bin/env python3
"""
Quick verification before running bot
"""
import sys
import os
from pathlib import Path

def check():
    print("\n" + "="*60)
    print("🔍 DLBot - Pre-Launch Verification")
    print("="*60 + "\n")
    
    issues = []
    
    # 1. .env file
    print("1️⃣  Checking .env file...")
    if not Path(".env").exists():
        issues.append("❌ .env file not found")
    else:
        print("   ✅ .env exists")
        with open(".env") as f:
            content = f.read()
            if "BOT_TOKEN=" in content:
                print("   ✅ BOT_TOKEN configured")
            else:
                issues.append("❌ BOT_TOKEN not in .env")
            
            if "ADMIN_IDS=" in content:
                print("   ✅ ADMIN_IDS configured")
            else:
                issues.append("❌ ADMIN_IDS not in .env")
    
    # 2. Python imports
    print("\n2️⃣  Checking imports...")
    imports = ["aiogram", "pyrogram", "sqlalchemy", "loguru", "dotenv"]
    for imp in imports:
        try:
            __import__(imp)
            print(f"   ✅ {imp}")
        except ImportError:
            issues.append(f"❌ {imp} not installed")
    
    # 3. Config
    print("\n3️⃣  Checking config...")
    try:
        from config_simple import settings
        print(f"   ✅ Config loaded")
        print(f"   ✅ BOT_TOKEN: {settings.BOT_TOKEN[:20]}...")
        print(f"   ✅ Database: {settings.DB_TYPE}")
        print(f"   ✅ Environment: {settings.APP_ENV}")
    except Exception as e:
        issues.append(f"❌ Config error: {e}")
    
    # 4. Directories
    print("\n4️⃣  Checking directories...")
    dirs = ["bot", "database", "modules", "migrations", "locales"]
    for d in dirs:
        if Path(d).exists():
            print(f"   ✅ {d}/")
        else:
            issues.append(f"❌ {d}/ missing")
    
    # 5. Database models
    print("\n5️⃣  Checking database models...")
    try:
        from database.models import Base, User
        print(f"   ✅ Models loaded")
    except Exception as e:
        issues.append(f"❌ Models error: {e}")
    
    # Summary
    print("\n" + "="*60)
    if issues:
        print("⚠️  ISSUES FOUND:\n")
        for issue in issues:
            print(f"   {issue}")
        print("\n" + "="*60)
        return False
    else:
        print("✅ ALL CHECKS PASSED - Ready to run!\n")
        print("To start the bot, run:")
        print("   python main.py")
        print("\n" + "="*60)
        return True

if __name__ == "__main__":
    success = check()
    sys.exit(0 if success else 1)
