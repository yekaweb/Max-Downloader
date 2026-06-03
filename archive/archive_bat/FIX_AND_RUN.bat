@echo off
REM Archived to bat_archive/FIX_AND_RUN.bat
REM Use the archived copy instead of this root file.
REM Quick fix for distutils error
echo Installing setuptools (distutils replacement)...
pip install setuptools --upgrade --quiet

echo.
echo Starting bot...
python main.py

pause
