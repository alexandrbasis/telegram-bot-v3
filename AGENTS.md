# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tres Dias Telegram Bot v3 is a Python-based Telegram bot for managing event participants with Airtable integration. It features participant search functionality with Russian/English name support and fuzzy matching.

## Key Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements/dev.txt    # Development dependencies
pip install -r requirements/base.txt   # Production dependencies
```

### Testing
```bash
# Run all tests
./venv/bin/pytest tests/ -v

# Run tests with coverage
./venv/bin/pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test types
./venv/bin/pytest tests/unit/ -v      # Unit tests only
./venv/bin/pytest tests/integration/ -v  # Integration tests only

# Run single test file
./venv/bin/pytest tests/unit/test_data/test_airtable/test_airtable_client.py -v
```

### Code Quality
```bash
# Type checking
./venv/bin/mypy src --no-error-summary

# Linting
./venv/bin/flake8 src tests

# Code formatting
./venv/bin/black src tests
./venv/bin/isort src tests

# Check specific file for line length issues
./venv/bin/flake8 path/to/file.py --select=E501
```

### Running the Bot
```bash
# Using the startup script (recommended)
./start_bot.sh

# Direct Python execution
python -m src.main
```

# Project Structure Guide

This section explains the folder structure of the project. Use this as a reference for navigating and understanding the codebase.

## Root Directory

The root contains configuration files and main project folders:
- [pyproject.toml](mdc:pyproject.toml): Python project configuration with build settings and dependencies
- [.env.example](mdc:.env.example): Environment variables template
- [start_bot.sh](mdc:start_bot.sh): Bot startup script with environment setup
- [project_index.json](mdc:project_index.json): Auto-generated project metadata and structure index
- [CHANGELOG.md](mdc:CHANGELOG.md): Version history and release notes
- [PROJECT_PLAN.md](mdc:PROJECT_PLAN.md): Comprehensive project planning documentation

## Key Directories

### [src/](mdc:src)

Main application source code organized by functional layers:

- [src/bot/](mdc:src/bot): Telegram bot interface layer
  - `handlers/`: Conversation handlers and command processors
  - `keyboards/`: Telegram inline and reply keyboard definitions
- [src/services/](mdc:src/services): Business logic and application services
- [src/data/](mdc:src/data): Data access layer with repository pattern
  - `airtable/`: Airtable-specific client and repository implementations
  - `repositories/`: Abstract repository interfaces
- [src/models/](mdc:src/models): Data models and Pydantic schemas
- [src/config/](mdc:src/config): Configuration management and settings
- [src/utils/](mdc:src/utils): Shared utilities and helper functions

### [tests/](mdc:tests)

Comprehensive test suite mirroring the `src/` structure:

- [tests/unit/](mdc:tests/unit): Unit tests for individual components
  - `test_bot_handlers/`: Bot handler unit tests
  - `test_bot_keyboards/`: Keyboard component tests
  - `test_config/`: Configuration validation tests
  - `test_data/`: Data layer and repository tests
    - `test_airtable/`: Airtable client and integration tests
    - `test_repositories/`: Repository pattern tests
  - `test_models/`: Model validation and schema tests
  - `test_services/`: Service layer business logic tests
- [tests/integration/](mdc:tests/integration): End-to-end integration tests
  - `test_bot_handlers/`: Full conversation flow tests
- [tests/fixtures/](mdc:tests/fixtures): Shared test data and mock objects

### [requirements/](mdc:requirements)

Dependency management with environment-specific requirements:
- `base.txt`: Core production dependencies
- `dev.txt`: Development tools and testing dependencies  
- `test.txt`: Testing-specific dependencies

### [docs/](mdc:docs)

Comprehensive project documentation:

- [docs/architecture/](mdc:docs/architecture): System architecture and design decisions
- [docs/business/](mdc:docs/business): Business requirements and user stories
- [docs/data-integration/](mdc:docs/data-integration): Airtable integration and data flow documentation
- [docs/development/](mdc:docs/development): Development guides and workflows
- [docs/technical/](mdc:docs/technical): Technical specifications and API documentation

### [tasks/](mdc:tasks)

Task and project management files for development tracking.

### [logs/](mdc:logs)

Application log files and logging output directory.

### [venv/](mdc:venv)

Python virtual environment (excluded from version control).

## Architecture Overview

### 3-Layer Architecture
- **Bot Layer** (`src/bot/`): Telegram handlers and conversation flow
- **Service Layer** (`src/services/`): Business logic and data processing  
- **Data Layer** (`src/data/`): Database abstraction with repository pattern

### Key Components

#### Configuration (`src/config/`)
- `settings.py`: Centralized configuration using environment variables and dataclasses
- `field_mappings.py`: Airtable field ID mappings and translations

#### Data Access (`src/data/`)
- `airtable/airtable_client.py`: Low-level Airtable API client with rate limiting
- `airtable/airtable_participant_repo.py`: Participant-specific repository with fuzzy search
- `repositories/participant_repository.py`: Abstract repository interface

#### Bot Handlers (`src/bot/handlers/`)
- `search_conversation.py`: Main conversation handler setup
- `search_handlers.py`: Search functionality with Russian/English support

#### Models (`src/models/`)
- `participant.py`: Participant data model with Pydantic validation

### Search Functionality
The bot supports enhanced Russian name search with:
- Language detection (Cyrillic vs Latin scripts)
- Multi-field fuzzy matching (Russian names, English names, nicknames)
- Similarity scoring and ranking
- Rich formatted results

### Configuration Management
Settings are loaded via dataclasses from environment variables with defaults. Key config sections:
- `DatabaseSettings`: Airtable API configuration
- `TelegramSettings`: Bot token and behavior settings
- `LoggingSettings`: Log levels and formatting
- `ApplicationSettings`: Environment and feature flags

### Testing Structure
- Unit tests in `tests/unit/` mirror the `src/` structure
- Integration tests in `tests/integration/` test end-to-end flows
- Fixtures in `tests/fixtures/` for shared test data
- Coverage configuration excludes test files and virtual environments

### Environment Variables
Required:
- `TELEGRAM_BOT_TOKEN`: Bot API token from @BotFather
- `AIRTABLE_API_KEY`: Airtable personal access token
- `AIRTABLE_BASE_ID`: Base identifier (defaults to `appRp7Vby2JMzN0mC`)

Optional:
- `AIRTABLE_TABLE_NAME`: Table name (defaults to `Participants`)
- `AIRTABLE_TABLE_ID`: Table identifier (defaults to `tbl8ivwOdAUvMi3Jy`)
- `LOG_LEVEL`: Logging level (defaults to `INFO`)
- `ENVIRONMENT`: Runtime environment (defaults to `development`)

### Development Workflow
1. All settings validation happens at startup via dataclass `__post_init__`
2. Repository pattern allows easy database backend switching
3. Rate limiting is built into the Airtable client (5 requests/second default)
4. Error handling follows consistent patterns with custom exception hierarchy
5. Logging is configured per module with appropriate levels

### Recent Features

#### Enhanced Search Results with Participant Editing
The bot now features:
- Interactive search results with match quality indicators
- Inline participant editing capabilities with real-time field updates
- Save/cancel workflow with confirmation prompts and retry mechanisms
- Comprehensive error handling and user feedback
- Rich formatting for improved user experience

Key components:
- `src/services/participant_update_service.py`: Handles participant updates with validation
- Enhanced search handlers with editing interface integration
- Complete save/cancel workflow with change tracking and confirmation screens

#### Save/Cancel Workflow with Airtable Integration
Advanced editing workflow features:
- Change confirmation screens showing "Current Value → **New Value**" format
- Explicit save confirmation before committing changes to Airtable
- Cancel workflow that discards changes and returns to main menu
- Retry mechanism for failed save operations with user-friendly error messages
- Complete state management preventing data loss during error recovery
- Integration with existing conversation flows and main menu navigation

## Git & Version Control

- Add and commit automatically whenever an entire task is finished
- Use descriptive commit messages that capture the full scope of changes

## EXTREMELY IMPORTANT: Code Quality Checks

**ALWAYS run the following commands before completing any task:**

Automatically use the IDE's built-in diagnostics tool to check for linting and type errors:
   - Run `mcp__ide__getDiagnostics` to check all files for diagnostics
   - Fix any linting or type errors before considering the task complete
   - Do this for any file you create or modify

This is a CRITICAL step that must NEVER be skipped when working on any code-related task.
