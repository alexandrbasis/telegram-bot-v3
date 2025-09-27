# Changelog - 2025-09-27

All notable changes made on 2025-09-27 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Changes Made

### Added
- **View-Aligned Exports System** - Comprehensive implementation of Airtable view-aligned exports across all three export types
  - **Repository Layer Standardization** - Added `list_view_records()` method to all repository interfaces (`src/data/repositories/roe_repository.py:151-165`, `src/data/repositories/bible_readers_repository.py:137-151`)
  - **Concrete View Support** - Implemented view-based record retrieval in Airtable repositories (`src/data/airtable/airtable_roe_repo.py:349-371`, `src/data/airtable/airtable_bible_readers_repo.py:317-339`)
  - **Configuration Management** - Added configurable view names via environment variables with validation (`src/config/settings.py:134-143,187-195`)
    - `AIRTABLE_PARTICIPANT_EXPORT_VIEW` (default: "Кандидаты")
    - `AIRTABLE_ROE_EXPORT_VIEW` (default: "РОЕ: Расписание")
    - `AIRTABLE_BIBLE_READERS_EXPORT_VIEW` (default: "Чтецы: Расписание")
  - **Export Utilities Enhancement** - Added view-based column ordering functions (`src/utils/export_utils.py:217-281`)
    - `extract_headers_from_view_records()` for preserving Airtable view column order
    - `order_rows_by_view_headers()` for reordering data while maintaining line numbers
  - **Service Layer Integration** - Updated all export services to use view-based data retrieval
    - Participant exports use configured view with preserved column ordering (`src/services/participant_export_service.py`)
    - ROE exports with participant name hydration (`src/services/roe_export_service.py`)
    - Bible Readers exports with participant hydration (`src/services/bible_readers_export_service.py`)
  - **Graceful Fallback Behavior** - Services automatically fall back to legacy export when views unavailable
  - **Comprehensive Test Coverage** - 1524 tests passing with 100% coverage across 8 implementation steps
    - TDD approach with Red-Green-Refactor cycles for all components
    - Unit tests for repository interfaces, concrete implementations, utilities, and services
    - Integration tests validating end-to-end export workflows

### Changed
- **Changelog System Restructure** - Migrated from monolithic changelog to date-based changelog system
  - Created `docs/changelogs/` directory structure for organized change tracking
  - Implemented date-based subdirectories (YYYY-MM-DD format) for daily changelog entries
  - Moved existing changelog to `docs/changelogs/CHANGELOG_LEGACY.md` for historical reference
  - Updated changelog generator agent to support date-based entry creation and management
- **Changelog Generation System Testing** - Validated new date-based changelog workflow and functionality
  - Tested date detection and automatic directory creation for daily changelog entries
  - Verified file management for existing vs new changelog files on the same date
  - Confirmed agent configuration supports new workflow in `.claude/agents/changelog-generator.md`
  - Validated proper entry formatting and categorization in date-specific files (`docs/changelogs/2025-09-27/changelog.md`)

### Fixed

### Removed