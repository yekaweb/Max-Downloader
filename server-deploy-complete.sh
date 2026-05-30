#!/bin/bash

# ============================================
# DLBot Complete Deployment Fix on Server
# ============================================

set -e

echo "════════════════════════════════════════"
echo "🚀 DLBot Complete Bot Loader Deployment"
echo "════════════════════════════════════════"
echo ""

cd /home/dlbot-telegram

# 1. Pull latest changes
echo "📥 [1/7] Pulling latest changes..."
git fetch origin
git reset --hard origin/main
echo "✅ Pull complete"
echo ""

# 2. Clear Python cache
echo "🗑️  [2/7] Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache cleared"
echo ""

# 3. Kill old processes
echo "💀 [3/7] Killing old bot processes..."
pkill -9 -f "python.*main.py" || true
sleep 2
echo "✅ Old processes killed"
echo ""

# 4. Verify file structure
echo "📂 [4/7] Verifying file structure..."
ls -la bot/loader_complete.py
echo "✅ loader_complete.py exists"
echo ""

# 5. Test import
echo "🔍 [5/7] Testing bot import..."
python3 << 'EOF'
try:
    from bot.loader_complete import bot, dp
    if bot and dp:
        print("✅ Bot and Dispatcher loaded successfully")
    else:
        print("❌ Bot or Dispatcher is None")
        exit(1)
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)
EOF
echo ""

# 6. Start bot
echo "🤖 [6/7] Starting bot..."
python3 main.py &
BOT_PID=$!
sleep 3

# Check if process is still running
if kill -0 $BOT_PID 2>/dev/null; then
    echo "✅ Bot started successfully (PID: $BOT_PID)"
else
    echo "❌ Bot failed to start"
    tail -50 logs/dlbot.log 2>/dev/null || echo "No logs yet"
    exit 1
fi
echo ""

# 7. Summary
echo "════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE"
echo "════════════════════════════════════════"
echo ""
echo "Bot PID: $BOT_PID"
echo "Bot Status: Running ✅"
echo ""
echo "Test commands:"
echo "  /start      - Show main menu"
echo "  /help       - Show help"
echo "  /download   - Show download menu"
echo "  /admin      - Show admin panel (if admin)"
echo ""
echo "Monitoring:"
echo "  tail -f logs/dlbot.log"
echo ""
echo "To stop bot:"
echo "  pkill -9 -f 'python.*main.py'"
echo ""
