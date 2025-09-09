# Bot Commands Reference

## Search Commands

### /search [query] and Search Button
Search for participants by name (Russian or English), nickname, or other details. Available via command or main menu "🔍 Поиск участников" button.

**Main Menu Button Equivalence** (Enhanced 2025-09-09):
- Main Menu button provides identical functionality to `/start` command
- **Shared Initialization**: Both use `initialize_main_menu_session()` and `get_welcome_message()` helpers
- **Consistent Welcome**: Same Russian message: "Добро пожаловать в бот Tres Dias! 🙏\n\nВыберите тип поиска участников."
- **Entry Point Recovery**: Text button handlers enable conversation re-entry after timeout without manual `/start`

### /search_room [room_number]
Search for participants assigned to a specific room number with enhanced structured Russian results. Supports alphanumeric room identifiers.

**Usage Examples:**
- `/search_room 205` - Find participants in room 205
- `/search_room A1` - Find participants in room A1
- `/search_room Conference` - Find participants in Conference room

**Enhanced Features (2025-01-09):**
- **Structured Russian Results**: Displays participant information with role, department, and floor translations
- **Complete Translation Support**: All departments and roles displayed in Russian using comprehensive translation mappings
- **Rich Formatting**: Shows participant names (Russian/English), translated role/department, and floor context
- **Input Validation**: Validates room number format with user-friendly Russian error messages
- **Russian Interface**: Complete Russian language support throughout the interaction
- **Empty Room Handling**: Shows appropriate message when room is empty
- **Navigation**: Reply keyboard for easy mode switching between search types

