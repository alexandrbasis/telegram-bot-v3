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

def get_last_action_summary(stdin_data):
    """Extract last meaningful action from various sources"""
    
    # Try git status to see what files were modified
    try:
        cwd = stdin_data.get("cwd", "")
        if cwd and os.path.exists(cwd):
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                modified_files = []
                new_files = []
                
                for line in lines:
                    if line.startswith(' M') or line.startswith('M '):
                        filename = os.path.basename(line[3:].strip())
                        modified_files.append(filename)
                    elif line.startswith('A ') or line.startswith('??'):
                        filename = os.path.basename(line[3:].strip())
                        new_files.append(filename)
                
                if new_files:
                    return f"📝 Created {new_files[0]}"
                elif modified_files:
                    return f"✏️ Updated {modified_files[0]}"
                    
    except Exception:
        pass
    
    # Fallback: try to infer from current directory
    cwd = stdin_data.get("cwd", "")
    if cwd:
        if "telegram-bot" in cwd:
            return "🤖 Updated telegram bot"
        elif "claude" in cwd.lower():
            return "🔧 Updated Claude Code settings"
        else:
            project_name = os.path.basename(cwd)
            if project_name and project_name != "/":
                return f"💻 Updated {project_name}"
    
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
            return f"📝 Created new file: {filename}"
    
    elif tool_name in ["Edit", "MultiEdit"]:
        file_path = params.get("file_path", "")
        if file_path:
            filename = os.path.basename(file_path)
            return f"✏️ Updated file: {filename}"
    
    elif tool_name == "Bash":
        command = params.get("command", "")
        description = params.get("description", "")
        
        if "git commit" in command:
            return "📦 Committed changes to repository"
        elif "git push" in command:
            return "🚀 Pushed changes to remote repository"
        elif "pytest" in command or "test" in command:
            if "coverage" in command:
                return "🧪 Ran tests with coverage analysis"
            else:
                return "🧪 Ran test suite"
        elif "npm run" in command or "yarn" in command:
            return "⚙️ Built and compiled project"
        elif "flake8" in command or "mypy" in command:
            return "🔍 Code quality check completed"
        elif description and len(description) > 10:
            return f"💻 {description}"
        elif command:
            # Truncate long commands
            cmd_short = command[:40] + "..." if len(command) > 40 else command
            return f"💻 Executed: {cmd_short}"
    
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
    bot_token = os.environ.get("CLAUDE_HOOK_BOT_TOKEN")
    chat_id = os.environ.get("CLAUDE_HOOK_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("⚠️ Telegram credentials not set", file=sys.stderr)
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        # Use proper URL encoding to avoid issues with special characters
        import urllib.parse
        encoded_message = urllib.parse.quote_plus(message)
        
        result = subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-d", f"chat_id={chat_id}",
            "-d", f"text={encoded_message}",
            "-d", "parse_mode=HTML"
        ], capture_output=True, check=True, text=True)
        print(f"✅ Sent: {message}", file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to send Telegram message: {e.stderr}", file=sys.stderr)
        return False

def main():
    try:
        stdin_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        send_telegram_message("❌ Hook: Invalid JSON input")
        sys.exit(1)
    
    hook_event = stdin_data.get("hook_event_name", "")
    
    # Handle permission requests and important notifications
    if hook_event == "Notification":
        notification_msg = stdin_data.get("message", "")
        if "permission" in notification_msg.lower() or "confirm" in notification_msg.lower():
            message = "🔐 Waiting for permission"
        elif "waiting" in notification_msg.lower() or "input" in notification_msg.lower():
            message = "⏳ Waiting for input"
        else:
            # Skip other notification types
            return
        send_telegram_message(message)
        return
    
    # Get action summary for Stop/SubagentStop
    action = get_last_action_summary(stdin_data)
    
    if hook_event == "Stop":
        if action:
            message = f"{action}"
        else:
            message = "🤖 Task completed"
    
    elif hook_event == "SubagentStop":
        if action and action.startswith("🎯"):
            message = f"{action}"
        else:
            message = "🎯 Subtask completed"
    
    else:
        # Skip other events
        return
    
    # Send notification
    send_telegram_message(message)

if __name__ == "__main__":
    main()
    sys.exit(0)