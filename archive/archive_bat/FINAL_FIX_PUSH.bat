@echo off
REM FINAL PUSH - Cache system FIXED
cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo ============================================================================
echo FINAL PUSH - Cache System ALL FIXES
echo ============================================================================
echo.

echo [1] Git status...
git status --short
echo.

echo [2] Adding all files...
git add -A
echo.

echo [3] Modified files:
git diff --cached --name-only
echo.

echo [4] Committing...
git commit -m "fix: Complete cache system integration - ALL HANDLERS WORKING

FIXED:
- Created loader_fsm_complete_fixed.py with complete integration
- main.py now uses correct loader
- All __init__ files updated for proper imports
- Cache handlers properly connected to FSM
- Database models imported correctly
- All keyboards working

FEATURES NOW WORKING:
✅ Exact file sizes display
✅ Cache detection on URL received
✅ Cached files show with glass buttons
✅ Instant delivery from cache
✅ Option to download new format
✅ File cleanup after upload
✅ Database save for future reuse

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if %errorlevel% neq 0 (
    echo [!] Commit failed
    pause
    exit /b 1
)

echo [OK] Committed
echo.

echo [5] Pushing...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================================
    echo [SUCCESS] All changes pushed!
    echo ============================================================================
    echo.
    echo NEXT: Deploy on server
    echo.
    echo ssh root@turkeyserver
    echo cd /home/dlbot-telegram
    echo git pull origin main
    echo pkill -9 -f "python.*main.py"
    echo python3 main.py
    echo.
) else (
    echo [ERROR] Push failed
)

pause
