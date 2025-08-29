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

**New Capabilities (2025-08-29)**:
- `update_by_id()` method for partial field updates
- Field mapping between internal models and Airtable schema
- Rate limiting and error recovery for update operations

### Service Layer Architecture

**Participant Update Service** (New - 2025-08-29):
- Centralized validation logic for all field types
- Russian error message generation
- Enum value conversion (Gender, Size, Role, Department, Payment Status)
- Special validation for numeric and date fields

**Validation Strategies**:
- **Required Fields**: Russian name (min length 1)
- **Optional Text Fields**: Church, location, contact information
- **Enum Fields**: Button-based selection with predefined options
- **Special Fields**: Payment amount (integer ≥ 0), payment date (YYYY-MM-DD)

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

### Search → Edit Workflow
1. User searches via `/search` command
2. Results display with "Подробнее" (Details) buttons  
3. Button click transitions to participant editing interface
4. Editing interface shows complete profile with 13 edit buttons
5. Field editing uses appropriate input method (buttons vs text)
6. Changes saved via repository `update_by_id()` method
7. User returns to search results with context preserved

### State Management
- **Context Preservation**: User data maintained across state transitions
- **Error Recovery**: Validation failures return to appropriate input state
- **Cancellation Handling**: Clean state cleanup on cancel operations
- **Back Navigation**: Seamless return to previous conversation states

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
- 56 unit tests for editing functionality (100% pass rate)
- Mock repositories for isolated testing
- Service layer testing with comprehensive validation scenarios
- Handler testing with conversation state simulation

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