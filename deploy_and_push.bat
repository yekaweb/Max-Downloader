@echo off
REM Deploy script for Windows - Push updates to GitHub

setlocal enabledelayedexpansion

REM Colors (Windows doesn't support ANSI by default, using Unicode bullets)
set GREEN=[92m
set YELLOW=[93m
set RED=[91m
set NC=[0m

echo.
echo ==================================================
echo 🚀 DLBot Deployment Script (Windows)
echo ==================================================
echo.

REM 1. Check if we're in correct directory
if not exist "main.py" (
    echo ❌ Error: main.py not found in current directory
    echo    Please run this script from project root directory
    pause
    exit /b 1
)

REM 2. Check git status
echo 📊 Git Status:
git status --short
echo.

REM 3. Show staged changes
echo 📋 Current changes:
git diff --name-only
echo.

REM 4. Ask for confirmation
set /p confirm="Proceed with deployment? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

REM 5. Get commit message
echo.
set /p commit_msg="📝 Commit message: "

if "!commit_msg!"=="" (
    echo ❌ Commit message cannot be empty
    pause
    exit /b 1
)

REM 6. Stage all changes
echo.
echo 📦 Staging changes...
git add .

REM 7. Show what will be committed
echo.
echo 🔍 Changes to commit:
git diff --cached --stat

REM 8. Confirm again
echo.
set /p confirm2="Confirm commit and push? (y/n): "
if /i not "%confirm2%"=="y" (
    echo Cancelled.
    git reset
    pause
    exit /b 0
)

REM 9. Commit
echo.
echo 💾 Creating commit...
git commit -m "!commit_msg!" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if errorlevel 1 (
    echo ❌ Commit failed
    pause
    exit /b 1
)

REM 10. Push
echo.
echo 🚀 Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo ❌ Push failed
    pause
    exit /b 1
)

REM 11. Success
echo.
echo ✅ Deployment successful!
echo.
echo 📊 Commit info:
git log -1 --oneline
echo.
echo 🔗 View on GitHub:
echo    https://github.com/yekaweb/dlbot-telegram/commits/main
echo.
echo ✨ Done!
pause
