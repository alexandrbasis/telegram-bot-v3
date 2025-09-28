# Changelog - 2025-09-28

All notable changes made on 2025-09-28 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changes Made

### Added

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