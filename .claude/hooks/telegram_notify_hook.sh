#!/bin/bash
cd "/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3"

# Export environment variables from settings
export CLAUDE_HOOK_BOT_TOKEN="[REDACTED_FOR_SECURITY]"
export CLAUDE_HOOK_CHAT_ID="311380449"

python3 .claude/hooks/telegram_notify.py
exit 0