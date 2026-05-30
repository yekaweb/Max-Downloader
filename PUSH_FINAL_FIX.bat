@echo off
cd /d "d:\telgram bot md backup 2- Copy"

echo [*] Adding files...
git add -A

echo [*] Committing...
git commit -m "fix: Working download with proper progress and error handling

- Removed broken SessionLocal import (was causing errors)
- Simplified download flow without caching (just download)
- Fixed 'Cannot write to closing transport' error
- Removed static progress message
- Basic working version first

Status:
✅ /start shows menu buttons
✅ /download works
✅ Video downloads work
✅ Audio downloads work
✅ No more import errors
✅ No more transport closing errors

Next phase: Add cache system after core works

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if %errorlevel% equ 0 (
    echo [*] Pushing...
    git push origin main
    echo [OK] Pushed!
) else (
    echo [!] Commit failed
)

pause
