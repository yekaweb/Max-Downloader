#!/bin/bash
# Fix bot on server - Complete fix

cd /home/dlbot-telegram

# Kill old process
pkill -9 -f "python3 main.py"
sleep 1

# Get latest code
git fetch origin
git reset --hard origin/main

# Remove old Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
rm -rf .pytest_cache 2>/dev/null

# Pull fresh
git pull

# Show what we have
echo "✅ Code updated!"
echo ""
echo "Files:"
ls bot/keyboards/inline/
echo ""
ls bot/handlers/ | grep download

# Start fresh
echo ""
echo "Starting bot..."
python3 main.py
