@echo off
cd /d "d:\telgram bot md backup 2- Copy"

echo [*] Adding files...
git add -A

echo [*] Committing...
git commit -m "fix: Add keyboard buttons to start/download commands

- Fixed cmd_start to show main_menu_kb (دکمه‌های شیشه‌ای)
- Added download_menu handler
- Added platform selection handler
- Now shows: دانلود ویدیو, تنظیمات, پروفایل, درباره, راهنما

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if %errorlevel% equ 0 (
    echo [*] Pushing...
    git push origin main
    echo [OK] Pushed!
) else (
    echo [!] Commit failed
)

pause
