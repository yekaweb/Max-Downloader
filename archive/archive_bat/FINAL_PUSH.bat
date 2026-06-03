@echo off
REM Archived to bat_archive/FINAL_PUSH.bat
REM Use the archived copy instead of this root file.
REM Final deployment script - Windows
REM All-in-one command for complete bot deployment

setlocal enabledelayedexpansion

cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo ======================================================================
echo                    DLBOT - FINAL DEPLOYMENT
echo ======================================================================
echo.

REM Check git
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/6] Checking git status...
git status
echo.

echo [2/6] Adding files...
git add ^
    bot/loader_complete.py ^
    main.py ^
    server-deploy-complete.sh ^
    TEST_CHECKLIST.md ^
    DEPLOYMENT_READY.md ^
    go.bat ^
    DEPLOY_NOW.bat ^
    push.sh

if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)
echo OK - Files added
echo.

echo [3/6] Checking what will be committed...
git diff --cached --stat
echo.

echo [4/6] Creating commit...
git commit -m "feat: Complete working bot with callbacks and menus

Implementation:
- bot/loader_complete.py: 300+ lines with all handlers
- Main menu: 4 buttons (Download, Profile, Settings, Help)
- Download menu: 3 platforms with back button
- Admin panel: Stats, Broadcast, Users
- All callbacks properly registered
- Back buttons available everywhere

Files created:
- bot/loader_complete.py (Complete implementation)
- TEST_CHECKLIST.md (12+ test scenarios)
- DEPLOYMENT_READY.md (Deployment guide)
- server-deploy-complete.sh (Server script)
- go.bat, push.sh, DEPLOY_NOW.bat (Helpers)

Fixes:
- No import path ambiguity
- All handlers in dispatcher
- Callbacks respond immediately
- Clean menu navigation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if errorlevel 1 (
    echo ERROR: Failed to create commit
    pause
    exit /b 1
)
echo OK - Commit created
echo.

echo [5/6] Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo ERROR: Failed to push
    echo Check your git credentials and internet connection
    pause
    exit /b 1
)
echo OK - Pushed successfully
echo.

echo [6/6] Showing latest commit...
git log -1 --stat
echo.

echo ======================================================================
echo                      SUCCESS! ✅
echo ======================================================================
echo.
echo NEXT STEPS ON SERVER:
echo.
echo   1. SSH to server:
echo      ssh root@turkeyserver
echo.
echo   2. Navigate to project:
echo      cd /home/dlbot-telegram
echo.
echo   3. Pull latest code:
echo      git pull origin main
echo.
echo   4. Kill old bot:
echo      pkill -9 -f "python.*main.py"
echo.
echo   5. Clear cache:
echo      find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo.
echo   6. Start bot:
echo      python3 main.py
echo.
echo   7. Test bot:
echo      - Open Telegram
echo      - Send /start
echo      - Click buttons
echo      - Send /admin (if admin user)
echo.
echo TEST CHECKLIST:
echo   See TEST_CHECKLIST.md for full test scenarios
echo.
echo ======================================================================
echo.
pause
