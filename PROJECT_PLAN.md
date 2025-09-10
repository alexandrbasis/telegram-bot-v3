# Tres Dias Telegram Bot - Simplified Project Plan

## Overview

**Project Goal**: Create a simple, well-structured Telegram bot for managing Tres Dias event participants. This is designed for personal/family use with a focus on simplicity, readability, and maintainability.

**Target Users**: Personal use, friends, and family managing small to medium-sized Tres Dias events.

**Key Principle**: "Simple but well-structured" - avoid over-engineering while maintaining good coding practices.

## Business Requirements

### Core Features
1. **Participant Management**
   - Add new participants with basic information (name, room, role, contact details)
   - Store and retrieve participant data
   - Edit/update participant information

2. **Search & Discovery**
   - Search participants by name (partial matching)
   - Filter by room assignment
   - Filter by role (pilgrim, team member, etc.)
   - List all participants with pagination

3. **Payment Tracking**
   - Mark participants as paid/unpaid
   - Track payment amounts and dates
   - View payment status in search results
   - Generate simple payment reports

### User Experience Goals
- Simple, intuitive bot commands
- Fast response times
- Clear error messages
- Minimal typing required for common operations

## Simplified Architecture

### 3-Layer Architecture with Database Abstraction
Instead of complex domain-driven design, we'll use a simple 3-layer approach with database abstraction:

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

### Key Architectural Principles
- **Separation of Concerns**: Bot handlers don't contain business logic
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Direction**: Bot → Services → Data (no reverse dependencies)
- **Database Abstraction**: Services depend on repository interfaces, not concrete implementations
- **Migration Flexibility**: Abstract database layer enables easy migration to other databases
- **Testability**: Each layer can be tested independently
- **Readability**: Code should be self-documenting with clear names

### Database Strategy
**Primary Database**: Airtable provides an excellent starting point because:
- **Immediate UI**: Built-in web interface for manual data management
- **No Infrastructure**: No database server setup or maintenance
- **Easy Backup**: Built-in backup and collaboration features
- **Good API**: Well-documented REST API with Python client

**Future Migration Path**: The abstract repository layer enables easy migration to:
- **SQLite**: For local file-based database needs
- **PostgreSQL**: For production enterprise use
- **MongoDB**: For document-based storage needs
- **Google Sheets**: Alternative cloud-based option

**Migration Process**: To switch databases, only the repository implementation needs to change:
```python
# Current: Airtable
participant_repo = AirtableParticipantRepository(airtable_client)

# Future: PostgreSQL  
participant_repo = PostgresParticipantRepository(postgres_client)

# Services remain unchanged!
participant_service = ParticipantService(participant_repo)
```

### Technology Stack
- **Core**: Python 3.9+, python-telegram-bot
- **Database**: Airtable (primary), with abstract layer for future migrations
- **Database Client**: pyairtable for Airtable integration
- **Configuration**: python-dotenv for environment variables
- **Testing**: pytest with basic coverage, responses for API mocking
- **Code Quality**: flake8, black formatter, mypy type checking

## Project Structure

```
telegram-bot-v2/
├── src/
│   ├── bot/                    # Telegram bot interface
│   │   ├── handlers/           # Command and message handlers
│   │   │   ├── add_participant.py
│   │   │   ├── search_participants.py
│   │   │   ├── payment_tracking.py
│   │   │   └── help_commands.py
│   │   ├── keyboards.py        # Inline keyboard definitions
│   │   └── messages.py         # Message templates and formatting
│   │
│   ├── services/               # Business logic layer
│   │   ├── participant_service.py  # Participant operations
│   │   ├── search_service.py       # Search and filtering
│   │   ├── payment_service.py      # Payment tracking
│   │   └── validation_service.py   # Input validation
│   │
│   ├── data/                   # Data access layer
│   │   ├── repositories/           # Database abstraction layer
│   │   │   ├── participant_repository.py    # Abstract repository interface
│   │   │   └── payment_repository.py        # Abstract payment repository
│   │   ├── airtable/               # Airtable implementation
│   │   │   ├── airtable_participant_repo.py # Airtable participant implementation
│   │   │   ├── airtable_payment_repo.py     # Airtable payment implementation
│   │   │   └── airtable_client.py          # Airtable connection wrapper
│   │   ├── backup_manager.py       # Data backup functionality
│   │   └── data_validator.py       # Data integrity checks
│   │
│   ├── models/                 # Data models
│   │   ├── participant.py      # Participant data class
│   │   └── payment.py          # Payment data class
│   │
│   ├── config/                 # Configuration management
│   │   ├── settings.py         # App settings and constants
│   │   └── field_mappings.py   # Field validation rules
│   │
│   └── utils/                  # Shared utilities
│       ├── logger.py           # Logging configuration
│       ├── formatters.py       # Text formatting helpers
│       └── exceptions.py       # Custom exception classes
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   │   ├── test_services/
│   │   ├── test_data/
│   │   └── test_models/
│   ├── integration/            # Integration tests
│   │   └── test_bot_handlers/
│   └── fixtures/               # Test data and mocks
│
├── data/                       # Local data directory
│   ├── backups/               # Automated data backups from Airtable
│   ├── exports/               # Data export files (CSV, JSON)
│   └── cache/                 # Local cache for performance (optional)
│
├── requirements/               # Dependency management
│   ├── base.txt               # Core dependencies (python-telegram-bot, pyairtable, etc.)
│   ├── dev.txt                # Development dependencies (black, flake8, mypy)
│   └── test.txt               # Testing dependencies (pytest, responses, etc.)
│
├── scripts/                    # Utility scripts
│   ├── backup_data.py         # Manual backup script
│   └── migrate_data.py        # Data migration helpers
│
├── .env.example               # Environment variables template
├── Makefile                   # Development automation
├── pyproject.toml             # Project configuration
└── README.md                  # Setup and usage instructions
```

