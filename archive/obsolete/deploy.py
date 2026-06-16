#!/usr/bin/env python3
"""
DLBot Deployment Script
Complete setup and start process
"""

import sys
import os
import subprocess
from pathlib import Path

def run_cmd(cmd, description):
    """Run command and report status"""
    print(f"\n⏳ {description}...")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} succeeded")
            return True
        else:
            print(f"⚠️  {description} returned code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("=" * 70)
    print("🤖 DLBot - Automated Deployment & Start")
    print("=" * 70)
    
    os.chdir("d:\\telgram bot md backup 2- Copy")
    
    # Step 1: Test environment
    print("\n[STEP 1/5] Testing environment...")
    run_cmd("python test_env.py", "Environment test")
    
    # Step 2: Install requirements
    print("\n[STEP 2/5] Installing Python dependencies...")
    run_cmd("pip install -r requirements.txt --quiet", "Pip install")
    
    # Step 3: Create necessary directories
    print("\n[STEP 3/5] Creating directories...")
    dirs = ["logs", "temp_downloads", "cached_files"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"  ✅ {d}/")
    
    # Step 4: Database migration
    print("\n[STEP 4/5] Setting up database schema...")
    if not run_cmd("alembic upgrade head", "Database migration"):
        print("  ⚠️  Trying alternative migration method...")
        run_cmd("python -m alembic upgrade head", "Alternative migration")
    
    # Step 5: Start bot
    print("\n[STEP 5/5] Starting bot...")
    print("=" * 70)
    print("🚀 Bot is starting...\n")
    
    run_cmd("python main.py", "Bot startup")
    
    print("\n" + "=" * 70)
    print("Bot stopped.")
    print("=" * 70)

if __name__ == "__main__":
    main()
