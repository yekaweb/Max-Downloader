#!/usr/bin/env bash

# run_bot.sh - Bot Startup Script

echo "=========================================="
echo "DLBot - Telegram Downloader Bot"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    exit 1
fi
python3 --version
echo ""

# Step 2: Install requirements
echo "[2/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully!"
echo ""

# Step 3: Check .env file
echo "[3/4] Checking .env configuration..."
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found"
    echo "Please copy .env.example to .env and fill in your values"
    exit 1
fi

# Check if BOT_TOKEN is set
if grep -q "BOT_TOKEN=" .env; then
    BOT_TOKEN=$(grep "BOT_TOKEN=" .env | cut -d '=' -f 2)
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" == "YOUR_TELEGRAM_BOT_TOKEN" ]; then
        echo "ERROR: BOT_TOKEN is not configured properly"
        echo "Please set BOT_TOKEN in .env file"
        exit 1
    fi
    echo "✓ BOT_TOKEN is configured"
else
    echo "ERROR: BOT_TOKEN not found in .env"
    exit 1
fi

# Check if ADMIN_IDS is set
if grep -q "ADMIN_IDS=" .env; then
    ADMIN_IDS=$(grep "ADMIN_IDS=" .env | cut -d '=' -f 2)
    if [ -z "$ADMIN_IDS" ] || [ "$ADMIN_IDS" == "YOUR_ADMIN_USER_IDS_COMMA_SEPARATED" ]; then
        echo "WARNING: ADMIN_IDS is not configured"
        echo "Bot will work but admin features may not be available"
    else
        echo "✓ ADMIN_IDS is configured"
    fi
fi

echo ".env file validated!"
echo ""

# Step 4: Start bot
echo "[4/4] Starting bot..."
echo "=========================================="
echo ""

python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Bot crashed or exited with error"
    echo "Check the logs above for details"
    exit 1
fi