## Implementation Guidelines

### Code Quality Standards
- **Naming**: Use clear, descriptive names for functions, variables, and classes
- **Functions**: Keep functions small (≤30 lines), single-purpose
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Brief docstrings for public functions and classes
- **Error Handling**: Handle expected errors gracefully with user-friendly messages

### Development Best Practices

#### Database Abstraction Layer
```python
# Abstract repository interface (easy migration to other databases)
from abc import ABC, abstractmethod
from typing import List, Optional

class ParticipantRepository(ABC):
    @abstractmethod
    async def create(self, participant: Participant) -> str:
        """Create participant and return ID."""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> List[Participant]:
        """Find participants by name (partial match)."""
        pass

# Airtable implementation
class AirtableParticipantRepository(ParticipantRepository):
    def __init__(self, airtable_client: AirtableClient):
        self.client = airtable_client
    
    async def create(self, participant: Participant) -> str:
        record = await self.client.create_record(participant.to_dict())
        return record["id"]
    
    async def find_by_name(self, name: str) -> List[Participant]:
        records = await self.client.search_records("name", name)
        return [Participant.from_dict(r["fields"]) for r in records]

# Service layer uses the abstract interface
class ParticipantService:
    def __init__(self, repository: ParticipantRepository):
        self.repository = repository  # Uses abstract interface, not concrete implementation
    
    async def add_participant(self, name: str, room: str, role: str) -> dict:
        """Add a new participant and return success status."""
        participant = self._validate_and_create(name, room, role)
        participant_id = await self.repository.create(participant)
        return {"success": True, "participant_id": participant_id}
```

#### Bot Handler Example
```python
# Good example of bot handler
async def handle_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command for adding new participant."""
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /add <name> <room> <role>")
        return
    
    result = await participant_service.add_participant(args[0], args[1], args[2])
    if result["success"]:
        await update.message.reply_text(f"✅ Added participant: {args[0]}")
```

### File Organization Rules
- **One class per file** (except small related classes)
- **Group related functions** in the same module
- **Import organization**: Standard library → Third party → Local imports
- **No circular imports**: Use dependency injection if needed

## Quality Assurance Strategy

