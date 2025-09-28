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
- **Security Audit Service**: Comprehensive security event logging and performance metrics
- **Authorization Performance**: Sub-100ms authorization with advanced caching

### Data Layer (`src/data/`)
- **Repositories**: Abstract data access interfaces with role-based filtering
- **Implementations**: Airtable-specific data access with security compliance
- **Models**: Pydantic data models

## Authorization Architecture (Added 2025-09-24)

### Role-Based Access Control System

The bot implements a comprehensive three-tier role-based access control (RBAC) system:

**Role Hierarchy**: Admin > Coordinator > Viewer
- **Admin**: Full access to all functionality including exports and sensitive data
- **Coordinator**: Access to participant data with some restrictions (no PII)
- **Viewer**: Limited access with strict data filtering and no sensitive information

### Core Authorization Components

#### Configuration Layer (`src/config/settings.py`)
- **Role Parsing**: Environment variable parsing for TELEGRAM_VIEWER_IDS, TELEGRAM_COORDINATOR_IDS
- **Type Safety**: Robust handling of Union[int, str, None] user ID types
- **Validation**: Comprehensive validation with clear error messages for invalid configurations
- **Backward Compatibility**: Maintains existing TELEGRAM_ADMIN_IDS functionality

#### Authorization Utilities (`src/utils/auth_utils.py`)
- **Role Resolution**: `get_user_role()` function determines highest role for a user
- **Hierarchy Functions**: `is_admin_user()`, `is_coordinator_user()`, `is_viewer_user()` with proper inheritance
- **Performance Caching**: 5-minute TTL cache with manual invalidation support for <50ms response times
- **Advanced Caching System**: High-performance `AuthorizationCache` with LRU eviction and thread safety
- **Security Audit Integration**: Complete audit trail for all authorization events
- **Privacy-Compliant Logging**: Hashed user IDs in logs to protect user privacy
- **Secure Defaults**: Unknown roles default to viewer-level access

#### Access Control Middleware (`src/utils/access_control.py`)
- **Flexible Decorators**: `@require_role()` accepts single role or role list
- **Convenience Decorators**: `@require_admin()`, `@require_coordinator_or_above()`, `@require_viewer_or_above()`
- **Error Handling**: Proper unauthorized access messages and user feedback
- **Update Integration**: `get_user_role_from_update()` utility for role extraction

#### Data Filtering (`src/utils/participant_filter.py`)
- **Role-Based Filtering**: `filter_participants_by_role()` applies appropriate data restrictions
- **PII Protection**: Viewers cannot access sensitive fields (phone, email, payment info)
- **Security Compliance**: Prevents data leakage through comprehensive field filtering
- **Coordinator Restrictions**: Coordinators have access to most data except financial information

#### Security Audit Service (`src/services/security_audit_service.py`)
- **Comprehensive Logging**: Structured security event logging with AuthorizationEvent, SyncEvent, and PerformanceMetrics
- **Performance Monitoring**: Automatic threshold-based logging (debug/info/warning/error) with <100ms fast threshold
- **Cache State Tracking**: Detailed cache hit/miss monitoring for performance optimization
- **Security Event Correlation**: Complete audit trail linking authorization attempts to user roles and actions
- **Configurable Thresholds**: Customizable performance and security alert thresholds

### Handler-Level Enforcement

#### Comprehensive Handler Security Implementation (Updated 2025-09-25)
All bot handlers now implement mandatory authorization checks using decorator-based security:

**Security Decorators Applied**:
- `@require_viewer_or_above()`: Applied to all search, list, and view operations (22+ handlers)
- `@require_coordinator_or_above()`: Applied to all participant editing operations (10 handlers)
- `@require_admin()`: Applied to administrative functions including /auth_refresh command

