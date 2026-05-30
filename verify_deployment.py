"""
Deployment Verification and Troubleshooting
Verify bot deployment and identify issues
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print("🔍 DLBot Deployment Verification")
print("=" * 70)

checks = {
    "Python Version": False,
    "Required Files": False,
    "Requirements Installed": False,
    ".env Configuration": False,
    "Database File": False,
    "Migrations": False,
    "Bot Configuration": False,
}

# 1. Python Version
print("\n[1/7] Checking Python version...")
try:
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        print(f"✅ Python {py_version}")
        checks["Python Version"] = True
    else:
        print(f"⚠️  Python {py_version} (minimum 3.10 recommended)")
        checks["Python Version"] = True
except Exception as e:
    print(f"❌ {e}")

# 2. Required Files
print("\n[2/7] Checking required files...")
required_files = [
    ".env",
    "requirements.txt",
    "main.py",
    "config.py",
    "alembic.ini",
    "migrations/env.py",
    "bot/loader.py",
    "database/connection.py",
]

files_ok = True
for file in required_files:
    if Path(file).exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - NOT FOUND")
        files_ok = False

checks["Required Files"] = files_ok

# 3. Requirements
print("\n[3/7] Checking Python packages...")
required_packages = [
    "aiogram",
    "pyrogram",
    "sqlalchemy",
    "alembic",
    "pydantic",
    "dotenv",
    "loguru",
]

packages_ok = True
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - NOT INSTALLED")
        packages_ok = False

checks["Requirements Installed"] = packages_ok

# 4. .env Configuration
print("\n[4/7] Checking .env configuration...")
env_ok = False
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["BOT_TOKEN", "ADMIN_IDS", "BOT_USERNAME"]
    env_missing = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
            env_ok = True
        else:
            print(f"❌ {var} - MISSING")
            env_missing.append(var)
    
    if env_missing:
        print(f"\n⚠️  Missing: {', '.join(env_missing)}")
        print("Edit .env file and set these variables")
        env_ok = False if not any(os.getenv(v) for v in required_vars) else True
    
    checks[".env Configuration"] = env_ok
except Exception as e:
    print(f"❌ {e}")
    checks[".env Configuration"] = False

# 5. Database File
print("\n[5/7] Checking database...")
db_ok = True
db_path = Path("dlbot.db")
if db_path.exists():
    size = db_path.stat().st_size
    print(f"✅ dlbot.db exists ({size} bytes)")
    checks["Database File"] = True
else:
    print("⚠️  dlbot.db not found (will be created on first run)")
    checks["Database File"] = True

# 6. Migrations
print("\n[6/7] Checking migrations...")
migrations_ok = False
try:
    versions_dir = Path("migrations/versions")
    if versions_dir.exists():
        migration_files = list(versions_dir.glob("*.py"))
        if migration_files:
            print(f"✅ Found {len(migration_files)} migration(s)")
            for f in migration_files:
                print(f"   - {f.name}")
            migrations_ok = True
        else:
            print("⚠️  No migration files found (will be created)")
            migrations_ok = True
    else:
        print("⚠️  migrations/versions folder missing")
        migrations_ok = False
    checks["Migrations"] = migrations_ok
except Exception as e:
    print(f"❌ {e}")

# 7. Bot Configuration
print("\n[7/7] Checking bot configuration...")
try:
    from config import settings
    print(f"✅ Config loaded successfully")
    print(f"   - Environment: {settings.env}")
    print(f"   - Bot Token: {settings.telegram.bot_token[:20]}...")
    print(f"   - Admin IDs: {settings.telegram.admin_ids}")
    print(f"   - Database: {settings.database.db_type}")
    checks["Bot Configuration"] = True
except Exception as e:
    print(f"❌ {e}")
    checks["Bot Configuration"] = False

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

passed = sum(1 for v in checks.values() if v)
total = len(checks)

for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")

print("\n" + "-" * 70)
print(f"Result: {passed}/{total} checks passed")

if passed == total:
    print("\n🎉 Everything looks good! You can start the bot:")
    print("\n   python main.py")
    print("\nOr use the batch file:")
    print("\n   START_BOT.bat")
    sys.exit(0)
else:
    print("\n⚠️  Some issues found. Please fix them before running.")
    sys.exit(1)
