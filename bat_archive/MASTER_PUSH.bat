@echo off
REM ============================================================================
REM MASTER DEPLOYMENT SCRIPT - One-Click GitHub Push
REM ============================================================================
REM فایل مسترِ پوش - تمام تغییرات رو یک جا بفرستید
REM
REM استفاده: بعد از هر تغییر فقط این فایل رو رن کنید
REM Usage: Just run this after any changes - everything pushes automatically
REM ============================================================================

cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo ============================================================================
echo 🚀 MASTER DEPLOYMENT SCRIPT - GitHub Auto-Push
echo ============================================================================
echo.

REM Stage ALL changes
echo [*] Staging all changes...
git add -A

REM Get current timestamp for commit message
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

REM Get list of modified files
echo [*] Modified files:
git diff --cached --name-only
echo.

REM Commit with timestamp
echo [*] Committing changes...
git commit -m "chore: Auto-push changes - %mydate% %mytime%

Automated deployment of latest changes.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

REM Check if commit was successful
if %errorlevel% equ 0 (
    echo [✓] Commit successful
    echo.
    echo [*] Pushing to GitHub...
    git push origin main
    
    if %errorlevel% equ 0 (
        echo.
        echo ============================================================================
        echo ✅ SUCCESS! All changes pushed to GitHub
        echo ============================================================================
        echo.
        echo Next: Deploy on server
        echo   ssh root@turkeyserver
        echo   cd /home/dlbot-telegram
        echo   git pull origin main
        echo   pkill -9 -f "python.*main.py"
        echo   python3 main.py
        echo.
    ) else (
        echo ❌ Push failed
        echo Try: git push origin main
    )
) else (
    echo [!] Nothing to commit (no changes)
)

echo.
pause
