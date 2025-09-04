# Architecture Overview

## 3-Layer Architecture

Tres Dias Telegram Bot v3 follows a clean 3-layer architecture pattern:

### Bot Layer (`src/bot/`)
- **Handlers**: Telegram message/callback handlers
- **Conversations**: ConversationHandler state machines
- **Keyboards**: Inline keyboard layouts and buttons

### Service Layer (`src/services/`)
- **Business Logic**: Data validation and processing
- **Orchestration**: Coordination between data and presentation layers
- **Validation**: Field-specific validation rules

### Data Layer (`src/data/`)
- **Repositories**: Abstract data access interfaces
- **Implementations**: Airtable-specific data access
- **Models**: Pydantic data models

## Key Architectural Components

### Conversation Management

**Search Conversation Handler**:
- Multi-state conversation flow for participant search and editing
- State transitions: SEARCH → RESULTS → DETAILS → EDITING → CONFIRMATION
- Context preservation across state changes
- Integration between search and editing workflows
- **State Collision Prevention**: SearchStates uses values 10-12 to avoid conflicts with EditStates 0-2
- **Mixed Handler Support**: ConversationHandler configured with per_message=None for proper CallbackQueryHandler tracking

**Participant Editing Handler** (New - 2025-08-29):
- 4-state ConversationHandler for comprehensive field editing
- States: FIELD_SELECTION → TEXT_INPUT/BUTTON_SELECTION → CONFIRMATION
- Russian localization across all states
- Field-specific validation and error handling

### Data Access Patterns

**Repository Pattern**:
- `ParticipantRepository` abstract interface
- `AirtableParticipantRepo` concrete implementation
- Support for search, retrieval, and **selective field updates**

**New Capabilities**:
- `update_by_id()` method for partial field updates (2025-08-29)
- **Room/Floor search methods** (2025-09-04):
  - `find_by_room_number(room: str)` - Filter participants by room assignment
  - `find_by_floor(floor: Union[int, str])` - Filter participants by floor
- Field mapping between internal models and Airtable schema
- Rate limiting and error recovery for update operations
- **Security enhancements** with formula injection prevention

### Service Layer Architecture

**Participant Update Service** (2025-08-29):
- Centralized validation logic for all field types
- Russian error message generation
- Enum value conversion (Gender, Size, Role, Department, Payment Status)
- Special validation for numeric and date fields

**Search Service Extensions** (2025-09-04):
- **Room-based search**: `search_by_room(room: str)` with input validation
- **Floor-based search**: `search_by_floor(floor: Union[int, str])` with type conversion
- **Formatted results**: `search_by_room_formatted(room: str)` for UI consumption
- **Validation utilities**: Comprehensive input validation with `ValidationResult` objects

**Validation Strategies**:
- **Required Fields**: Russian name (min length 1)
- **Optional Text Fields**: Church, location, contact information
- **Enum Fields**: Button-based selection with predefined options
- **Special Fields**: Payment amount (integer ≥ 0), payment date (YYYY-MM-DD)
- **Room/Floor Fields**: Alphanumeric room numbers, Union[int, str] floor support

### User Interface Architecture

**Keyboard Factory Pattern**:
- Field-specific keyboard generators
- Russian label mapping
- Consistent layout patterns (2-3 columns, cancel buttons)
- Dynamic option loading from enum definitions

**Localization Strategy**:
- Russian field names and labels
- Localized validation error messages
- Russian navigation buttons and prompts
- Enum value translation (M/F → Мужской/Женский)

## Component Integration

### Search → Edit → Save Workflow
1. User searches via `/search` command
2. Results display with "Подробнее" (Details) buttons  
3. Button click transitions to participant editing interface
4. Editing interface shows complete profile with 13 edit buttons
5. Field editing uses appropriate input method (buttons vs text)
6. **Save confirmation screen** displays all pending changes in "Current → **New**" format
7. User confirms save operation or cancels to discard changes
8. Changes committed via repository `update_by_id()` method with retry mechanism
9. User returns to search results with context preserved

### State Management
- **Context Preservation**: User data maintained across state transitions
- **Error Recovery**: Validation failures return to appropriate input state with retry options
- **Change Tracking**: All field modifications tracked until explicit save confirmation
- **Cancellation Handling**: Clean state cleanup on cancel operations with change discard
- **Save Confirmation**: Explicit user confirmation required before Airtable updates
- **Retry Mechanism**: Failed save operations preserve changes and offer retry with error details
- **Back Navigation**: Seamless return to previous conversation states
- **State Collision Management**: Non-overlapping state enum values prevent handler conflicts (SearchStates: 10-12, EditStates: 0-2)
- **ConversationHandler Configuration**: Proper per_message parameter configuration ensures mixed handler types (MessageHandler + CallbackQueryHandler) work correctly

### Data Flow
```
User Input → Handler → Service (validation) → Repository → Airtable API
     ↓                                                        ↓
UI Response ← Keyboard ← Error/Success ← Update Result ← API Response
```

## Scalability Considerations

### Performance
- Rate limiting built into Airtable client (5 requests/second)
- Selective field updates reduce API call overhead
- In-memory state management for conversation context

### Maintainability  
- Separation of concerns across 3 layers
- Repository pattern allows easy database backend switching
- Service layer centralizes business logic and validation
- Keyboard factory pattern simplifies UI management

### Testability
- 75+ unit tests including editing and room/floor search functionality (100% pass rate)
- Mock repositories for isolated testing
- Service layer testing with comprehensive validation scenarios
- Handler testing with conversation state simulation
- **Room/Floor search testing**: 34 comprehensive tests covering repository, service, validation, and security layers

## Error Handling Strategy

### Validation Errors
- Field-specific Russian error messages
- Clear retry instructions
- Graceful conversation state recovery

### System Errors
- Airtable API error handling with user-friendly messages
- Rate limit protection with automatic retry
- Connection timeout recovery
- Logging for debugging and monitoring

## Future Architecture Enhancements

### Potential Improvements
- Event-driven architecture for field change notifications
- Caching layer for frequently accessed participant data
- Batch update operations for bulk editing
- Plugin architecture for custom validation rules
- Audit trail system for change tracking