**Handler Categories Secured**:
1. **Search Handlers** (`src/bot/handlers/search_handlers.py`): /start command, search buttons, main menu entry points
2. **Room Search Handlers** (`src/bot/handlers/room_search_handlers.py`): All 3 room search entry points
3. **Floor Search Handlers** (`src/bot/handlers/floor_search_handlers.py`): Core 2 floor search handlers
4. **List Handlers** (`src/bot/handlers/list_handlers.py`): All 4 list generation handlers
5. **Edit Participant Handlers** (`src/bot/handlers/edit_participant_handlers.py`): All 10 editing handlers (coordinator+ required)
6. **Admin Handlers** (`src/bot/handlers/admin_handlers.py`): /auth_refresh cache invalidation command

#### Search Handler Authorization (`src/bot/handlers/search_handlers.py`)
- **Role Resolution**: Handlers determine user role at conversation start
- **Repository Integration**: User role passed to repository methods for filtering
- **Fallback Security**: All search paths include role-based filtering to prevent bypass
- **Entry Point Security**: All conversation entry points protected with @require_viewer_or_above decorators
- **Admin Cache Refresh**: /auth_refresh command allows real-time role updates without bot restart

#### Repository Interface Updates (`src/data/repositories/participant_repository.py`)
- **Role Parameters**: Repository methods accept `user_role` parameter for filtering
- **Consistent Interface**: All search methods updated to enforce role-based access
- **Abstract Compliance**: Interface ensures all implementations apply proper filtering

### Security Features

#### Multi-Layer Security
1. **Configuration Validation**: Role assignments validated at startup
2. **Handler Enforcement**: Authorization checks at conversation entry points
3. **Service Layer Filtering**: Data filtering applied before UI presentation
4. **Repository Security**: Final data access layer enforces role restrictions

#### Performance & Reliability
- **Advanced Caching**: Dual-tier caching system with 5-minute and 1-minute TTL options
- **Exceptional Performance**: Cache hits 0.22ms (95th percentile), cache misses 0.45ms (99th percentile)
- **Authorization Benchmarks**: Exceeds requirements by 450x (requirement: <100ms, achieved: 0.22ms)
- **Thread-Safe Caching**: Concurrent access optimized with LRU eviction and health monitoring
- **Security Audit Performance**: Full audit logging with <1ms overhead
- **Fallback Configuration**: Environment variables provide backup when Airtable unavailable
- **Error Recovery**: Graceful degradation with clear error messaging
- **Test Coverage**: 64+ comprehensive tests covering security scenarios

#### Privacy Compliance
- **Hashed Logging**: User IDs hashed in authorization logs to protect privacy
- **Minimal Data Exposure**: Viewers see only non-sensitive participant information
- **Secure by Default**: Unknown users/roles receive minimal access permissions

### Handler Security Testing Coverage (Added 2025-09-25)

#### Comprehensive Authorization Test Suites
- **35+ Authorization Tests**: Complete test coverage across all secured handlers
- **Test Categories**: Unauthorized access blocking, authorized access validation, role hierarchy enforcement
- **TDD Implementation**: Test-driven development approach with Red-Green-Refactor methodology
- **Integration Test Updates**: Core integration tests updated with authorization mocks for compatibility

#### Security Implementation Verification
- **Zero Authorization Bypass**: All handlers require appropriate role levels
- **Consistent Error Messages**: Standardized Russian denial messages across all handlers
- **Performance Validation**: Authorization checks maintain <50ms response times
- **Production Ready**: Complete security posture suitable for immediate deployment

### Future Airtable Integration Readiness

#### AuthorizedUsers Table Mapping (`src/config/field_mappings.py`)
- **Field Mapping Constants**: AccessLevel, Status, TelegramUserID field mappings
- **Option ID Support**: Role option IDs for future Airtable sync implementation
- **Schema Compliance**: Field IDs follow proper Airtable format (17 characters, 'fld' prefix)

#### Sync Architecture Foundation
- **Environment Fallback**: Current role configuration serves as backup during Airtable sync failures
- **Cache Invalidation**: Manual /auth_refresh command enables real-time role updates without bot restart
- **Extensible Design**: Authorization utilities designed for future Airtable integration

## Key Architectural Components

### Conversation Management

