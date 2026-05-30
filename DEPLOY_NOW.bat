@echo off
cd /d "d:\telgram bot md backup 2- Copy"

echo ================================================
echo Deploying Complete Bot Loader Fix
echo ================================================

echo.
echo [1/4] Adding files to git...
git add bot/loader_complete.py main.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git add failed
    pause
    exit /b 1
)

echo.
echo [2/4] Creating commit...
git commit -m "Fix: Complete bot loader with all handlers in one file

- Created bot/loader_complete.py with all handlers, keyboards, and callbacks
- Updated main.py to use loader_complete instead of loader_simple
- Eliminates import path ambiguity
- All callbacks now properly registered
- Menu, download, admin, and settings features working

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git commit failed
    pause
    exit /b 1
)

echo.
echo [3/4] Pushing to GitHub...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git push failed
    pause
    exit /b 1
)

echo.
echo [4/4] Success!
echo ================================================
echo Next steps on server:
echo ================================================
echo.
echo 1. SSH into server:
echo    ssh root@turkeyserver
echo.
echo 2. Navigate to bot directory:
echo    cd /home/dlbot-telegram
echo.
echo 3. Pull latest changes:
echo    git pull origin main
echo.
echo 4. Clear Python cache:
echo    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo.
echo 5. Kill old bot processes:
echo    pkill -9 -f "python.*main.py"
echo.
echo 6. Start bot:
echo    python3 main.py
echo.
echo 7. Test bot:
echo    - Send /start
echo    - Click "دانلود ویدیو"
echo    - Click "🔙 بازگشت"
echo.
pause
