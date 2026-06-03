@echo off
setlocal enabledelayedexpansion

REM DLBot Deployment Script - Fixed Version
REM Windows CMD version with simplified config

echo.
echo ================================================
echo   DLBot - Bot Deployment (Fixed)
echo ================================================
echo.

cd /d "d:\telgram bot md backup 2- Copy"

REM Check .env exists
if not exist .env (
    echo ❌ ERROR: .env file not found!
    echo Please make sure .env file exists with:
    echo   - BOT_TOKEN=your_token
    echo   - ADMIN_IDS=id1,id2
    echo   - BOT_USERNAME=your_username
    pause
    exit /b 1
)

echo ✅ Configuration file found

REM Step 1: Install/Update dependencies
echo.
echo [1/4] Installing dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo ⚠️  Warning: pip install had issues, but continuing...
)

REM Step 2: Create directories
echo.
echo [2/4] Creating directories...
if not exist logs mkdir logs
if not exist temp_downloads mkdir temp_downloads
if not exist cached_files mkdir cached_files
echo ✅ Directories ready

REM Step 3: Database migration
echo.
echo [3/4] Setting up database...
python -m alembic upgrade head
if errorlevel 1 (
    echo ⚠️  First time setup - creating database...
)

REM Step 4: Start bot
echo.
echo [4/4] Starting bot...
echo.
echo ================================================
echo   Bot is starting... Press Ctrl+C to stop
echo ================================================
echo.

python main.py

echo.
echo ================================================
echo   Bot stopped
echo ================================================
pause
