#!/bin/bash
cd "/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3"

# Load only Claude hook environment variables from .env file
if [ -f .env ]; then
    export CLAUDE_HOOK_BOT_TOKEN=$(grep '^CLAUDE_HOOK_BOT_TOKEN=' .env | cut -d'=' -f2-)
    export CLAUDE_HOOK_CHAT_ID=$(grep '^CLAUDE_HOOK_CHAT_ID=' .env | cut -d'=' -f2-)
fi

python3 .claude/hooks/telegram_notify.py
exit 0