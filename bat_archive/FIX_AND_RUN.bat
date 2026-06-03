@echo off
REM Quick fix for distutils error
echo Installing setuptools (distutils replacement)...
pip install setuptools --upgrade --quiet

echo.
echo Starting bot...
python main.py

pause
