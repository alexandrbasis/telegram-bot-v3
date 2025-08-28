#!/usr/bin/env python3
"""
Telegram notification hook for Claude Code
Sends informative messages about completed tasks
"""

import json
import sys
import os
import re
from datetime import datetime
import subprocess

def get_last_action_summary():
    """Extract last meaningful action from transcript"""
    transcript_path = sys.stdin_data.get("transcript_path", "")
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
            
        # Look at last few messages for tool usage
        for line in reversed(lines[-20:]):
            try:
                entry = json.loads(line.strip())
                if entry.get("type") == "tool_use":
                    tool_name = entry.get("name", "")
                    params = entry.get("input", {})
                    return format_tool_action(tool_name, params)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    
    return None

def format_tool_action(tool_name, params):
    """Format tool action into readable description"""
    if tool_name == "Task":
        desc = params.get("description", "")
        agent_type = params.get("subagent_type", "")
        if desc and agent_type:
            return f"🎯 {agent_type}: {desc}"
        return f"🎯 Subagent: {desc or 'completed task'}"
    
    elif tool_name == "Write":
        file_path = params.get("file_path", "")
        if file_path:
            filename = os.path.basename(file_path)
            return f"📝 Created {filename}"
    
    elif tool_name in ["Edit", "MultiEdit"]:
        file_path = params.get("file_path", "")
        if file_path:
            filename = os.path.basename(file_path)
            return f"✏️ Modified {filename}"
    
    elif tool_name == "Bash":
        command = params.get("command", "")
        if "git commit" in command:
            return "📦 Committed changes"
        elif "git push" in command:
            return "🚀 Pushed to remote"
        elif "pytest" in command or "test" in command:
            return "🧪 Ran tests"
        elif "npm run" in command or "yarn" in command:
            return "⚙️ Build/compile"
        elif command:
            # Truncate long commands
            cmd_short = command[:30] + "..." if len(command) > 30 else command
            return f"💻 Ran: {cmd_short}"
    
    elif tool_name.startswith("mcp__linear__"):
        if "create_issue" in tool_name:
            return "📋 Created Linear issue"
        elif "update_issue" in tool_name:
            return "🔄 Updated Linear issue"
        elif "create_comment" in tool_name:
            return "💬 Added Linear comment"
    
    elif tool_name == "Grep":
        pattern = params.get("pattern", "")
        return f"🔍 Searched: {pattern[:20]}..."
    
    elif tool_name == "Read":
        file_path = params.get("file_path", "")
        if file_path:
            filename = os.path.basename(file_path)
            return f"👀 Read {filename}"
    
    return f"🤖 Used {tool_name}"

def send_telegram_message(message):
    """Send message to Telegram"""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("⚠️ Telegram credentials not set", file=sys.stderr)
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-d", f"chat_id={chat_id}",
            "-d", f"text={message}",
            "-d", "parse_mode=HTML"
        ], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to send Telegram message", file=sys.stderr)
        return False

def main():
    global sys.stdin_data
    
    try:
        sys.stdin_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("❌ Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    
    hook_event = sys.stdin_data.get("hook_event_name", "")
    time_str = datetime.now().strftime("%H:%M")
    
    # Handle Notification events
    if hook_event == "Notification":
        notification_msg = sys.stdin_data.get("message", "")
        if "permission" in notification_msg.lower():
            message = f"🔐 Needs permission {time_str}"
        elif "waiting" in notification_msg.lower():
            message = f"⏳ Waiting for input {time_str}"
        else:
            message = f"ℹ️ {notification_msg[:30]}... {time_str}"
        send_telegram_message(message)
        return
    
    # Get action summary for Stop/SubagentStop
    action = get_last_action_summary()
    
    if hook_event == "Stop":
        if action:
            message = f"{action} ✅ {time_str}"
        else:
            message = f"🤖 Claude finished ✅ {time_str}"
    
    elif hook_event == "SubagentStop":
        if action and action.startswith("🎯"):
            message = f"{action} ✅ {time_str}"
        else:
            message = f"🎯 Subagent finished ✅ {time_str}"
    
    else:
        message = f"🤖 {hook_event} ✅ {time_str}"
    
    # Send notification
    send_telegram_message(message)

if __name__ == "__main__":
    main()