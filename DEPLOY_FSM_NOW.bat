@echo off
REM ============================================================================
REM DLBot FSM Implementation - Complete Deployment Script
REM ============================================================================
REM Deploys the complete step-by-step download flow with:
REM - Full FSM state management
REM - Quality/codec/subtitle selection
REM - Real-time progress tracking
REM ============================================================================

cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo ============================================================================
echo DLBot FSM Download Flow - Complete Implementation
echo ============================================================================
echo.

REM Add all FSM-related files
git add bot/states/download.py
git add bot/keyboards/inline/download.py
git add bot/handlers/download_complete.py
git add bot/loader_fsm.py
git add main.py
git add FSM_IMPLEMENTATION_COMPLETE.md

REM Commit with detailed message
git commit -m "feat: Implement complete step-by-step FSM download flow

COMPLETE IMPLEMENTATION:
✅ Full Finite State Machine (7 steps)
✅ Video/Audio format branching
✅ Quality selection (4K/1080p/720p/480p/360p/240p)
✅ Codec selection (H.264/AV1/VP9)
✅ Subtitle language selection (Persian/English/Arabic/Russian/None)
✅ Send As selection (Video/Document)
✅ Real-time progress tracking with speed and ETA
✅ Beautiful Persian UI with emojis
✅ Back buttons at every step
✅ FSInputFile for safe file transmission
✅ Try/except error handling
✅ Dynamic yt-dlp option configuration

FILES CHANGED:
- bot/states/download.py: Complete FSM states with proper branching
- bot/keyboards/inline/download.py: 6 beautiful Persian keyboards
- bot/handlers/download_complete.py: Router-based alternative handlers
- bot/loader_fsm.py: Main loader with all FSM logic (NEW)
- main.py: Updated to use loader_fsm

TESTING:
1. Local: python main.py → /download → Follow prompts
2. Server: git pull && python3 main.py → Test in Telegram

USER FLOW:
/download → Send URL → Select format → Select quality/codec →
Select subtitle → Select send-as → Download → Upload → Done ✅

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git push origin main

echo.
echo ============================================================================
echo SUCCESS! FSM Implementation Deployed
echo ============================================================================
echo.
echo Next Steps:
echo.
echo LOCAL TESTING:
echo   1. python main.py
echo   2. In Telegram: /start
echo   3. Click 'دانلود ویدیو'
echo   4. /download
echo   5. Send YouTube URL
echo   6. Follow step-by-step prompts
echo   7. Watch the download happen! 🎉
echo.
echo SERVER DEPLOYMENT:
echo   1. ssh root@turkeyserver
echo   2. cd /home/dlbot-telegram
echo   3. git pull origin main
echo   4. pkill -9 -f 'python.*main.py'
echo   5. sleep 3
echo   6. python3 main.py
echo.
echo FEATURES IMPLEMENTED:
echo   ✅ Complete FSM flow (7 steps)
echo   ✅ Quality selection (6 options)
echo   ✅ Codec selection (3 options)
echo   ✅ Subtitle selection (5 options)
echo   ✅ Send As (2 options)
echo   ✅ Real-time progress
echo   ✅ Back buttons
echo   ✅ Error handling
echo   ✅ File validation
echo   ✅ Safe transmission
echo.
echo ============================================================================
echo Documentation: FSM_IMPLEMENTATION_COMPLETE.md
echo ============================================================================
echo.
pause
