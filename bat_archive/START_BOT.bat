@echo off
setlocal enabledelayedexpansion

REM DLBot Deployment Script
REM Windows CMD version

echo.
echo ================================================
echo DLBot - Automated Deployment and Start
echo ================================================
echo.

cd /d "d:\telgram bot md backup 2- Copy"

REM Step 1: Test environment
echo [1/5] Testing environment...
python test_env.py
if errorlevel 1 (
    echo.
    echo ⚠️  Environment test completed with warnings. Continuing...
)

REM Step 2: Install dependencies
echo.
echo [2/5] Installing Python dependencies...
echo This may take 2-5 minutes...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo ⚠️  Pip install had warnings, but continuing...
)

REM Step 3: Create directories
echo.
echo [3/5] Creating necessary directories...
if not exist logs mkdir logs
if not exist temp_downloads mkdir temp_downloads
if not exist cached_files mkdir cached_files
echo ✅ Directories created

REM Step 4: Database setup
echo.
echo [4/5] Setting up database...
python -m alembic upgrade head
if errorlevel 1 (
    echo ⚠️  Alembic warning (normal on first run)
)

REM Step 5: Start bot
echo.
echo [5/5] Starting bot...
echo ================================================
echo.
python main.py

REM Pause to see output
pause