**Example Structured Output:**
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
```

### /search_floor [floor_number]
Search for participants on a specific floor with room-by-room breakdown.

**Usage Examples:**
- `/search_floor 2` - Find all participants on floor 2
- `/search_floor 1` - Find all participants on floor 1
- `/search_floor Ground` - Find participants on ground floor

**Features:**
- **Room Grouping**: Results organized by room with participant counts
- **Smart Sorting**: Numeric rooms sorted numerically, then alphabetically
- **Floor Overview**: Shows total participant count and room distribution
- **Russian Interface**: Complete Russian language support with localized messages
- **Empty Floor Handling**: Shows appropriate message when floor is empty
- **Navigation**: Reply keyboard for search mode selection

**Button Functionality**: The search button uses ConversationHandler with proper state management (SearchStates: 10-12) and per_message configuration to ensure reliable button response.

**Usage Examples:**
- `/search Иван` - Find participants with "Иван" in their name
- `/search John` - Find participants with "John" in their name  
- `/search церковь` - Find participants by church name

**Enhanced Features:**
- **Language Detection**: Automatically detects Cyrillic vs Latin script
- **Multi-field Search**: Searches Russian names, English names, nicknames, church, location
- **Fuzzy Matching**: Finds similar names even with typos
- **Match Quality Labels**: Shows search confidence (Отличное совпадение, Хорошее совпадение, Частичное совпадение)
- **Interactive Selection**: Click participant buttons to view/edit details
- **Search Mode Selection**: Reply keyboard with buttons for Name/Room/Floor search modes

**Search Results Display:**
- Shows up to 10 participants per page
- Displays: Name (Russian/English), Role, Department, Match Quality
- "Подробнее" (Details) button for each participant
- Pagination with "Назад" (Back) and "Далее" (Next) buttons

## Participant Editing Interface

### Participant Selection
After searching, click "Подробнее" (Details) on any participant to access the comprehensive editing interface.

**Complete Participant Profile Display:**
- Full Name (Russian): [Name]
- Full Name (English): [Name] 
- Church: [Church]
- Country/City: [Location]
- Gender: [М/Ж]
- Size: [XS-3XL]
- Role: [Кандидат/Команда]
- Department: [Department]
- Contact: [Contact Info]
- Payment Status: [Оплачено/Частично/Не оплачено]
- Payment Amount: [Amount]
- Payment Date: [Date]
- Submitted By: [Name]

### Enhanced Field Editing Display

**Complete Participant Context After Edits**: After successfully updating any field, the bot displays the complete participant profile with all current information, including the newly updated field. This provides users with full context and confirmation of changes without requiring navigation back to search results.

**Display Features**:
- Uses the same rich formatting as initial search results for consistency
- Shows all participant fields in their current state
- Includes the updated field value within the complete profile
- Maintains the same edit buttons for continued editing

### Field Editing Commands

Each participant field can be edited through dedicated "Изменить [Field]" buttons:

#### Button-Based Fields (Immediate Selection)

1. **"Изменить пол" (Edit Gender)**
   - Options: "Мужской" (M), "Женский" (F)
   - Click button → Select option → Complete participant display with updated information

2. **"Изменить размер" (Edit Size)**  
   - Options: XS, S, M, L, XL, XXL, 3XL
   - Click button → Select size → Complete participant display with updated information

3. **"Изменить роль" (Edit Role)**
   - Options: "Кандидат" (Candidate), "Команда" (Team)
   - Click button → Select role → Complete participant display with updated information

4. **"Изменить Департамент" (Edit Department)**
   - Options: ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate
   - Click button → Select department → Complete participant display with updated information

5. **"Изменить статус платежа" (Edit Payment Status)**
   - Options: "Оплачено" (Paid), "Частично" (Partial), "Не оплачено" (Unpaid)
   - Click button → Select status → Complete participant display with updated information

#### Text Input Fields (Prompt Workflow)

1. **"Изменить имя (русское)" (Edit Russian Name)** ⭐ *Required*
   - Click button → Bot prompts: "Отправьте новое имя на русском"
   - Type new name → Validation (required, min length 1) → Complete participant display with updated information

2. **"Изменить имя (английское)" (Edit English Name)**
   - Click button → Bot prompts: "Отправьте новое имя на английском" 
   - Type new name → Complete participant display with updated information

3. **"Изменить церковь" (Edit Church)**
   - Click button → Bot prompts: "Отправьте название церкви"
   - Type church name → Complete participant display with updated information

4. **"Изменить местоположение" (Edit Location)**
   - Click button → Bot prompts: "Отправьте страну и город"
   - Type location → Complete participant display with updated information

5. **"Изменить контакты" (Edit Contact)**
   - Click button → Bot prompts: "Отправьте контактную информацию"
   - Type contact info → Complete participant display with updated information

6. **"Изменить кто подал" (Edit Submitted By)**
   - Click button → Bot prompts: "Отправьте имя того, кто подал"
   - Type submitter name → Complete participant display with updated information

#### Special Validation Fields

1. **"Изменить сумму" (Edit Payment Amount)**
   - Click button → Bot prompts: "Отправьте сумму платежа (только цифры)"
   - Type amount → Validation (integer ≥ 0) → Complete participant display with updated information
   - Error message if invalid: "Ошибка: Сумма должна быть положительным числом"

2. **"Изменить дату платежа" (Edit Payment Date)**
   - Click button → Bot prompts: "Отправьте дату в формате ГГГГ-ММ-ДД"
   - Type date → Validation (YYYY-MM-DD format) → Complete participant display with updated information
   - Error message if invalid: "Ошибка: Дата должна быть в формате ГГГГ-ММ-ДД"

### Save/Cancel Actions

#### Save Confirmation Workflow
- **"Сохранить изменения" (Save Changes)**: Displays confirmation screen showing all pending changes
- **Confirmation Screen**: Shows "Current Value → **New Value**" format for all modified fields
- **"Подтвердить сохранение" (Confirm Save)**: Commits all changes to Airtable
- **Save Success**: Displays complete updated participant information using format_participant_result() with all applied changes, providing full context instead of simple confirmation message

#### Cancel and Navigation
- **"Отмена" (Cancel)**: Discards all changes and returns to main menu using shared initialization helpers for consistent state reset
- **"Назад к поиску" (Back to Search)**: Returns to search results without saving
- **"Вернуться в главное меню" (Return to Main Menu)**: Cancel confirmation option

**Enhanced Cancel Handler** (2025-09-09):
- Uses shared `initialize_main_menu_session()` and `get_welcome_message()` for consistent state management
- Provides same unified welcome message as start command and main menu button
- Ensures proper state reset with search_results clearing and force_direct_name_input flag setting

#### Error Handling and Retry
- **Save Failure**: Automatic retry buttons appear on Airtable update errors
- **"Попробовать снова" (Try Again)**: Retry failed save operation preserving changes
- **Error Messages**: User-friendly Russian error messages with actionable instructions
- **Data Preservation**: User changes maintained during retry operations
- **Display Error Recovery**: Enhanced error handling prevents silent display failures during field editing with comprehensive logging (REGRESSION markers) and meaningful user feedback
- **Context Loss Handling**: Graceful degradation when participant context is lost, providing clear error messages and recovery guidance

## Search Mode Navigation

### Search Mode Selection Interface
Users can switch between different search modes using a reply keyboard interface:

**Available Modes:**
- **"🔍 Поиск по имени" (Name Search)**: Traditional participant name search
- **"🏠 Поиск по комнате" (Room Search)**: Search by room number  
- **"🏢 Поиск по этажу" (Floor Search)**: Search by floor with room breakdown

**Navigation Flow:**
1. User clicks main menu "🔍 Поиск участников" button
2. Bot displays search mode selection keyboard
3. User selects desired search mode
4. Bot prompts for appropriate input (name, room number, or floor)
5. Results displayed with option to return to mode selection

## Room and Floor Search Results

### Room Search Display
```
🏠 Комната 205:

👤 Иван Петров (Кандидат)
   Церковь: Храм Христа Спасителя
   
👤 Мария Иванова (Команда)
   Департамент: ROE
   
Всего найдено: 2 участника
```

### Floor Search Display
```
🏢 Этаж 2:

