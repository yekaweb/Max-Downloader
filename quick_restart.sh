#!/bin/bash

# Make script executable
chmod +x /home/reza/Max-Downloader/restart_bot_with_phases.sh

# Restart bot
cd /home/reza/Max-Downloader

# Kill old process
pkill -9 -f "python3 main.py" 2>/dev/null || true
sleep 2

# Start new bot with phases integration
echo "🚀 Starting DLBot with Phase 1-5 Integration..."
python3 main.py
