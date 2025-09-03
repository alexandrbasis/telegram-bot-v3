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
Кто подал: Мария Иванова

[Изменить имя (русское)] [Изменить имя (английское)]
[Изменить церковь] [Изменить местоположение]
[Изменить пол] [Изменить размер]
[Изменить роль] [Изменить Департамент]
[Изменить контакты] [Изменить статус платежа]
[Изменить сумму] [Изменить дату платежа]
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
**Behavior**: Discards unsaved changes and returns to search results
**Response**: Returns to previous search results page with context preserved

## ConversationHandler State Machine

### State Definitions
```python
class EditStates:
    FIELD_SELECTION = "field_selection"      # Display participant profile with edit buttons
    TEXT_INPUT = "text_input"                # Handle text input for free text fields
    BUTTON_SELECTION = "button_selection"    # Handle inline keyboard button selections
    CONFIRMATION = "confirmation"            # Save/cancel workflow
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
```

### Field Mapping (Airtable)
```python
# Internal field → Airtable field ID mapping
FIELD_MAPPINGS = {
    "full_name_ru": "fldXXXXXXXXXXXXXX",
    "full_name_en": "fldYYYYYYYYYYYYYY", 
    "gender": "fldZZZZZZZZZZZZZZ",
    # ... etc for all 13 fields
}
```

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

## Rate Limiting & Performance

### Airtable API Constraints
- **Rate Limit**: 5 requests per second
- **Request Timeout**: 10 seconds
- **Retry Strategy**: Exponential backoff on rate limit errors

### Bot Response Performance
- **Handler Response**: < 2 seconds
- **Field Update**: < 3 seconds (including Airtable call)
- **Search Results**: < 5 seconds for complex queries

### Memory Management
- **Conversation Context**: < 1MB per user session
- **State Persistence**: In-memory for active conversations
- **Data Caching**: Participant data cached during editing session
