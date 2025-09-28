# Changelog - 2025-09-28

All notable changes made on 2025-09-28 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changes Made

### Added
- **Help Command System with Comprehensive Bot Guidance** - New `/help` command providing complete Russian-language bot documentation and command discovery
  - **Global Help Command Handler** - Implemented standalone `/help` command accessible from any bot state (`src/bot/handlers/help_handlers.py`)
    - Independent command registration following pattern established by `/logging` command
    - State-agnostic functionality ensuring help access regardless of current conversation flow
    - Comprehensive Russian guidance covering all 8 bot commands organized in 5 functional categories
  - **Dynamic Help Content Generation** - Smart help message generation adapting to bot configuration (`src/bot/messages.py:225-289`)
    - Feature flag-aware content that includes/excludes schedule commands based on `enable_schedule_feature` setting
    - Structured organization: Core Commands, Search, Export, Schedule (conditional), and Admin categories
    - Consistent Russian terminology and emoji usage following existing bot conventions
  - **Enhanced User Onboarding** - Updated welcome message to include help command reference (`src/bot/handlers/search_handlers.py:77`)
    - Seamless integration with existing welcome flow without disrupting current functionality
    - Clear guidance for new users to discover bot capabilities through `/help` command
    - Maintained existing welcome message structure and formatting conventions
  - **Global Command Registration** - Help command registered in main application for universal accessibility (`src/main.py:159`)
    - Direct registration via `CommandHandler("help", handle_help_command)` in bot application setup
    - No conversation handler dependencies ensuring consistent behavior across all bot states
    - Priority handling to ensure help availability even during active conversations
  - **Comprehensive Test Coverage** - Complete test suite covering all help functionality aspects
    - Unit tests for help message generation and content validation (`tests/unit/test_bot_handlers/test_help_handlers.py`)
    - Integration tests for command registration and global accessibility (`tests/integration/test_bot_handlers/test_help_integration.py`)
    - Feature flag testing ensuring dynamic content adapts correctly to configuration changes
    - Russian language consistency validation and message formatting verification

### Changed
- **Schedule Formatting Enhancement with Russian Localization** - Comprehensive improvements to schedule display formatting and user experience
  - **Russian Audience Translation Support** - Added localized audience type mapping for Russian users (`src/utils/schedule_formatter.py`)
    - `AUDIENCE_ALIASES` dictionary mapping English audience types to Russian equivalents
    - Support for "Men" → "Мужчины", "Women" → "Женщины", "Team Members" → "Тим Мемберы"
    - Graceful fallback to original values for unmapped audience types
  - **Smart Section Header Detection** - Implemented intelligent section parsing from event descriptions (`src/utils/schedule_formatter.py`)
    - `SECTION_MARKERS` tuple for detecting section headers (Session, Time, Break, etc.)
    - `_extract_section_and_details()` function for separating section names from event details
    - Location emoji detection for visual section identification
  - **Hierarchical Bullet Point Formatting** - Enhanced visual hierarchy for improved readability (`src/utils/schedule_formatter.py`)
    - Primary events use bullet symbol (•) for main schedule items
    - Sub-items and details use hollow bullet (◦) for secondary information
    - Improved visual distinction between event types and nested content
  - **Enhanced Documentation** - Updated technical documentation with schedule command improvements (`docs/technical/bot-commands.md`)
    - Documented new formatting features and Russian localization support
    - Added examples of hierarchical formatting and section detection
  - **Comprehensive Test Coverage** - Added extensive test suite for all formatting enhancements (`tests/unit/test_utils/test_schedule_formatter.py`)
    - Unit tests for Russian audience translation with all supported mappings
    - Section header detection tests covering various input formats
    - Hierarchical formatting validation with bullet point verification
    - Edge case handling for unknown audience types and malformed inputs

### Fixed

### Removed