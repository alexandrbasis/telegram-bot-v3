# API Design

## Authorization and Performance API

### Security Audit Service API (Added 2025-09-25)
**Purpose**: Comprehensive security event logging and performance monitoring

**Core Components**:
- `SecurityAuditService`: Main service class for security event management
- `AuthorizationEvent`: Structured authorization attempt logging
- `SyncEvent`: Airtable synchronization event tracking
- `PerformanceMetrics`: Authorization performance measurement

**Authorization Event Structure**:
```python
@dataclass
class AuthorizationEvent:
    user_id: Optional[int]           # Telegram user ID
    action: str                      # Action attempted
    result: str                      # "granted" or "denied"
    user_role: Optional[str]         # Resolved user role
    cache_state: str                 # "hit", "miss", "expired", "error"
    timestamp: datetime              # Event timestamp (UTC)
    airtable_metadata: Optional[Dict] # Related Airtable data
    error_details: Optional[str]     # Error context if applicable
```

**Performance Benchmarks**:
- **Cache Hits**: 0.22ms at 95th percentile (requirement: <100ms) - 450x faster
- **Cache Misses**: 0.45ms at 99th percentile (requirement: <300ms) - 665x faster
- **Concurrent Access**: <75ms at 95th percentile under load
- **Large Scale**: Performance maintained with 10K+ users

**Security Vulnerabilities Discovered**:
- **CRITICAL**: Cache poisoning vulnerability allowing privilege escalation
- **MEDIUM**: Timing attack vulnerability (0.60ms variance) enabling user enumeration

### Authorization Cache API (Added 2025-09-25)
**Purpose**: High-performance authorization caching with thread safety and health monitoring

**Core Features**:
- **TTL Management**: 60-second default TTL with configurable options
- **LRU Eviction**: 10,000 entry limit with intelligent eviction
- **Thread Safety**: Concurrent access support with locking
- **Health Monitoring**: Real-time statistics and performance tracking
- **Manual Invalidation**: Selective cache clearing for security updates

**API Methods**:
```python
cache = get_authorization_cache()
role, cache_state = cache.get(user_id)    # Returns (role, "hit"/"miss"/"expired")
cache.set(user_id, role)                  # Set role in cache
cache.invalidate(user_id)                 # Remove specific user
cache.clear()                             # Clear all entries
stats = cache.get_stats()                 # Performance statistics
```

## Bot Command API

### Search API

#### `/search [query]`
**Purpose**: Multi-field participant search with Russian/English support

**Input Parameters**:
- `query` (string): Search term for name, church, location, or other fields

**Response Format**:
- Paginated results (up to 10 per page)
- Match quality indicators (Отличное/Хорошее/Частичное совпадение)
- Interactive buttons for participant selection

**Example Response**:
```
Результаты поиска: "Иван"

1. Иван Петров | Кандидат | ROE
   Отличное совпадение
   [Подробнее]

2. Ivan Petrov | Команда | Chapel  
   Хорошее совпадение
   [Подробнее]

[Назад] [Далее]
```

#### Room/Floor Search API (New - 2025-09-04)
**Purpose**: Location-based participant search by room number or floor

**Room Search**: `/search room:[room_number]` (Enhanced 2025-01-09)
- **Input**: Room number (alphanumeric: "101", "A1", "Conference")
- **Validation**: Non-empty string, handles numeric and alphanumeric formats
- **Response**: Structured Russian-formatted results with role, department, and floor information

**Floor Search**: `/search floor:[floor_number]`
- **Input**: Floor number (integer or string: "1", "2", "Ground")
- **Validation**: Union[int, str] with proper conversion
- **Response**: Participants grouped by room on specified floor
- **Floor Discovery**: Utilizes backend `get_available_floors()` service to determine floors containing participants

**Enhanced Room Search Response (2025-01-09)**:
```
🏠 Комната 205:

👤 Иван Петров (Иван Петров)
   Роль: Кандидат
   Департамент: ROE
   Этаж: 2

👤 Мария Иванова (Maria Ivanova)
   Роль: Команда
   Департамент: Кухня  
   Этаж: 2

Всего найдено: 2 участника
```

**Translation Support**: Complete Russian translations for all departments and roles using `src/utils/translations.py` utility module.

**Example Floor Search Response**:
```
Участники на этаже: "2"

Комната 201:
1. Петр Иванов | Кандидат

Комната 205:
2. Иван Петров | Кандидат
3. Мария Смирнова | Команда
```

## Department Filtering API (Enhanced 2025-01-21)

### Repository Layer Department Filtering
**Purpose**: Filter participant lists by department assignment with chief-first ordering

