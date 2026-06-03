@echo off
cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo ========================================
echo DLBot Deployment Script
echo ========================================
echo.

REM Test environment
echo [1/4] Testing environment...
python test_env.py
if errorlevel 1 (
    echo Environment test failed!
    pause
    exit /b 1
)

REM Install/update requirements
echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo pip install failed!
    pause
    exit /b 1
)

REM Run database migrations
echo.
echo [3/4] Setting up database...
alembic upgrade head
if errorlevel 1 (
    echo Database migration failed - trying alternative...
    python -m alembic upgrade head
)

REM Start bot
echo.
echo [4/4] Starting bot...
echo.
python main.py

pause