**Search Conversation Handler**:
- Multi-state conversation flow for participant search and editing
- State transitions: SEARCH → RESULTS → DETAILS → EDITING → CONFIRMATION
- Context preservation across state changes
- Integration between search and editing workflows
- **State Collision Prevention**: SearchStates uses values 10-12 to avoid conflicts with EditStates 0-2
- **Mixed Handler Support**: ConversationHandler configured with per_message=None for proper CallbackQueryHandler tracking
- **Automatic Timeout Handling**: Configurable conversation timeout (default 30 minutes) prevents users from getting stuck in stale states

**Room and Floor Search Handlers** (New - 2025-09-04):
- Dedicated conversation handlers for location-based searches
- **RoomSearchStates**: AWAITING_ROOM_INPUT for room number collection
- **FloorSearchStates**: AWAITING_FLOOR_INPUT for floor number collection  
- **Search Mode Selection**: MODE_SELECTION state for choosing between name/room/floor search
- Integration with main search conversation via unified entry points
- Russian language support throughout all conversation states

**Participant Editing Handler** (New - 2025-08-29):
- 4-state ConversationHandler for comprehensive field editing
- States: FIELD_SELECTION → TEXT_INPUT/BUTTON_SELECTION → CONFIRMATION
- Russian localization across all states
- Field-specific validation and error handling

**Participant Lists Handler** (Enhanced 2025-01-21):
- Role-based bulk participant list access via "📋 Получить список" main menu button with department filtering
- **Department Filtering Integration**: Complete workflow from team selection to department-specific lists
- **List Navigation States**: Integrated with existing SearchStates for seamless conversation flow
- **Department Context Preservation**: Department filter state maintained through pagination and navigation
- **Enhanced Navigation**: "🔄 Выбор департамента" button returns users to department selection
- **Chief-First Sorting**: Department chiefs automatically appear at top of filtered lists
- **Russian Localization**: All department names translated and displayed in Russian
- **Offset-based Pagination**: Advanced pagination system prevents participant skipping during message length trimming
- **Dynamic Page Sizing**: Automatically adjusts participants per page to stay under Telegram's 4096-character limit
- **State Management**: Maintains current role, department filter, and navigation offset in user context
- **MarkdownV2 Escaping**: Safe rendering of user-generated content preventing formatting injection attacks
- Integration with existing main menu and conversation patterns without breaking changes

**Export Conversation Handler** (New - 2025-09-22):
- Interactive export conversation flow converting `/export` command to selection-based workflow
- 6 export options with Russian localization: Export All, Export Team, Export Candidates, Export by Department, Export Bible Readers, Export ROE
- Department selection submenu with all 13 departments for targeted filtering
- ConversationHandler-based state management with proper conversation flow
- Service factory integration for all export types without service layer modifications
- Admin authentication validation at conversation entry point
- Progress tracking integration with ExportProgressTracker for real-time user feedback
- Mobile-optimized inline keyboards with 2-column and 3-column layouts
- Complete error handling with user-friendly Russian error messages
- Cancel and navigation support with clean state management
- File delivery integration with automatic cleanup and resource management

**Conversation Timeout Handler** (2025-01-09):
- Automatic timeout handling for all conversation states including export and list functionality
- Configurable timeout period via `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` environment variable
- Russian timeout message display: "Сессия истекла, начните заново"
- Main menu recovery button for seamless user experience
- Graceful state cleanup prevents memory leaks and stale conversation data
- **Text Button Entry Points**: MessageHandler entry points for "🔍 Поиск участников", "📋 Получить список", and Main Menu text buttons enable conversation re-entry after timeout without requiring /start command

### Data Access Patterns

**Repository Pattern**:
- `ParticipantRepository` abstract interface
- `AirtableParticipantRepo` concrete implementation
- Support for search, retrieval, and **selective field updates**
- **Multi-Table Repository Support** (2025-09-22):
  - `BibleReadersRepository` abstract interface for Bible reading session management
  - `ROERepository` abstract interface for ROE (Rollo of Encouragement) session management
  - Repository interfaces follow consistent patterns across all table types
  - Factory pattern for table-specific client creation with cached client reuse
  - Table-specific export services with repository integration
  - Multi-table data access for export operations with participant hydration