**Repository Interface**: `get_team_members_by_department(department: Optional[Department]) -> List[Participant]`
- **Department Parameter**: Optional department filter (None returns all participants)
- **Chief-First Sorting**: Chiefs (IsDepartmentChief = true) appear first in results
- **Airtable Integration**: Uses optimized filtering formulas and sort parameters
- **Secondary Sorting**: Alphabetical by Church field after chief prioritization

**Implementation Details**:
```python
# Repository method signature
async def get_team_members_by_department(
    self,
    department: Optional[Department] = None
) -> List[Participant]:
    """Get team members filtered by department with chief-first ordering."""
```

**Airtable Query Generation**:
- **Department Filtering**: `{Department} = 'ROE'` for specific departments
- **Chief-First Sort**: `sort=[{field: 'IsDepartmentChief', direction: 'desc'}, {field: 'Church', direction: 'asc'}]`
- **Unassigned Filter**: `{Department} = BLANK()` for participants without departments
- **All Participants**: No filter applied when department=None

### Service Layer Integration
**Purpose**: Integrate department filtering into existing list services with backward compatibility

**Service Interface**: `get_team_members_list(department: Optional[Department] = None) -> PaginatedResponse`
- **Backward Compatibility**: Optional department parameter maintains existing API contracts
- **Chief Indicator Formatting**: Crown emoji (👑) displayed before department chiefs' names
- **Filtered Results**: Efficient server-side filtering reduces query response sizes by 80-90%

**Chief Indicator Display Format**:
```python
# Chief formatting logic
if participant.is_department_chief:
    display_name = f"👑 {participant.full_name_ru}"
else:
    display_name = participant.full_name_ru
```

**Example API Response**:
```
**Список участников команды - ROE** (элементы 1-15 из 23)

1. **👑 Иван Петров** (Руководитель отдела)
   🏢 Отдел: ROE
   ⛪ Церковь: Храм Христа Спасителя

2. **Мария Иванова**
   🏢 Отдел: ROE
   ⛪ Церковь: Церковь Святого Николая

... (continues with remaining participants)
```

## Participant Editing API

### Participant Selection
**Trigger**: Click "Подробнее" (Details) button from search results

**Response**: Complete participant profile with editing interface

**Profile Display Format**:
```
Участник: Иван Петров

Имя (русское): Иван Петров
Имя (английское): Ivan Petrov
Церковь: Храм Христа Спасителя
Местоположение: Москва, Россия
Пол: Мужской
Размер: L
Роль: Кандидат
Департамент: ROE
Контакты: +7-123-456-78-90
Статус платежа: Оплачено
Сумма платежа: 5000
Дата платежа: 2025-08-15
Дата рождения: 1985-03-10
Возраст: 39
Кто подал: Мария Иванова

[Изменить имя (русское)] [Изменить имя (английское)]
[Изменить церковь] [Изменить местоположение]
[Изменить пол] [Изменить размер]
[Изменить роль] [Изменить Департамент]
[Изменить контакты] [Изменить статус платежа]
[Изменить сумму] [Изменить дату платежа]
[🎂 Изменить дату рождения] [🔢 Изменить возраст]
[Изменить кто подал]

[Сохранить изменения] [Отмена] [Назад к поиску]
```

### Field Editing APIs

#### Button-Based Field Selection
**Fields**: Gender, Size, Role, Department, Payment Status  
**Behavior**: Immediate inline keyboard display with options

**Gender Edit API**:
```
Выберите пол:

[Мужской] [Женский]
[Отмена]
```

**Size Edit API**:
```
Выберите размер:

[XS] [S] [M]
[L] [XL] [XXL]
[3XL]
[Отмена]
```

**Department Edit API**:
```
Выберите Департамент:

[ROE] [Chapel] [Setup]
[Palanka] [Administration] [Kitchen]
[Decoration] [Bell] [Refreshment]
[Worship] [Media] [Clergy]
[Rectorate]
[Отмена]
```

#### Text Input Field APIs
**Fields**: Full Names, Church, Location, Contact, Submitted By  
**Behavior**: Prompt message → Wait for text input → Validation → Update

**Text Input Prompts**:
- Russian Name: "Отправьте новое имя на русском"
- English Name: "Отправьте новое имя на английском"
- Church: "Отправьте название церкви"
- Location: "Отправьте страну и город"
- Contact: "Отправьте контактную информацию"
- Submitted By: "Отправьте имя того, кто подал"

#### Special Validation Field APIs
**Payment Amount**: Integer validation with Russian error messages
**Payment Date**: Date format validation (YYYY-MM-DD)

