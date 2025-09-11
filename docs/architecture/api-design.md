# API Design

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

## Data Model API

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

### Memory Management
- **Conversation Context**: < 1MB per user session
- **State Persistence**: In-memory for active conversations
- **Data Caching**: Participant data cached during editing session