**New Capabilities**:
- `update_by_id()` method for partial field updates (2025-08-29)
- **Room/Floor search methods** (2025-09-04):
  - `find_by_room_number(room: str)` - Filter participants by room assignment
  - `find_by_floor(floor: Union[int, str])` - Filter participants by floor
- **Floor discovery method** (Enhanced 2025-01-21):
  - `get_available_floors()` - Return floors containing participants with 5-minute caching
  - **Interactive Floor Discovery Support**: Powers inline keyboard generation for seamless user experience
- **Department filtering method** (Enhanced 2025-01-21):
  - `get_team_members_by_department(department: Optional[Department])` - Filter participants by department with chief-first sorting
  - **Chief-First Ordering**: Department chiefs (IsDepartmentChief = true) appear first in results
  - **Optimized Airtable Queries**: Server-side filtering with complex sorting parameters
- Field mapping between internal models and Airtable schema
- Rate limiting and error recovery for update operations
- **Security enhancements** with formula injection prevention
- **Service factory pattern** for centralized dependency injection (2025-09-04)
- **Multi-Table Configuration**: Extended DatabaseSettings with BibleReaders and ROE table support
- **Airtable Client Factory**: Table-specific client creation with dependency injection support
- **View-Based Data Access** (Updated 2025-09-27):
  - `list_view_records(view: str)` - Raw Airtable view record retrieval preserving field order
  - View-driven export architecture maintaining exact Airtable column ordering
  - Header reconstruction from actual view data including linked relationship fields
  - Configurable view names for Participants (Кандидаты), ROE (РОЕ: Расписание), and Bible Readers (Чтецы: Расписание) exports
  - Graceful fallback to repository filtering when views unavailable

### Service Layer Architecture

**Schedule Service** (Enhanced 2025-09-28):
- Airtable schedule data retrieval with 10-minute TTL caching
- Event filtering by date range and active status
- Service factory integration for dependency injection
- Error handling with graceful fallback for empty schedules

**Schedule Formatting Service** (Enhanced 2025-09-28):
- **Advanced Schedule Formatting**: Comprehensive Russian localization and intelligent visual hierarchy
- **Section Detection System**: Smart parsing of section markers from event descriptions
- **Multi-line Content Support**: Proper handling of detailed event descriptions with bullet point formatting
- **Audience Translation Engine**: Automatic translation of audience types to Russian
  - English/Mixed → Russian: `All` → `Все`, `Team` → `Тимы`, `Candidates` → `Кандидаты`
  - Alias Support: `leadership`, `clergy` → `Тимы`, `candidate` → `Кандидаты`
- **Hierarchical Visual Structure**: Enhanced bullet point system for improved readability
  - Primary events: `•` (bullet symbol) for main schedule items
  - Sub-details: `◦` (white bullet) for location and description details
- **Time Range Formatting**: Proper en-dash separator (`–`) for professional time display
- **Day Label Integration**: Support for human-readable day headers in Russian
- **Empty Schedule Handling**: Graceful Russian messaging when no events exist for a day

**Participant Update Service** (2025-08-29):
- Centralized validation logic for all field types
- Russian error message generation
- Enum value conversion (Gender, Size, Role, Department, Payment Status)
- Special validation for numeric and date fields

**Enhanced Export Services with View Alignment** (Updated 2025-09-27):
- **Participant Export Service**: Extended with view-driven architecture for Airtable alignment
  - **View-Aligned Exports**: All participant exports use configurable "Кандидаты" view for consistent column ordering
  - **Column Order Preservation**: Exports maintain exact Airtable view ordering for direct comparison
  - **Department-based filtering**: Export participants from specific departments using view structure with participant hydration
  - **Header Reconstruction**: Headers built from actual view data including linked relationship fields
  - **View-Driven Methods**: `_export_view_to_csv()`, `_determine_view_headers()`, `_records_to_csv()`
  - **Graceful Fallback**: Automatic repository filtering when view unavailable with 422 error detection
  - Complete export: Full participant database export (existing functionality maintained)