**Payment Amount API**:
```
Prompt: "Отправьте сумму платежа (только цифры)"
Validation: Integer ≥ 0
Error: "Ошибка: Сумма должна быть положительным числом"
```

**Payment Date API**:
```
Prompt: "Отправьте дату в формате ГГГГ-ММ-ДД"
Validation: YYYY-MM-DD format
Error: "Ошибка: Дата должна быть в формате ГГГГ-ММ-ДД"
```

**Date of Birth API** (Fixed 2025-09-11):
```
Prompt: "📅 Введите дату рождения в формате ГГГГ-ММ-ДД (например: 1990-05-15):"
Validation: YYYY-MM-DD format with date parsing
Clearing: Whitespace-only input clears field (sets to None)
Error: "❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД (например: 1990-05-15)" + InfoMessages guidance
Serialization: Fixed JSON serialization error for Airtable API
```

**Age API** (Fixed 2025-09-11):
```
Prompt: "🔢 Введите возраст (от 0 до 120):"
Validation: Integer range 0-120
Clearing: Whitespace-only input clears field (sets to None)
Errors: "❌ Возраст должен быть от 0 до 120" or "❌ Возраст должен быть числом" + InfoMessages guidance
Display: Fixed participant reconstruction to include age field in all contexts
```

## Data Export API

### /export Command API
**Purpose**: Administrative CSV export with filtering capabilities for participant database

#### Enhanced Export Services (2025-09-22)
**Export Service Extensions**: Extended export capabilities with role-based and department-based filtering for targeted data subsets

**Participant Export Service Filtering**:
- **Role-Based Filtering**: `get_participants_by_role_as_csv(role: Role)` - Export only TEAM members or CANDIDATES
- **Department-Based Filtering**: `get_participants_by_department_as_csv(department: Department)` - Export participants from specific departments
- **Complete Export**: `get_all_participants_as_csv()` - Full participant database export (existing functionality)

**New Export Services with Enhanced Reliability (2025-09-26)**:
- **BibleReaders Export**: `BibleReadersExportService.get_bible_readers_as_csv()` - Exports Bible reading assignments with participant details
- **ROE Export**: `ROEExportService.get_roe_sessions_as_csv()` - Exports ROE session data with presenter information

**Enhanced Export Service Features (2025-09-26)**:
- **Async Export Interfaces**: All export services now provide both `export_to_csv_async()` and `export_to_csv()` methods
- **Event Loop Detection**: Sync wrappers automatically detect running event loops and delegate appropriately
- **Fallback Logic**: Candidate exports implement automatic fallback when Airtable views are unavailable
- **Error Recovery**: 422 VIEW_NAME_NOT_FOUND errors trigger seamless fallback to repository filtering
- **Participant Hydration**: BibleReaders and ROE exports include hydrated participant names from linked participant IDs
- **Multi-Relationship Handling**: ROE service handles complex relationships (presenters, assistants, prayer partners)
- **Consistent CSV Format**: All export services maintain uniform CSV formatting with proper field headers
- **Progress Tracking**: All services integrate with ExportProgressTracker for real-time progress updates
- **Line Number Consistency**: Sequential line numbering preserved across all export flows
- **Comprehensive Error Handling**: Graceful handling of view availability and empty result scenarios

**Authorization**:
- **Admin Validation**: Uses `auth_utils.is_admin_user()` for access control
- **Settings Integration**: Admin user IDs from `ADMIN_USER_IDS` environment variable
- **Type Safety**: Handles Union[int, str, None] user ID types with conversion
- **Security Logging**: Comprehensive logging for access attempts and failures

**Request Flow**:
```
/export command → Admin validation → Progress notifications → CSV generation → File delivery
```

**Response Format**:
```
🔄 Начинается экспорт данных участников...
📈 Экспорт: 25% завершено (250/1000 участников)
📈 Экспорт: 50% завершено (500/1000 участников)
📈 Экспорт: 75% завершено (750/1000 участников)
✅ Экспорт завершён! Отправляю файл...
[CSV file attachment: participants_export_YYYY-MM-DD_HH-MM.csv]
```

**Progress Tracking API**:
- **Throttled Notifications**: Minimum 2-second intervals prevent Telegram rate limiting
- **Progress Updates**: Real-time export status with percentage and count
- **ExportProgressTracker**: Dedicated class for progress management
- **Message Pattern**: Consistent Russian progress messages

