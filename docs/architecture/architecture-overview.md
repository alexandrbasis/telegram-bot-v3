# Architecture Overview

## Project Structure

The Telegram bot follows a clean 3-layer architecture with database abstraction, implemented in Phase 1:

```
┌─────────────────┐
│   Bot Layer     │  ← Telegram handlers, user interface
├─────────────────┤
│  Service Layer  │  ← Business logic, data processing  
├─────────────────┤
│   Data Layer    │  ← Database abstraction
│  ┌─────────────┐│
│  │ Repository  ││  ← Abstract database interface
│  │ Interface   ││
│  ├─────────────┤│
│  │  Airtable   ││  ← Primary database implementation
│  │Implementation││
│  └─────────────┘│
└─────────────────┘
```

## Implemented Directory Structure

```
src/
├── bot/                    # Telegram bot interface layer
│   ├── handlers/           # Command and message handlers
│   ├── __init__.py         # Bot package initialization
├── services/               # Business logic layer
│   ├── __init__.py         # Services package initialization
├── data/                   # Data access layer
│   ├── repositories/       # Abstract database interfaces
│   │   ├── __init__.py     # Repository package initialization
│   ├── airtable/          # Airtable implementation
│   │   ├── __init__.py     # Airtable package initialization
│   ├── __init__.py         # Data package initialization
├── models/                 # Data models and entities
│   ├── __init__.py         # Models package initialization
├── config/                 # Configuration management
│   ├── __init__.py         # Config package initialization
└── utils/                  # Shared utilities
    ├── __init__.py         # Utils package initialization

tests/                      # Comprehensive test suite
├── unit/                   # Unit tests by layer
│   ├── test_services/      # Service layer tests
│   ├── test_data/          # Data layer tests
│   ├── test_models/        # Model tests
│   ├── __init__.py         # Unit tests package
├── integration/            # Integration tests
│   ├── test_bot_handlers/  # Bot integration tests
│   ├── __init__.py         # Integration tests package
├── fixtures/               # Test data and mocks
│   ├── __init__.py         # Fixtures package
├── __init__.py             # Tests package initialization
└── test_project_structure.py  # Structure validation tests

Supporting Infrastructure:
├── requirements/           # Dependency management
│   ├── base.txt           # Core runtime dependencies  
│   ├── dev.txt            # Development dependencies
│   └── test.txt           # Testing dependencies
├── scripts/               # Utility and automation scripts
├── data/                  # Local data storage
│   ├── backups/          # Data backups
│   ├── exports/          # Export files
│   └── cache/            # Performance cache
```

## Key Architectural Principles

### 1. Separation of Concerns
- **Bot Layer**: Handles Telegram API interactions only
- **Service Layer**: Contains all business logic
- **Data Layer**: Manages data persistence and retrieval

### 2. Dependency Direction
- Bot → Services → Data (no reverse dependencies)
- Services depend on repository abstractions, not implementations

### 3. Database Abstraction
- Abstract repository interfaces enable easy migration between databases
- Current implementation uses Airtable
- Future migrations to PostgreSQL, SQLite, or MongoDB require only repository layer changes

### 4. Python Package Structure
- All directories properly initialized with `__init__.py` files
- Enables clean imports: `from src.services import ParticipantService`
- Package hierarchy supports modular development and testing

## Implementation Status

**Phase 1 Foundation: COMPLETED**
- Complete directory structure per PROJECT_PLAN.md specification
- 18 Python packages with proper `__init__.py` initialization  
- Project configuration with `pyproject.toml`
- Requirements management system
- Testing framework with pytest integration
- Development environment fully configured
- Structure validation tests passing

**Next Phase**: Core feature implementation will build upon this foundation.