- **BibleReaders Export Service**: Dedicated export service for Bible reading assignments
  - **View-Aligned Architecture**: Uses configurable "Чтецы: Расписание" view for column ordering
  - Participant name hydration from linked participant IDs
  - CSV generation with view-aligned column order and participant names embedded in the `Participants` column
  - **Graceful Fallback**: Repository filtering when view unavailable
  - Progress tracking and file management integration
- **ROE Export Service**: Dedicated export service for ROE session data
  - **View-Aligned Architecture**: Uses configurable "РОЕ: Расписание" view for column ordering
  - Multi-relationship hydration (presenters, assistants, prayer partners)
  - Scheduling metadata inclusion (date/time/duration)
  - **Graceful Fallback**: Repository filtering when view unavailable
  - Complex presenter information handling
- **Repository Interface Extensions**:
  - `list_view_records(view: str)` method for raw Airtable view data access
  - View-based record retrieval preserving field order and structure
- **Service Factory Integration**: All export services accessible through centralized factory pattern
- **Linked Field Support**: Relationship fields (Roe, BibleReaders, ROE 2) included with proper formatting
- UTF-8 encoding support for Russian text content
- Telegram file size limit validation (50MB)
- Secure temporary file management with automatic cleanup
- View-aligned headers for consistency with live Airtable base structure
- Consistent CSV formatting across all export services

**Search Service Extensions** (Enhanced 2025-01-21):
- **Room-based search**: `search_by_room(room: str)` with input validation
- **Floor-based search**: `search_by_floor(floor: Union[int, str])` with type conversion
- **Interactive Floor discovery service**: `get_available_floors()` with 5-minute caching and error resilience
- **UI Integration Support**: Service methods designed to power interactive keyboard components
- **Formatted results**: `search_by_room_formatted(room: str)` for UI consumption
- **Validation utilities**: Comprehensive input validation with `ValidationResult` objects

**Participant List Service** (Enhanced 2025-01-21):
- **Role-based List Access**: `get_team_members_list()` and `get_candidates_list()` methods
- **Complete Department Filtering**: Enhanced with optional department parameter for targeted filtering
- **Department Selection Integration**: Supports full workflow from role selection to department-specific lists
- **Chief Indicator Formatting**: Crown emoji (👑) displayed before department chiefs' names
- **Chief-First Ordering**: Department chiefs automatically appear first in all filtered lists
- **Server-side Filtering**: Leverages repository `get_team_members_by_department()` method for efficient Airtable queries
- **Russian Department Translation**: Integrates department_to_russian function for consistent localization
- **Navigation Context Support**: Department filter information included in pagination metadata
- **Backward Compatibility**: Optional department parameter maintains existing API contracts
- **Advanced Pagination**: Offset-based pagination with continuity guarantee preventing participant skipping
- **Dynamic Message Length Handling**: Iterative participant removal to stay under 4096-character Telegram limit
- **Russian Formatting**: Complete Russian localization with DD.MM.YYYY date format and numbered list display
- **MarkdownV2 Support**: Safe content escaping preventing formatting injection from user-generated data
- **Pagination Metadata**: Returns navigation information (current_offset, next_offset, prev_offset, actual_displayed)
- **Empty Result Handling**: Graceful "Участники не найдены." messaging for empty role categories and departments

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
- **Search mode keyboards** (2025-09-04): Centralized search type selection with name/room/floor options
- **Interactive Floor Discovery Keyboards** (2025-01-21):
  - `get_floor_discovery_keyboard()`: Single button for floor discovery
  - `get_floor_selection_keyboard()`: Dynamic buttons for available floors (3 per row)
  - **Callback Data Patterns**: `floor_discovery` and `floor_select_{number}` for proper routing