**Error Response API with File Delivery**:
```
# Unauthorized access
{
  "message": "Доступ запрещён. Эта команда доступна только администраторам.",
  "status": "access_denied"
}

# Export failure
{
  "message": "Произошла ошибка при экспорте данных. Попробуйте позже.",
  "status": "export_failed"
}

# File too large (enhanced with 50MB limit)
{
  "message": "Файл слишком большой для отправки через Telegram (максимум 50MB).",
  "status": "file_size_exceeded"
}

# Comprehensive Telegram API Error Handling
# RetryAfter error with automatic retry
{
  "message": "Слишком много запросов. Повторная попытка...",
  "status": "retry_after",
  "retry_seconds": 30,
  "attempt": "1/3"
}

# BadRequest error with validation details
{
  "message": "Неверный формат файла или превышен размер.",
  "status": "bad_request"
}

# NetworkError with retry mechanism
{
  "message": "Ошибка сети. Повторная попытка...",
  "status": "network_error",
  "attempt": "2/3"
}

# General TelegramError with audit logging
{
  "message": "Ошибка Telegram API. Попробуйте позже.",
  "status": "telegram_error",
  "logged": "admin_audit_trail"
}
```

**Enhanced CSV Export Service API with Reliability Features (2025-09-26)**:
- **Participant Service Methods**:
  - `get_all_participants_as_csv(progress_callback)` - Complete database export
  - `get_participants_by_role_as_csv(role: Role, progress_callback)` - View-aligned export with fallback for TEAM/CANDIDATE roles
  - `get_participants_by_department_as_csv(department: Department, progress_callback)` - Department-filtered export using view structure
- **View-Based Export Architecture with Fallback**:
  - `_export_view_to_csv(view_name, filter_func)` - Core view-driven export method with error handling
  - `_is_view_not_found_error(error)` - Detects 422 VIEW_NAME_NOT_FOUND errors for fallback logic
  - `_fallback_candidates_from_all_participants()` - Repository filtering fallback maintaining line numbers
  - `_determine_view_headers(view_name, records)` - Header reconstruction from view data
  - `_records_to_csv(rows, headers)` - Convert records maintaining view column order
- **BibleReaders Service Methods with Async Interface**:
  - `export_to_csv_async()` - Async interface for handler integration
  - `export_to_csv()` - Sync wrapper with event loop detection
  - `get_bible_readers_as_csv(progress_callback)` - Bible reading assignments with participant names
- **ROE Service Methods with Async Interface**:
  - `export_to_csv_async()` - Async interface for handler integration
  - `export_to_csv()` - Sync wrapper with event loop detection
  - `get_roe_sessions_as_csv(progress_callback)` - ROE sessions with presenter/assistant/prayer partner details
- **Repository Interface Extensions**:
  - `list_view_records(view: str) -> List[Dict[str, Any]]` - Fetch raw Airtable view records preserving structure
- **Service Factory Integration**: All export services available through ServiceFactory pattern
- **Progress Callbacks**: Optional callback for UI updates (every 10 records)
- **View-Aligned Headers**: Headers reconstructed from actual view data including linked fields
- **UTF-8 Encoding**: Proper Russian text support
- **File Management**: Secure temporary file creation with automatic cleanup
- **Participant Hydration**: Linked participant data resolved to names for actionable CSV output
- **Column Order Preservation**: Exports maintain exact Airtable view ordering for direct comparison

**File Delivery API with Comprehensive Error Handling**:
- **Format**: CSV with exact Airtable field names as headers
- **Encoding**: UTF-8 for Russian text support
- **Filename**: `participants_export_YYYY-MM-DD_HH-MM.csv` pattern
- **Size Limit**: 50MB Telegram upload limit with pre-validation
- **Delivery Method**: Telegram document upload API with comprehensive error handling
- **Error Recovery**: Automatic retry mechanism for transient failures (up to 3 attempts)
- **Retry Logic**: Exponential backoff for RetryAfter errors with user progress updates
- **Cleanup**: Guaranteed temporary file removal with try-finally blocks even on failures
- **Audit Logging**: Complete user interaction logging for all delivery attempts and errors
- **Resource Management**: Secure file creation in temporary directories with automatic cleanup

**Integration Points with File Delivery**:
- **Repository Pattern**: Uses existing ParticipantRepository interface
- **Service Factory**: Integrated via ServiceFactory for dependency injection
- **3-Layer Architecture**: Bot → Service → Repository pattern compliance
- **Settings Integration**: Admin configuration via existing settings system
- **Telegram API Integration**: Direct file upload via python-telegram-bot library
- **Error Classification**: Comprehensive handling of all Telegram API error types
- **Progress Integration**: ExportProgressTracker with file delivery status updates
- **Logging Integration**: UserInteractionLogger for administrative monitoring and audit trails
- **Resource Management**: Dedicated file cleanup utilities with exception-safe patterns

