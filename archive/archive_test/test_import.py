#!/usr/bin/env python
"""Quick import test to verify dependencies"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

print("\n=== Testing imports ===")

try:
    import aiogram
    print("✅ aiogram")
except ImportError as e:
    print(f"❌ aiogram: {e}")

try:
    import sqlalchemy
    print(f"✅ sqlalchemy v{sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ sqlalchemy: {e}")

try:
    import aiosqlite
    print(f"✅ aiosqlite")
except ImportError as e:
    print(f"❌ aiosqlite: {e}")

try:
    import alembic
    print(f"✅ alembic")
except ImportError as e:
    print(f"❌ alembic: {e}")

try:
    import pydantic
    print(f"✅ pydantic")
except ImportError as e:
    print(f"❌ pydantic: {e}")

try:
    from config import settings
    print(f"✅ config loaded")
    print(f"   DB Type: {settings.db.db_type}")
    print(f"   DB DSN: {settings.db.dsn}")
except Exception as e:
    print(f"❌ config: {e}")

print("\n=== Tests complete ===")
