#!/bin/bash
#
# DLBot Restart Script - Restart bot with Phase 1-5 Integrations
# 

echo "=================================================="
echo "🤖 DLBot - Phases 1-5 Integration Restart"
echo "=================================================="

# Kill existing bot process
echo "⏹️  Stopping existing bot..."
pkill -f "python3 main.py" 2>/dev/null || true
sleep 2

# Check if bot is still running
if pgrep -f "python3 main.py" > /dev/null; then
    echo "⚠️  Bot still running, killing with SIGKILL..."
    pkill -9 -f "python3 main.py" || true
    sleep 2
fi

# Clear old logs
echo "🧹 Clearing old logs..."
rm -f logs/bot.log

# Start new bot
echo ""
echo "🚀 Starting DLBot with Phase 1-5 Optimizations..."
echo ""
echo "✅ Phases enabled:"
echo "   🔵 Phase 1: Caching System"
echo "   🟢 Phase 2: Parallel Download (3x connections)"
echo "   🟡 Phase 3: Stream Upload (5MB chunks)"
echo "   🟠 Phase 4: Compression (H.265, -40% size)"
echo "   🔴 Phase 5: Queue Management (Priority-based)"
echo ""

# Start bot in background
python3 main.py >> logs/bot.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started (PID: $BOT_PID)"
echo ""
echo "📊 Log file: logs/bot.log"
echo ""
echo "💡 To monitor logs:"
echo "   tail -f logs/bot.log | grep -E 'PHASES|Download|Upload|Compress'"
echo ""
echo "💡 To see real-time optimization:"
echo "   tail -f logs/bot.log | grep '\\[PHASES\\]'"
echo ""
echo "=================================================="
