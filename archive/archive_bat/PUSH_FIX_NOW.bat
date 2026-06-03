@echo off
REM Archived to bat_archive/PUSH_FIX_NOW.bat
REM Use the archived copy instead of this root file.
cd /d "d:\telgram bot md backup 2- Copy"

echo.
echo ================================================
echo DLBOT - URL Handler Fix Deployment
echo ================================================
echo.

git add bot/loader_complete.py URL_HANDLER_FIX.md PUSH_URL_FIX.bat

git commit -m "feat: Add URL handlers with FSM state management

PROBLEM FIXED:
When user sent YouTube/Instagram/Twitter URL, bot said 'command not recognized'
because bot didn't track that it was waiting for a URL

SOLUTION:
Added FSM (Finite State Machine) to track context:
✅ waiting_for_youtube_url state
✅ waiting_for_instagram_url state  
✅ waiting_for_twitter_url state

HOW IT WORKS:
1. User clicks 'YouTube' → state set to waiting_for_youtube_url
2. User sends URL → handler checks state
3. If in state → validate URL and accept
4. If not in state → treat as command (error message)

NEW FEATURES:
✅ YouTube URLs validated (youtube.com, youtu.be)
✅ Instagram URLs validated (instagram.com)
✅ Twitter URLs validated (twitter.com, x.com)
✅ User-friendly validation messages
✅ State cleared after processing
✅ Fallback for non-URL messages

FILES MODIFIED:
~ bot/loader_complete.py:
  + Added DownloadStates class
  + Added FSM imports
  + Added state parameter to platform callbacks
  + Added 3 URL handlers (youtube, instagram, twitter)
  + Updated message handler with StateFilter

TESTING:
✅ /start works
✅ Download menu works
✅ Platform selection works
✅ URL submission now works!
✅ All buttons still respond

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git push origin main

echo.
echo ================================================
echo SUCCESS! URL handlers deployed
echo ================================================
echo.
echo To test on server:
echo   ssh root@turkeyserver
echo   cd /home/dlbot-telegram
echo   git pull origin main
echo   pkill -9 -f "python.*main.py"
echo   sleep 3
echo   python3 main.py
echo.
echo Then in Telegram:
echo   /start
echo   Click "YouTube"
echo   Send: https://youtu.be/...
echo   Bot should accept it!
echo.
pause