🏠 Комната 201 (3 участника):
   • Иван Петров (Кандидат)
   • Мария Иванова (Команда)
   • Сергей Сидоров (Кандидат)

🏠 Комната 205 (2 участника):
   • Анна Козлова (Команда)
   • Петр Смирнов (Кандидат)

Всего на этаже: 5 участников в 2 комнатах
```

## Conversation Timeout Handling

### Automatic Session Management
All conversations include automatic timeout handling to prevent users from getting stuck in stale states:

- **Timeout Period**: Configurable via `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` environment variable (default: 30 minutes)
- **Timeout Message**: "Сессия истекла, начните заново" (Session expired, start again)
- **Recovery Option**: "Вернуться в главное меню" button returns user to main menu
- **State Cleanup**: Automatic conversation context cleanup prevents memory leaks
- **Universal Coverage**: Applied to all conversation types (search, edit, room/floor search)

### Timeout Scenarios
- **Search Conversations**: User searches but doesn't interact with results
- **Edit Workflows**: User enters editing mode but doesn't complete changes
- **Room/Floor Search**: User initiates location search but doesn't provide input
- **Any Conversation State**: Timeout applies to all states equally

### User Recovery Flow
1. User becomes inactive during any conversation
2. After timeout period (default 30 minutes), bot displays timeout message
3. User clicks "Вернуться в главное меню" button
4. User returns to main menu and can start fresh conversation
5. Previous conversation context is completely cleaned up

## Error Handling

### Standardized Error Messages (2025-09-05)
Error handling has been enhanced with centralized message templates located in `src/bot/messages.py` providing consistent, user-friendly Russian error messages across all search functionality.

### Validation Errors
- Clear Russian error messages for invalid input
- Prompts user to retry with correct format
- Field-specific validation rules enforced
- **Room Number Validation**: "Пожалуйста, введите корректный номер комнаты (например: 205, A1, Conference)"
- **Floor Number Validation**: "Пожалуйста, введите корректный номер этажа (например: 1, 2, Ground)"
- **Empty Results**: "По заданному запросу ничего не найдено"

### System Errors  
- Graceful handling of Airtable API errors
- Rate limiting protection (5 requests/second)
- Connection timeout recovery with 30-second timeout and 3 retry attempts
- **API Error Messages**: "Произошла ошибка. Попробуйте позже" with retry guidance
- Empty room/floor result handling with user-friendly messages

### Integration Testing and Performance
- **Response Time Validation**: All searches validated to complete within 3 seconds
- **Comprehensive Error Scenario Testing**: 28+ integration tests covering API failures, invalid inputs, and edge cases
- **Production Readiness**: Error handling tested against real Airtable field mappings and schema validation

## Usage Flow Examples

### Name Search Flow
1. User types: `/search Иван Петров`
2. Bot shows search results with "Подробнее" buttons
3. User clicks "Подробнее" on desired participant
4. Bot displays complete participant profile with 13 edit buttons
5. User clicks "Изменить роль" (Edit Role)
6. Bot shows role options: "Кандидат", "Команда"
7. User selects "Команда"
8. Bot displays complete participant profile with updated role information
9. User clicks "Сохранить изменения" to review changes
10. **Confirmation Screen**: Shows "Роль: Кандидат → **Команда**"
11. User clicks "Подтвердить сохранение" to commit changes
12. Bot saves to Airtable and confirms: "Участник успешно обновлен"
13. User returns to search results with context preserved

### Room Search Flow
1. User clicks "🔍 Поиск участников" in main menu
2. Bot displays search mode selection keyboard
3. User clicks "🏠 Поиск по комнате" (Room Search)
4. Bot prompts: "Введите номер комнаты для поиска:"
5. User types: `205`
6. Bot displays room search results with participant list
7. User can click "Подробнее" to view/edit participant details
8. Navigation options: return to search mode selection or main menu

### Floor Search Flow
1. User types: `/search_floor 2`
2. Bot displays floor overview with room-by-room breakdown
3. Results show: room numbers, participant counts, and participant names
4. User can navigate to specific participants for detailed view
5. Navigation options: search other floors or return to main menu

### Error Recovery Flow

1. User attempts to save changes
2. **Airtable Error Occurs** (network/API issue)
3. Bot displays: "Ошибка при сохранении данных в Airtable" 
4. **Retry Button**: "Попробовать снова" appears automatically
5. User clicks retry → Bot attempts save again with preserved changes
6. Success: Changes saved and user notified
7. Failure: Retry option remains available

### Timeout Recovery Flow

1. User starts participant search: `/search Иван`
2. Bot shows search results with "Подробнее" buttons
3. **User becomes inactive** (no interaction for 30 minutes)
4. **Timeout Triggers**: Bot displays "Сессия истекла, начните заново"
5. **Recovery Button**: "Вернуться в главное меню" button appears
6. User clicks recovery button → Returns to main menu with clean state
7. User can start fresh conversation without any residual context
8. **Alternative**: User can also ignore timeout message and use any main menu command