### Testing Approach (Pragmatic, not exhaustive)
- **Focus Areas**: Test critical business logic and happy paths
- **Coverage Goal**: ~70-80% (not 100% - this isn't enterprise software)
- **Test Types**:
  - Unit tests for services and data operations
  - Integration tests for complete workflows
  - Manual testing for user experience

### Testing Strategy by Layer
```python
# Service Layer Tests (Priority: High)
class TestParticipantService:
    def test_add_valid_participant(self):
        # Test with mocked repository interface
    
    def test_search_by_name(self):
        # Test name-based search functionality
    
    def test_invalid_data_handling(self):
        # Test error handling for bad input

# Repository Tests (Priority: Medium)
class TestAirtableParticipantRepository:
    def test_create_participant(self):
        # Test with mocked Airtable API calls
    
    def test_search_participants(self):
        # Test API search functionality with mock responses
    
    def test_api_error_handling(self):
        # Test handling of Airtable API errors

# Bot Handler Tests (Priority: Low - mostly integration testing)
class TestBotHandlers:
    def test_add_command_flow(self):
        # Test complete add participant workflow
```

### Code Quality Tools
```makefile
# Makefile commands for quality assurance
format:
    black src/ tests/
    isort src/ tests/

lint:
    flake8 src/ tests/
    mypy src/

test:
    pytest tests/ -v --cov=src --cov-report=term

quality-check: format lint test
```

### Quality Gates
- All tests must pass before merging
- No major linting errors
- Type checking passes (mypy)
- Manual testing of new features

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Basic working bot with participant addition

**Deliverables**:
- [ ] Project setup with proper structure  
- [ ] Airtable base setup (participants table)
- [ ] Abstract repository interfaces
- [ ] Airtable repository implementation
- [ ] Basic Participant model
- [ ] Simple `/add` command functionality
- [ ] Basic error handling and logging

**Acceptance Criteria**:
- Can start bot without errors
- Can add participants via `/add name room role`
- Data saves to Airtable correctly
- Basic input validation works
- Repository abstraction allows for easy database switching

### Phase 2: Core Features (Week 2)
**Goal**: Complete participant management with search

**Deliverables**:
- [x] Search functionality (`/search name`, `/search_room`, `/search_floor`) - ✅ Completed with comprehensive integration testing
- [ ] List all participants (`/list`)
- [ ] Edit participant information (`/edit`)
- [ ] Delete participants (`/delete`)
- [ ] Improved user interface with inline keyboards

**Acceptance Criteria**:
- All search types work correctly
- Pagination for large lists
- Edit operations update storage correctly
- User-friendly error messages

### Phase 3: Payment Tracking (Week 3)
**Goal**: Complete payment management system

**Deliverables**:
- [ ] Payment model and storage
- [ ] Mark as paid functionality (`/pay participant_name amount`)
- [ ] Payment status in search results
- [ ] Payment reports (`/payments`)
- [ ] Payment history tracking

**Acceptance Criteria**:
- Payment status accurately tracked
- Payment history preserved
- Clear payment status indicators
- Simple payment reporting

### Phase 4: Polish & Enhancement (Week 4)
**Goal**: Production-ready bot with nice-to-have features

**Deliverables**:
- [ ] Data export functionality (`/export`)
- [ ] Automated data backups
- [ ] Improved error handling and user feedback
- [ ] Help system (`/help`)
- [ ] Performance optimizations
- [x] Comprehensive testing - ✅ 90+ tests including 28 integration tests for room/floor search with performance validation

**Acceptance Criteria**:
- Export generates usable CSV/JSON files
- Regular automated backups work
- Comprehensive help documentation
- All tests pass with good coverage

## Getting Started

### Quick Setup
```bash
# 1. Clone and setup
git clone [repository]
cd telegram-bot-v2
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements/dev.txt

# 2. Configuration
cp .env.example .env
# Edit .env with your bot token

# 3. Run tests
make test

# 4. Start bot
python src/main.py
```

### Development Workflow
1. **Start**: Pick a task from current phase
2. **Test**: Write basic test for new functionality
3. **Code**: Implement feature following guidelines
4. **Verify**: Run tests and quality checks (`make quality-check`)
5. **Test**: Manual testing with actual bot
6. **Commit**: Small, focused commits with clear messages

### Success Metrics
- **User Experience**: Commands work intuitively without referring to documentation
- **Maintainability**: New developer can understand and modify code quickly
- **Reliability**: Bot handles errors gracefully and recovers well
- **Performance**: Responds quickly to user commands (< 2 seconds)

## Risk Management

### Technical Risks
- **Data Loss**: Mitigated by automated backups and simple file format
- **Bot Downtime**: Mitigated by good error handling and logging
- **Performance Issues**: Mitigated by simple architecture and file-based storage

### Project Risks  
- **Scope Creep**: Mitigated by clear phase boundaries and simple requirements
- **Over-Engineering**: Mitigated by "simple but well-structured" principle
- **Maintenance Burden**: Mitigated by clear documentation and simple architecture

## Conclusion

This project plan prioritizes **simplicity and maintainability** over enterprise-level complexity. The goal is to create a tool that:

- **Works reliably** for personal/family use cases
- **Is easy to understand** and modify by any developer (or AI)
- **Can be maintained** without significant overhead
- **Provides real value** quickly through phased implementation

The architecture is purposefully simple but follows good software engineering principles. This approach should deliver a working, maintainable solution without the complexity overhead of enterprise-level patterns.

**Remember**: The goal is "good enough" quality with clear, maintainable code - not perfect software engineering.

## Recent Implementation Updates

### Airtable Schema Update (September 2025)

**Status**: Completed - Enhanced participant data model with demographic fields

**Implementation Summary**:
- **New Fields Added**: DateOfBirth (date field) and Age (number field) with proper validation constraints
- **Real Field Integration**: Connected to live Airtable API to discover and validate actual field IDs:
  - DateOfBirth: `fld1rN2cffxKuZh4i` (DATE type, ISO format)
  - Age: `fldZPh65PIekEbgvs` (NUMBER type, 0-120 range)
- **Backward Compatibility**: All new fields are optional, ensuring existing records process correctly
- **Comprehensive Testing**: 100% test pass rate with enhanced coverage for field mappings, model validation, and schema discovery
- **Production Validation**: Schema discovery and validation scripts created for ongoing data integrity

**Key Technical Achievements**:
- **TDD Implementation**: Test-driven development approach with tests written during implementation
- **Schema Discovery Automation**: `scripts/discover_real_schema.py` for live API validation
- **Production Validation**: `scripts/validate_production_schema.py` for CI/CD integration
- **Enhanced Documentation**: Complete field specifications with usage examples and constraints