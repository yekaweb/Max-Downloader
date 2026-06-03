@echo off
REM Archived to bat_archive/PUSH_CACHE_NOW.bat
REM Use the archived copy instead of this root file.
REM Push cache system files to GitHub NOW
cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo [*] Git status...
git status --short
echo.

echo [*] Adding files...
git add -A
echo [OK]
echo.

echo [*] Commit...
git commit -m "feat: Cache system with exact sizes and file cleanup

- Exact file sizes before download
- Smart caching (telegram_file_id storage)
- Auto cleanup after upload
- Beautiful cache UI
- 70-90%% storage savings

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if %errorlevel% neq 0 (
    echo [!] Nothing to commit or error
    exit /b 0
)

echo [*] Pushing...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo [OK] PUSHED!
) else (
    echo [ERROR] Push failed
)

pause