### Save/Cancel APIs

#### Save Changes API
**Trigger**: "Сохранить изменения" button
**Behavior**: Commits all field changes to Airtable via repository `update_by_id()`
**Response**: Success confirmation with updated participant display

```
✅ Успешно!
Участник успешно обновлен.

[Назад к поиску]
```

#### Cancel Changes API
**Triggers**: "Отмена" or "Назад к поиску" buttons
**Behavior**: Discards unsaved changes and returns to main menu using shared initialization
**Response**: Returns to main menu with unified welcome message and consistent state reset

**Enhanced Cancel Handler** (2025-09-09):
- Uses `initialize_main_menu_session()` for consistent state management
- Displays unified welcome message via `get_welcome_message()`
- Ensures identical behavior to start command and main menu button

## ConversationHandler State Machine

### State Definitions
```python
class EditStates:
    FIELD_SELECTION = "field_selection"      # Display participant profile with edit buttons
    TEXT_INPUT = "text_input"                # Handle text input for free text fields
    BUTTON_SELECTION = "button_selection"    # Handle inline keyboard button selections
    CONFIRMATION = "confirmation"            # Save/cancel workflow

class SearchStates:
    MAIN_MENU = 10                           # Main menu with search options
    SEARCH_MODE_SELECTION = 11               # Search type selection (name/room/floor)
    AWAITING_INPUT = 12                      # Waiting for search input
```

### Entry Point Configuration (Enhanced 2025-09-09)
**Main Menu Start Command Equivalence**:
- **CommandHandler**: `/start` command entry point
- **CallbackQueryHandler**: Main menu button callback
- **MessageHandler Entry Points** (Timeout Recovery):
  - `"🔍 Поиск участников"` text button
  - Main menu text button pattern
  - Enables conversation re-entry after timeout without `/start` command

**Shared Initialization**:
```python
# Both handlers use shared helper functions:
initialize_main_menu_session(context)  # Sets user_data keys consistently
get_welcome_message()                   # Returns unified Russian welcome message
```

### State Transition Map
```
FIELD_SELECTION:
  → TEXT_INPUT (text field edit buttons)
  → BUTTON_SELECTION (enum field edit buttons) 
  → CONFIRMATION (save/cancel buttons)
  → END (back to search)

TEXT_INPUT:
  → FIELD_SELECTION (after validation/update)
  → TEXT_INPUT (validation error retry)

BUTTON_SELECTION:
  → FIELD_SELECTION (after selection)

CONFIRMATION:
  → END (after save/cancel)

SearchStates (Fixed 2025-09-10, Enhanced 2025-01-21):
SEARCH_MODE_SELECTION:
  → WAITING_FOR_NAME ("👤 По имени" button - NAV_SEARCH_NAME handler)
  → WAITING_FOR_ROOM ("🚪 По комнате" button - NAV_SEARCH_ROOM handler)
  → WAITING_FOR_FLOOR ("🏢 По этажу" button - NAV_SEARCH_FLOOR handler)
  → END (cancel/main menu buttons)

WAITING_FOR_NAME/ROOM (Critical Fix):
  → SHOWING_RESULTS (valid user input)
  → WAITING_FOR_* (validation error retry)
  → END (cancel button - NAV_CANCEL handler)
  → MAIN_MENU (main menu button - NAV_MAIN_MENU handler)
  → SEARCH_MODE_SELECTION (back to search modes - NAV_BACK_TO_SEARCH_MODES handler)

WAITING_FOR_FLOOR (Enhanced with Callback Integration 2025-01-21):
  → SHOWING_RESULTS (valid user input OR floor selection callback)
  → WAITING_FOR_FLOOR (validation error retry)
  → FLOOR_DISCOVERY_DISPLAY (floor_discovery callback)
  → END (cancel button - NAV_CANCEL handler)
  → MAIN_MENU (main menu button - NAV_MAIN_MENU handler)
  → SEARCH_MODE_SELECTION (back to search modes - NAV_BACK_TO_SEARCH_MODES handler)
  
  Callback Handlers in WAITING_FOR_FLOOR state:
  - CallbackQueryHandler("^floor_discovery$") → Floor discovery button processing
  - CallbackQueryHandler("^floor_select_(\\d+)$") → Floor selection button processing
  
  Note: Navigation button text (NAV_SEARCH_*) now properly excluded from input processing
        via MessageHandler exclusion filters to prevent button text being treated as queries
```

