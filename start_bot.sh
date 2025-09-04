#!/bin/bash

# Telegram Bot Startup Script
# This script activates the virtual environment and starts the bot

set -e  # Exit on any error

echo "🤖 Starting Tres Dias Telegram Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements/base.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists and load it for diagnostics
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Make sure to create it with your bot token:"
    echo "   TELEGRAM_BOT_TOKEN=your_token_here"
    echo "   AIRTABLE_API_KEY=your_airtable_key"
    echo "   AIRTABLE_BASE_ID=your_base_id"
    echo ""
    echo "Continuing anyway..."
else
    # Load env vars so the script can access TELEGRAM_BOT_TOKEN for diagnostics.
    # Only accept KEY=VALUE or export KEY=VALUE lines; skip others (e.g., YAML style with colons).
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty and commented lines
        [[ -z "$line" ]] && continue
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        if [[ "$line" =~ ^[[:space:]]*export[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            var="${BASH_REMATCH[1]}"; val="${BASH_REMATCH[2]}"
            export "$var=$val"
        elif [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            var="${BASH_REMATCH[1]}"; val="${BASH_REMATCH[2]}"
            export "$var=$val"
        else
            echo "Skipping non KEY=VALUE line in .env: $line" >&2
        fi
    done < .env
fi

# Install/update dependencies if needed
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements/base.txt

# Diagnostics before start
echo "🧪 Running startup diagnostics..."

# Show Python and PTB versions
echo "🐍 Python version: $(python --version 2>&1)"
PTB_VER=$(python - <<'PY'
try:
    import telegram
    print(getattr(telegram, '__version__', 'unknown'))
except Exception:
    print('unknown')
PY
)
echo "📦 python-telegram-bot version: ${PTB_VER}"

# Check for potentially conflicting bot processes (exclude this script)
echo "🔎 Checking for running bot processes..."
MY_PID=$$
PROC_LIST=$(ps -Ao pid,command | grep -iE 'python.*src\.main|python.*telegram' | grep -v grep | awk -v me="$MY_PID" '$1 != me {print}' || true)
if [ -n "$PROC_LIST" ]; then
    echo "⚠️  Found the following processes that may conflict:"
    echo "$PROC_LIST"
    case "${KILL_OLD_BOT:-}" in
      1|true|TRUE|True|yes|YES|Yes|y|Y)
        echo "🛑 KILL_OLD_BOT is set — stopping old python bot processes"
        pkill -f 'python.*src.main' || true
        pkill -f 'python.*telegram' || true
        ;;
      *)
        echo "ℹ️  Set KILL_OLD_BOT=true to terminate them automatically."
        ;;
    esac
else
    echo "✅ No conflicting processes detected."
fi

# Show webhook info and optionally delete webhook before polling
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo "🌐 Fetching Telegram webhook info..."
    WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo" || true)
    echo "Webhook info: ${WEBHOOK_INFO}"
    case "${FORCE_DELETE_WEBHOOK:-}" in
      1|true|TRUE|True|yes|YES|Yes|y|Y)
        echo "🧹 FORCE_DELETE_WEBHOOK is set — deleting webhook (drop_pending_updates=true)"
        DEL_RES=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=true" || true)
        echo "deleteWebhook result: ${DEL_RES}"
        ;;
      *) ;;
    esac
else
    echo "ℹ️  TELEGRAM_BOT_TOKEN not available to the shell; skipping webhook diagnostics."
fi

# Start the bot
echo "🚀 Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

python -m src.main
