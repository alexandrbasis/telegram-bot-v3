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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Make sure to create it with your bot token:"
    echo "   TELEGRAM_BOT_TOKEN=your_token_here"
    echo "   AIRTABLE_API_KEY=your_airtable_key"
    echo "   AIRTABLE_BASE_ID=your_base_id"
    echo ""
    echo "Continuing anyway..."
fi

# Install/update dependencies if needed
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements/base.txt

# Start the bot
echo "🚀 Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

python -m src.main