## Error Response APIs

### Validation Error Response
```
❌ Ошибка валидации!

[Specific error message in Russian]

Попробуйте еще раз.
```

### System Error Response
```
❌ Произошла ошибка!

Не удалось обновить данные. Попробуйте позже.

[Назад к поиску]
```

## Translation API (Added 2025-01-09)

### Russian Translation Utilities
**Module**: `src/utils/translations.py`

**Purpose**: Provides consistent Russian translations for all enum values used in participant display

```python
# Department translation dictionary
DEPARTMENT_RUSSIAN: Dict[Department, str] = {
    Department.ROE: "ROE",
    Department.CHAPEL: "Капелла",
    Department.SETUP: "Подготовка",
    Department.PALANKA: "Паланка",
    Department.ADMINISTRATION: "Администрация",
    Department.KITCHEN: "Кухня",
    Department.DECORATION: "Декорация",
    Department.BELL: "Колокол",
    Department.REFRESHMENT: "Освежение",
    Department.WORSHIP: "Богослужение",
    Department.MEDIA: "Медиа", 
    Department.CLERGY: "Клир",
    Department.RECTORATE: "Ректорат"
}

# Role translation dictionary  
ROLE_RUSSIAN: Dict[Role, str] = {
    Role.CANDIDATE: "Кандидат",
    Role.TEAM: "Команда"
}

# Translation helper function
def translate_to_russian(value: Any, translation_dict: Dict) -> str:
    """Translate enum value to Russian with fallback to original value"""
    return translation_dict.get(value, str(value))
```

**Usage**: Used by room search formatting functions to ensure consistent Russian display of participant information across all interfaces.

## Floor Discovery API (New - 2025-01-20)

### Backend Floor Discovery Service
**Purpose**: Discover all floors that contain participants for interactive floor search

**Service Method**: `SearchService.get_available_floors()`
- **Returns**: `List[int]` - Numeric floors sorted ascending
- **Caching**: 5-minute TTL in-memory cache with timestamp cleanup
- **Error Handling**: API failures return empty list with logged warnings
- **Performance**: 10-second timeout with graceful fallback

**Implementation Details**:
```python
# Service layer method
async def get_available_floors(self) -> List[int]:
    """Get list of floors that have participants."""
    try:
        return await self.repository.get_available_floors()
    except Exception as e:
        logger.warning(f"Failed to get available floors: {e}")
        return []
```

**Repository Interface**:
```python
# Abstract repository method
async def get_available_floors(self) -> List[int]:
    """Return unique numeric floors that have at least one participant."""
    raise NotImplementedError
```

**Airtable Implementation**:
- Module-level cache: `Dict[str, Tuple[float, List[int]]]` with TTL cleanup
- API optimization: Fetches only floor field data to minimize payload
- Error resilience: Returns empty list on API failures with warning logs
- Cache key: `f"{base_id}:{table_identifier}"` for multi-base support

## Statistics Collection API (Added 2025-09-29)

### Statistics Service API
**Purpose**: Efficient participant and team statistics aggregation from Airtable for daily reporting

**Core Components**:
- `StatisticsService`: Main service class for data collection and aggregation
- `DepartmentStatistics`: Pydantic model for structured statistics results
- `StatisticsError`: Custom exception for secure error handling

**Service Interface**:
```python
class StatisticsService:
    async def collect_department_statistics(self) -> DepartmentStatistics:
        """Collect participant and team statistics by department."""
```

**DepartmentStatistics Model Structure**:
```python
@dataclass
class DepartmentStatistics:
    total_participants: int                    # Total number of participants
    participants_by_department: Dict[str, int] # Department → participant count mapping
    total_teams: int                          # Total number of teams
    collection_timestamp: datetime           # When statistics were collected (UTC)
```

**Performance Characteristics**:
- **Single-Fetch Design**: Uses one optimized Airtable query to collect all data
- **In-Memory Aggregation**: Processes data locally to minimize API calls
- **Rate Limiting Compliance**: Single-call approach eliminates rate limit concerns
- **Performance Target**: Completes data collection in under 5 seconds
- **Memory Efficiency**: Prevents accumulation through optimized processing

**Service Factory Integration**:
```python
# Factory method for dependency injection
service_factory.get_statistics_service() -> StatisticsService
```

**Error Handling**:
- **StatisticsError**: Custom exception with security-conscious error messages
- **Sensitive Data Protection**: Debug-level logging for sensitive error details
- **Graceful Degradation**: Robust error recovery with meaningful user feedback

