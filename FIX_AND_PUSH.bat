@echo off
REM Fix bot - remove duplicate and push
cd "d:\telgram bot md backup 2- Copy"

REM Remove duplicate file
del bot\keyboards\inline.py

REM Git commands
git add -A
git commit -m "Fix: Remove duplicate inline.py - use inline/__init__.py only"
git push

echo ✅ Push complete!
pause
