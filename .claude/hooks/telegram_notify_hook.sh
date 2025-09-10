#!/bin/bash
cd "/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

python3 .claude/hooks/telegram_notify.py
exit 0