**API Usage Example**:
```python
statistics_service = service_factory.get_statistics_service()
stats = await statistics_service.collect_department_statistics()

print(f"Total participants: {stats.total_participants}")
print(f"Teams by department: {stats.participants_by_department}")
print(f"Collection time: {stats.collection_timestamp}")
```

## Data Model API

### Repository Interface Extensions (2025-09-23)

#### View-Based Data Access
```python
# New repository method for view-driven exports
async def list_view_records(self, view: str) -> List[Dict[str, Any]]:
    """
    Retrieve raw Airtable records for a specific view.

    Args:
        view: Airtable view name to pull records from

    Returns:
        List of Airtable record dictionaries with preserved field order

    Raises:
        RepositoryError: If retrieval fails
    """
```

**Implementation Details**:
- **Purpose**: Enables view-driven exports that maintain Airtable column ordering
- **Raw Data Access**: Returns unprocessed Airtable record dictionaries
- **Field Order Preservation**: Maintains exact view column structure for export alignment
- **View Support**: Works with any Airtable view (Кандидаты, РОЕ: Расписание, Чтецы: Расписание, etc.)
- **Error Handling**: Follows established repository error patterns
- **Multi-Table Support**: Available across all repository types (Participants, ROE, Bible Readers)

#### View-Aligned Export Architecture (Updated 2025-09-27)
```python
# Export utility functions for view-based ordering
def extract_headers_from_view_records(records: List[Dict[str, Any]]) -> List[str]:
    """Extract column headers from view records preserving field order."""

def order_rows_by_view_headers(rows: List[Dict[str, Any]], headers: List[str]) -> List[List[str]]:
    """Reorder data rows to match view header sequence with line numbers."""
```

**View-Based Export Features**:
- **Column Order Preservation**: Exact Airtable view column ordering maintained
- **Header Reconstruction**: Headers derived from actual view data including linked fields
- **Line Number Integration**: Sequential numbering preserved as first column
- **Graceful Fallback**: Automatic repository filtering when views unavailable
- **Multi-Table Coverage**: Supports Participants, ROE, and Bible Readers exports

### Participant Model (Internal)
```python
class Participant(BaseModel):
    id: str
    full_name_ru: str          # Required
    full_name_en: Optional[str] = None
    church: Optional[str] = None
    country_and_city: Optional[str] = None
    gender: Optional[Gender] = None     # M/F
    size: Optional[Size] = None         # XS-3XL
    role: Optional[Role] = None         # CANDIDATE/TEAM
    department: Optional[Department] = None  # 13 options
    contact_information: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None  # Paid/Partial/Unpaid
    payment_amount: Optional[int] = None
    payment_date: Optional[str] = None  # YYYY-MM-DD
    submitted_by: Optional[str] = None
    room_number: Optional[str] = None   # Room assignment (alphanumeric)
    floor: Optional[Union[int, str]] = None  # Floor number or name
    date_of_birth: Optional[date] = None    # Date of birth (ISO date format) - Fixed 2025-09-11
    age: Optional[int] = None               # Age in years (0-120 range) - Fixed 2025-09-11
```

### Field Mapping (Airtable) - Updated 2025-09-10
```python
# Internal field → Airtable field ID mapping (Integration tested)
FIELD_MAPPINGS = {
    "full_name_ru": "fldXXXXXXXXXXXXXX",
    "full_name_en": "fldYYYYYYYYYYYYYY", 
    "gender": "fldZZZZZZZZZZZZZZ",
    "room_number": "fldJTPjo8AHQaADVu",  # RoomNumber field (TEXT type, alphanumeric)
    "floor": "fldlzG1sVg01hsy2g",        # Floor field (Union[int, str])
    "date_of_birth": "fld1rN2cffxKuZh4i",  # DateOfBirth field (DATE type, ISO format)
    "age": "fldZPh65PIekEbgvs",           # Age field (NUMBER type, 0-120 range)
    # ... etc for all fields
}
```

**Schema Validation**: Field IDs verified through comprehensive integration testing with actual Airtable API calls. Room number field supports alphanumeric values ("101", "A1", "Conference"), Floor field supports both numeric and string values (1, "Ground").

### Enum Definitions
```python
class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    
class Role(str, Enum):
    CANDIDATE = "CANDIDATE"
    TEAM = "TEAM"
    
class PaymentStatus(str, Enum):
    PAID = "Paid"
    PARTIAL = "Partial" 
    UNPAID = "Unpaid"
```

## Schedule Formatting API (Enhanced 2025-09-28)

### Enhanced Schedule Formatter
**Purpose**: Advanced schedule formatting with Russian localization and intelligent section detection

