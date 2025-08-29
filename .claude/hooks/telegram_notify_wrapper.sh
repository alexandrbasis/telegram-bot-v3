#!/bin/bash
cd "/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3"

# Export environment variables from settings
export TELEGRAM_BOT_TOKEN="8234555039:AAFqOCf6cyTv6Xq3mnZu8c6EJoqMdoGJdOo"
export TELEGRAM_CHAT_ID="311380449"

python3 .claude/hooks/telegram_notify.py
exit 0