**Localization Strategy**:
- Russian field names and labels
- Localized validation error messages
- Russian navigation buttons and prompts
- Enum value translation (M/F → Мужской/Женский)
- **Complete Russian interface** for room/floor search functionality with mobile-optimized reply keyboards
- **Interactive Floor Discovery Messages** (2025-01-21):
  - Enhanced guidance: "Выберите этаж из списка или пришлите номер этажа цифрой:"
  - Floor display headers and error messages in Russian
  - Graceful fallback messages: "Произошла ошибка. Пришлите номер этажа цифрой."

**Navigation Architecture** (Enhanced 2025-09-04):
- **Multi-mode Search Interface**: Unified entry point with mode selection
- **Reply Keyboard Navigation**: Mobile-optimized keyboards for search mode selection
- **State-based Routing**: Proper conversation state management between different search types
- **Context Preservation**: Seamless transitions between search modes while maintaining user context

## Component Integration

### Search → Edit → Save Workflow
1. User searches via `/search` command or Main Menu button
2. Results display with "Подробнее" (Details) buttons  
3. Button click transitions to participant editing interface
4. Editing interface shows complete profile with 13 edit buttons
5. Field editing uses appropriate input method (buttons vs text)
6. **Save confirmation screen** displays all pending changes in "Current → **New**" format
7. User confirms save operation or cancels to discard changes
8. Changes committed via repository `update_by_id()` method with retry mechanism
9. User returns to search results with context preserved

### Export Conversation Workflow (New 2025-09-22)
1. User (admin) types `/export` command
2. Bot validates admin access using auth utilities
3. **Export Selection Menu**: Bot displays 6 export options with Russian labels in mobile-optimized 2-column layout
4. **Direct Export Path**: User selects "Export All", "Export Team", "Export Candidates", "Export Bible Readers", or "Export ROE" → Bot begins processing immediately
5. **Department Export Path**: User selects "Export by Department" → Bot displays department selection submenu with all 13 departments in 3-column layout
6. **Department Selection**: User selects specific department → Bot begins department-filtered export processing
7. **Export Processing**: Selected export type processed through service factory with progress notifications
8. **Progress Updates**: Real-time progress tracking with throttled notifications (2-second intervals) displaying percentage and participant counts
9. **File Delivery**: CSV file generated and delivered via Telegram document upload with automatic cleanup
10. **Navigation & Cancel**: Cancel options at each step return to main menu, back navigation between selection screens
11. **Error Handling**: Comprehensive error scenarios with user-friendly Russian messages and recovery options

### Get List → Department Filtering → Navigation → Main Menu Workflow (Enhanced 2025-01-21)
1. User clicks "📋 Получить список" from main menu
2. Bot displays role selection: "👥 Команда" (Team) or "🎯 Кандидаты" (Candidates)
3. **Team Selection Path**: User selects "👥 Команда" → Bot displays department filtering interface with 15 options
4. **Department Selection**: User selects specific department or "Все участники" → Bot displays filtered list
5. **Candidate Selection Path**: User selects "🎯 Кандидаты" → Bot displays all candidates directly (bypasses department filtering)
6. **Enhanced Navigation**: User can navigate pages using "◀️ Назад", "▶️ Далее", "🔄 Выбор департамента" buttons
   - Department filter context preserved through pagination
   - Offset-based navigation ensures no participants are skipped during message length trimming
   - Dynamic page sizing automatically adjusts to stay under 4096-character limit
   - State management maintains current role, department filter, and navigation position across transitions
7. **Department Navigation**: "🔄 Выбор департамента" returns to department selection for easy filter changes
8. **Main Menu Return**: "🏠 Главное меню" button provides clean return to main menu with proper state reset
9. **Coexistence**: List functionality with department filtering operates alongside existing search without interference

