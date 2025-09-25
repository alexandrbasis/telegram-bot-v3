# Selective MCP Configuration Guide

> How to use MCP servers for specific chats instead of globally activating them

## Overview

By default, MCP servers you add to Claude Code are available across all your conversations. However, there are several strategies to use MCP configurations selectively - either for specific projects, specific chats, or on-demand when needed.

## Strategy 1: Project-Scoped MCP Servers

The most straightforward approach is to use **project scope** to limit MCP servers to specific project directories.

### Setup Process

1. **Navigate to your project directory** where you want the MCP server available:
   ```bash
   cd /path/to/your/project
   ```

2. **Add MCP server with project scope**:
   ```bash
   # For stdio servers
   claude mcp add myserver --scope project -- npx -y some-mcp-server

   # For HTTP servers
   claude mcp add api-server --scope project --transport http https://api.example.com/mcp

   # For SSE servers
   claude mcp add realtime-server --scope project --transport sse https://api.example.com/sse
   ```

3. **Result**: The server is only available when working in this project directory and gets stored in `.mcp.json` for team sharing.

### Project Configuration File

When you use `--scope project`, Claude Code creates/updates `.mcp.json`:

```json
{
  "mcpServers": {
    "airtable": {
      "command": "npx",
      "args": ["-y", "airtable-mcp-server"],
      "env": {
        "AIRTABLE_API_KEY": "${AIRTABLE_API_KEY}"
      }
    },
    "github-api": {
      "type": "http",
      "url": "https://api.github.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Strategy 2: Manual MCP Server Activation

Instead of having servers always running, you can add them as needed and remove them when done.

### Temporary Server Usage

```bash
# Add server for current task
claude mcp add temp-server --scope local -- npx -y specific-tool-server

# Work with the server in your conversation
# ... use the MCP server tools ...

# Remove when done
claude mcp remove temp-server
```

### Quick Server Switching

```bash
# List available servers
claude mcp list

# Add/remove servers as needed for different tasks
claude mcp add database --scope local -- npx -y postgres-mcp-server
# ... work with database ...
claude mcp remove database

claude mcp add design-tool --scope local --transport http https://figma-api/mcp
# ... work with designs ...
claude mcp remove design-tool
```

## Strategy 3: Multiple Project Configurations

Maintain different MCP configurations for different types of work by using separate project directories.

### Directory Structure

```
~/projects/
├── web-development/          # Web-focused MCP servers
│   └── .mcp.json            # → GitHub, Vercel, Stripe
├── data-analysis/           # Data-focused MCP servers
│   └── .mcp.json            # → PostgreSQL, Airtable, analytics
├── design-work/             # Design-focused MCP servers
│   └── .mcp.json            # → Figma, Canva, image tools
└── automation/              # Automation-focused MCP servers
    └── .mcp.json            # → Zapier, workflow tools
```

### Example Configurations

**Web Development** (`.mcp.json`):
```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.github.com/mcp"
    },
    "vercel": {
      "type": "http",
      "url": "https://mcp.vercel.com/"
    },
    "stripe": {
      "type": "http",
      "url": "https://mcp.stripe.com"
    }
  }
}
```

**Data Analysis** (`.mcp.json`):
```json
{
  "mcpServers": {
    "airtable": {
      "command": "npx",
      "args": ["-y", "airtable-mcp-server"],
      "env": {
        "AIRTABLE_API_KEY": "${AIRTABLE_API_KEY}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub"],
      "env": {
        "DATABASE_URL": "${POSTGRES_CONNECTION}"
      }
    }
  }
}
```

## Strategy 4: Environment-Based Configuration

Use environment variables to conditionally enable MCP servers.

### Conditional Server Loading

```json
{
  "mcpServers": {
    "production-db": {
      "command": "npx",
      "args": ["-y", "postgres-mcp"],
      "env": {
        "DATABASE_URL": "${PROD_DATABASE_URL:-}"
      }
    },
    "development-tools": {
      "command": "npx",
      "args": ["-y", "dev-tools-server"],
      "env": {
        "DEV_MODE": "${DEV_MODE:-false}"
      }
    }
  }
}
```

### Usage

```bash
# Work with production data
PROD_DATABASE_URL="postgresql://..." claude