**Module**: `src/utils/schedule_formatter.py`

**Core Features**:
- **Russian Audience Translation**: Automatic translation of audience types
  - `All` → `Все`, `Team` → `Тимы`, `Candidates` → `Кандидаты`
- **Section Header Detection**: Smart parsing of section markers from descriptions
- **Multi-line Description Support**: Proper formatting of detailed event descriptions
- **Day Label Integration**: Support for human-readable day headers
- **Hierarchical Visual Structure**: Enhanced bullet point formatting for improved readability

**Audience Translation API**:
```python
AUDIENCE_ALIASES = {
    "all": "Все",
    "team": "Тимы",
    "candidates": "Кандидаты",
    "leadership": "Тимы",
    "clergy": "Тимы",
    # ... additional aliases
}

def _translate_audience(value: Optional[str]) -> Optional[str]:
    """Translate audience type to Russian with fallback."""
```

**Section Detection API**:
```python
SECTION_MARKERS = (
    "section:", "секция:", "раздел:",
    "block:", "блок:"
)

def _match_section_header(line: str) -> Optional[str]:
    """Extract section name from description line."""
```

**Format Output Example**:
```
📅 2025-11-16 — День выпускного

🕔 Утро
• 05:30 Подъём ТМ — Тимы
  ◦ Начало дня
• 06:00 Молитва в часовне — Тимы
• 06:30 Первый звонок — Все

📦 Сборы
• 10:40 Сбор вещей — Все
  ◦ Подготовка к выезду
• 11:00 Вещи в часовню — Все

🎤 Программа
• 11:10 Восхваление — Все
• 11:30 #11 «Христианская атмосфера» — Тимы
```

**API Methods**:
```python
def format_schedule_day(date_value: dt.date, entries: Iterable[ScheduleEntry]) -> str:
    """Return formatted schedule string with RU-friendly layout."""

def format_time(t: dt.time) -> str:
    """Format time in HH:MM format."""

def _format_time_range(start: dt.time, end: Optional[dt.time]) -> str:
    """Format time range with proper separator."""
```

**Enhanced Formatting Features**:
- **Time Range Formatting**: Proper en-dash separator (`–`) for time ranges
- **Bullet Point Hierarchy**: Primary items use `•`, details use `◦`
- **Section Grouping**: Events grouped under section headers automatically
- **Empty Day Handling**: Graceful message when no events exist
- **Multi-line Support**: Proper formatting of detailed descriptions with bullet points
- **Sorting Logic**: Events sorted by start time, then by order field

## Error Handling and Message Templates (2025-09-05)

### Centralized Error Handling
Error handling has been enhanced with standardized message templates located in `src/bot/messages.py` providing consistent user experience.

### Error Response Templates
```python
# Room validation error
ROOM_VALIDATION_ERROR = "Пожалуйста, введите корректный номер комнаты"

# Floor validation error  
FLOOR_VALIDATION_ERROR = "Пожалуйста, введите корректный номер этажа"

# Empty results
EMPTY_RESULTS = "По заданному запросу ничего не найдено"

# API errors
API_ERROR = "Произошла ошибка. Попробуйте позже"
```

### Integration Testing Coverage
- **28+ Integration Tests**: Comprehensive end-to-end testing across 3 test files
- **Performance Validation**: All operations tested to complete within 3 seconds
- **Schema Validation**: Field mapping verification with production Airtable schema
- **Error Scenario Coverage**: API failures, invalid inputs, empty results, network timeouts

## Rate Limiting & Performance

### Airtable API Constraints
- **Rate Limit**: 5 requests per second
- **Request Timeout**: 30 seconds (enhanced from 10 seconds)
- **Retry Strategy**: 3 retry attempts with exponential backoff on rate limit errors

### Bot Response Performance (Validated 2025-09-05)
- **Handler Response**: < 2 seconds
- **Field Update**: < 3 seconds (including Airtable call) - **Integration tested**
- **Search Results**: < 3 seconds for complex queries - **Performance validated**
- **Room Search**: < 3 seconds for alphanumeric room queries
- **Floor Search**: < 3 seconds for multi-room floor queries with grouping
- **CSV Export Performance**: < 30 seconds for datasets up to 1500 participants
- **Progress Notifications**: 2-second throttling prevents rate limit violations

### Memory Management
- **Conversation Context**: < 1MB per user session
- **State Persistence**: In-memory for active conversations
- **Data Caching**: Participant data cached during editing session
- **Export Memory**: Streaming CSV generation prevents memory exhaustion for large datasets
- **File Cleanup**: Automatic temporary file removal after export completion
