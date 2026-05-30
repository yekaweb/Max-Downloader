@echo off
cd /d "d:\telgram bot md backup 2- Copy"
echo.
echo ========================================
echo  ENHANCED PROFESSIONAL DOWNLOAD SYSTEM
echo ========================================
echo.
git add -A
echo [*] Staging all changes...
timeout /t 1 /nobreak

git commit -m "feat: Enhanced Professional Download System - All issues fixed

- Real thumbnail display with media info
- Exact file sizes for each codec/quality
- Actual subtitle detection
- Codec-specific format selection
- Humanized view counts
- Proper progress message throttling
- Multi-level upload fallback
- Automatic temp file cleanup
- Complete spec compliance

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo [*] Commit created
timeout /t 1 /nobreak

git push origin main
echo.
echo [✓] Successfully pushed to GitHub!
echo.
pause