# Development mode
DEV_MODE="true" claude

# Regular mode (no special servers)
claude
```

## Strategy 5: Settings-Based Server Control

Use Claude Code settings to control which project MCP servers are enabled.

### Settings Configuration

In `.claude/settings.json` or `.claude/settings.local.json`:

```json
{
  "enableAllProjectMcpServers": false,
  "enabledMcpjsonServers": ["github", "airtable"],
  "disabledMcpjsonServers": ["expensive-api", "prod-database"]
}
```

This gives you fine-grained control over which servers from `.mcp.json` files actually get loaded.

## Strategy 6: Chat-Specific Workflow

Create a workflow for activating servers at the start of specific conversations.

### Workflow Example

1. **Start Claude Code in project directory**:
   ```bash
   cd /path/to/project
   claude
   ```

2. **Check available servers**:
   ```
   /mcp
   ```

3. **Activate specific servers for this conversation**:
   ```bash
   # In terminal (separate session)
   claude mcp add task-specific-server --scope local -- npx -y tool-server
   ```

4. **Return to conversation and use the server**

5. **Clean up when done**:
   ```bash
   claude mcp remove task-specific-server
   ```

## Advanced Configuration Examples

### Example 1: Airtable for Specific Project

```bash
# Only available in current project
cd ~/my-crm-project
claude mcp add airtable --scope project --env AIRTABLE_API_KEY=your_key \
  -- npx -y airtable-mcp-server

# Creates .mcp.json in project directory
# Team members get same configuration
```

### Example 2: GitHub API for Code Reviews

```bash
# Temporary server for code review session
claude mcp add github-review --scope local --transport http \
  https://api.github.com/mcp

# Work on reviews...
# Remove when done
claude mcp remove github-review
```

### Example 3: Multiple Environment Setup

```bash
# Development environment
cd ~/projects/dev-workspace
claude mcp add dev-db --scope project -- npx -y postgres-mcp-server

# Staging environment
cd ~/projects/staging-workspace
claude mcp add staging-db --scope project -- npx -y postgres-mcp-server

# Production access (restricted)
cd ~/projects/prod-workspace
claude mcp add prod-db --scope project --env READ_ONLY=true \
  -- npx -y postgres-mcp-server
```

## Best Practices

### 1. **Use Project Scope for Team Collaboration**
- Store configurations in `.mcp.json` for shared team access
- Use environment variables for sensitive credentials
- Document required environment variables in README

### 2. **Use Local Scope for Personal/Temporary Tools**
- Quick experiments and one-off tasks
- Personal productivity tools
- Temporary debugging servers

### 3. **Clean Up Unused Servers**
```bash
# Regular cleanup
claude mcp list
claude mcp remove unused-server1 unused-server2
```

### 4. **Security Considerations**
- Keep sensitive credentials in environment variables
- Use project scope for shared, local scope for personal
- Regularly audit your MCP server list

### 5. **Performance Optimization**
- Only activate servers you need for current work
- Remove expensive/slow servers when not needed
- Monitor server startup times with `MCP_TIMEOUT` environment variable

## Common Use Cases

### Research Sessions
```bash
# Start research session
claude mcp add web-search --scope local --transport http https://search-api.com/mcp
claude mcp add knowledge-base --scope local -- npx -y kb-server

# End session cleanup
claude mcp remove web-search knowledge-base
```

### Development Sessions
```bash
# Start development work
claude mcp add github --scope project --transport http https://api.github.com/mcp
claude mcp add database --scope project -- npx -y postgres-mcp-server

# Development work...
# Servers remain available for team
```

### Data Analysis Projects
```bash
# Project-specific data access
cd ~/analysis-project
claude mcp add analytics-db --scope project -- npx -y analytics-server
claude mcp add visualization --scope project -- npx -y chart-server
```

This approach gives you complete control over when and where MCP servers are available, avoiding global activation while maintaining flexibility for different types of work.