**Main Menu Start Command Equivalence** (Enhanced 2025-09-09):
- **Shared Initialization**: Both `/start` command and Main Menu button use shared helpers (`initialize_main_menu_session()` and `get_welcome_message()`) ensuring identical functionality
- **Consistent Welcome Message**: Both entry points display the same Russian welcome: "Добро пожаловать в бот Tres Dias! 🙏\n\nВыберите тип поиска участников."
- **State Initialization**: Both handlers set identical user_data keys (`search_results = []`, `force_direct_name_input = True`)
- **Timeout Recovery**: Text button handlers allow re-entry after conversation timeout without requiring manual /start commands

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
- **Automatic Timeout Management**: All conversation states include TIMEOUT handler for inactive session cleanup
- **Timeout Recovery**: Users can restart from main menu after session expiration with clear Russian instructions

### Data Flow
```
User Input → Handler → Service (validation) → Repository → Airtable API
     ↓                                                        ↓
UI Response ← Keyboard ← Error/Success ← Update Result ← API Response
```

**Export Conversation Flow** (New 2025-09-22):
```
/export Command → Admin Validation → Export Selection Menu → Department Selection (if needed) → Service Factory → Export Processing
       ↓                ↓                    ↓                        ↓                        ↓                ↓
Conversation State ← Auth Check ← Inline Keyboard ← Department Filter ← Service Selection ← Progress Updates
       ↓                                                                                                      ↓
File Delivery ← CSV Generation ← Repository Access ← Table-Specific Client ← Multi-Table Data ← Progress Completion
```

**Multi-Table Data Access Flow** (Enhanced 2025-09-22):
```
Export Request → Service Factory → Repository Factory → Table-Specific Client → Airtable API (Multi-Table)
        ↓              ↓                   ↓                    ↓                      ↓
Progress Tracking ← Service Selection ← Data Models ← Client Factory ← AirtableConfig ← Multi-Table Response
```

**Room/Floor Search Flow** (Enhanced 2025-01-21):
```
Search Mode Selection → Enhanced Floor Input → Interactive Discovery OR Manual Input → Validation → Repository Query → Formatted Results
        ↓                         ↓                           ↓                                                     ↓
Reply Keyboard ← Enhanced Russian Messages ← Callback Handling ← Service Layer ← Interactive Keyboard Generation ← Result Formatting
```

**Interactive Floor Discovery Flow** (New 2025-01-21):
```
Floor Discovery Button Click → Callback Handler → get_available_floors() → Floor Selection Keyboard → User Floor Click → Floor Search
              ↓                        ↓                      ↓                         ↓                       ↓
      Callback Acknowledgment ← Error Recovery ← Cached Results ← Dynamic Button Gen ← Message Edit ← Search Execution
```

## Scalability Considerations

### Performance
- Rate limiting built into Airtable client (5 requests/second)
- Selective field updates reduce API call overhead
- In-memory state management for conversation context
- **Floor discovery caching**: 5-minute TTL reduces API load by up to 12x during active usage
- **Interactive Export Conversation**: Conversation-based export with state management optimized for user experience
- **Export Selection Optimization**: Mobile-optimized keyboards reduce interaction time and improve usability
- **Service Factory Efficiency**: Centralized service access reduces initialization overhead across export types
- **Department Selection Caching**: Department list generation optimized for quick secondary menu display
- **CSV Export Capabilities**: Admin-only data export with progress tracking and file management
- **Authentication Utilities**: Admin user validation with robust type handling and settings integration
- **Export Progress Throttling**: 2-second minimum intervals prevent Telegram rate limit violations during long exports
- **Streaming CSV Generation**: Memory-efficient export processing for large datasets (1500+ participants tested)
- **Secure File Management**: Automatic cleanup prevents storage accumulation from export operations

### Maintainability  
- Separation of concerns across 3 layers
- Repository pattern allows easy database backend switching
- Service layer centralizes business logic and validation
- Keyboard factory pattern simplifies UI management

### Testability
- 96+ unit tests including editing and room/floor search functionality (100% pass rate)
- Mock repositories for isolated testing
- Service layer testing with comprehensive validation scenarios
- Handler testing with conversation state simulation
- **Room/Floor search testing**: 55 comprehensive tests covering:
  - Backend: 34 tests (repository, service, validation, security layers)
  - Frontend: 21 tests (handler logic, conversation flows, keyboard integration, Russian localization)

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
