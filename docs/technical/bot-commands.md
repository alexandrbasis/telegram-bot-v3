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
Search for participants on a specific floor with room-by-room breakdown. Features interactive floor discovery for enhanced user experience.

**Usage Examples:**
- `/search_floor 2` - Find all participants on floor 2
- `/search_floor 1` - Find all participants on floor 1
- `/search_floor Ground` - Find participants on ground floor

### Department-Based Filtering (Enhanced 2025-01-21)
Complete department filtering feature enabling users to navigate from team selection to department-specific participant lists with enhanced navigation and Russian localization.

**Complete Workflow Features:**
- **Team Selection Integration**: Users navigate from "Team members" selection to department filtering interface
- **Department Selection Interface**: 15-option keyboard (13 departments + "All participants" + "No department")
- **Filtered Results**: Department-specific participant lists with chief-first sorting
- **Navigation Context**: Department filter state preserved through pagination and navigation
- **Back Navigation**: Returns to department selection (not role selection) for intuitive workflow
- **Russian Interface**: All department names displayed in Russian with accurate translations
- **Chief Identification**: Department chiefs marked with crown emoji (👑) for visual recognition
- **Chief-First Ordering**: Department chiefs automatically appear at top of all filtered lists
- **Complete Coverage**: All 13 predefined departments accessible through intuitive selection
- **Special Options**: "Все участники" for complete lists, "Без департамента" for unassigned members
- **Server-Side Filtering**: Efficient Airtable queries reduce response times and data transfer
- **Error Handling**: Graceful handling of empty departments and invalid callbacks

**Enhanced Interactive Features (2025-01-21):**
- **Interactive Floor Discovery**: "Показать доступные этажи" button reveals available floors without guessing
- **Floor Selection Buttons**: Available floors display as clickable "Этаж 1", "Этаж 2" buttons for direct selection
- **Dual Input Methods**: Users can discover floors via button or manually enter floor numbers
- **Enhanced Guidance**: Clear instructions show both button interaction and manual input options in Russian
- **Error Fallback**: If discovery fails, users get manual input guidance: "Произошла ошибка. Пришлите номер этажа цифрой."

**Core Features:**
- **Room Grouping**: Results organized by room with participant counts
- **Smart Sorting**: Numeric rooms sorted numerically, then alphabetically
- **Floor Overview**: Shows total participant count and room distribution
- **Russian Interface**: Complete Russian language support with localized messages
- **Empty Floor Handling**: Shows appropriate message when floor is empty
- **Navigation**: Reply keyboard for search mode selection

**Button Functionality**: The search button uses ConversationHandler with proper state management (SearchStates: 10-12) and per_message configuration to ensure reliable button response.

**Interactive Floor Discovery Workflow (2025-01-21):**
1. User clicks "🏢 По этажу" from search mode selection
2. Bot displays enhanced prompt: "Выберите этаж из списка или пришлите номер этажа цифрой:" with "Показать доступные этажи" button
3. **Interactive Discovery Path**: User clicks discovery button → Bot shows available floors as "Этаж 1", "Этаж 2" buttons (3 per row)
4. **Direct Selection**: User clicks floor button → Bot triggers floor search automatically
5. **Manual Input Path**: User types floor number → Bot processes search as before
6. **Error Recovery**: API failures show helpful fallback message with manual input guidance

**Conversation Flow Integration (2025-01-21):**
- **Callback Handler Registration**: Floor discovery handlers properly registered in ConversationHandler with patterns `^floor_discovery$` and `^floor_select_(\\d+)$` in WAITING_FOR_FLOOR state
- **State Transition Validation**: Complete conversation flow integration validated through comprehensive testing
- **Backward Compatibility**: Traditional numeric floor input continues working alongside interactive features without interference
- **Error Recovery Scenarios**: Comprehensive error handling for API failures, callback timeouts, and empty results with proper user guidance
- **Performance Validation**: All callback responses validated to complete within acceptable time limits

## Get List Commands

### Get List Button and Bulk Access
Access pre-filtered participant lists by role for quick bulk viewing. Available via main menu "📋 Получить список" button alongside the search functionality.

**Main Menu Integration**: The Get List button provides instant access to categorized participant lists without requiring search queries, ideal for administrative tasks and logistics planning.

**Enhanced Usage Flow with Department Filtering:**
1. User clicks "📋 Получить список" from main menu
2. Bot displays role selection: "👥 Команда" (Team) or "🎯 Кандидаты" (Candidates)
3. User selects "👥 Команда" (Team) → Bot displays department filtering options with 15-button keyboard
4. User selects specific department or "Все участники" (All participants) option
5. Bot displays paginated numbered list with filtered participants (chiefs highlighted with 👑)
6. Navigation with "◀️ Назад", "▶️ Далее", "🔄 Выбор департамента", and "🏠 Главное меню" buttons
7. **Context Preservation**: Department filter maintained through pagination
8. **Back Navigation**: "🔄 Выбор департамента" returns to department selection for easy filtering changes
9. **Direct Candidate Access**: Selecting "🎯 Кандидаты" bypasses department filtering and shows all candidates directly

### Team Members List
View complete list of all team members with organizational details and department filtering for logistics and planning.

**Enhanced Department Filtering Features:**
- **Department Selection Workflow**: Navigate from team selection to 15-option department filtering interface
- **Server-side Role Filtering**: Efficient Airtable filtering by role="TEAM"
- **Department-Specific Lists**: Filter by any of 13 departments or view all participants
- **Chief Identification**: Department chiefs marked with crown emoji (👑) for organizational structure
- **Chief-First Ordering**: Department chiefs automatically appear first in all filtered lists
- **Russian Department Names**: All departments displayed in Russian with accurate translations
- **Special Filtering Options**: "Все участники" (all team members) and "Без департамента" (unassigned)
- **Navigation Context**: Department filter preserved through pagination and navigation
- **Numbered List Format**: Sequential numbering (1., 2., 3.) for easy reference
- **Organizational Information**: Full name (Russian), department, church affiliation
- **Pagination**: Dynamic page size with Telegram 4096-character message limit handling
- **Offset-based Navigation**: Ensures no participants are skipped during pagination

**Display Example:**
```
**Список участников команды - Setup** (элементы 1-20 из 45)

1. **👑 Иван Петров** (Руководитель отдела)
   🏢 Отдел: Setup
   ⛪ Церковь: Храм Христа Спасителя

2. **Мария Иванова**
   🏢 Отдел: Setup
   ⛪ Церковь: Церковь Святого Николая

... (continues with remaining participants)
```

### Candidates List
View complete list of all candidates with organizational context for administrative planning.

**Features:**
- **Server-side Role Filtering**: Efficient Airtable filtering by role="CANDIDATE"
- **Department Filtering**: Enhanced filtering capabilities with department selection interface
- **Chief Identification**: Department chiefs marked with crown emoji (👑) for priority management
- **Chief-First Ordering**: Department chiefs appear first in all filtered department lists
- **Identical Format**: Same numbered list format and information display as team list
- **Consistent Navigation**: Same pagination and navigation controls
- **Administrative Focus**: Designed for candidate management and organizational planning

**Display Example:**
```
**Список кандидатов** (элементы 1-18 из 32)

1. **Анна Козлова**
   🏢 Отдел: —
   ⛪ Церковь: Церковь Покрова

2. **Петр Смирнов**
   🏢 Отдел: —
   ⛪ Церковь: Собор Александра Невского

... (continues with remaining participants)
```

### Pagination and Navigation
Lists support robust pagination designed to handle large datasets without losing participants.

**Navigation Controls:**
- **"◀️ Назад" (Previous)**: Navigate to previous page of results
- **"▶️ Далее" (Next)**: Navigate to next page of results  
- **"🏠 Главное меню" (Main Menu)**: Return to main menu and exit list view

**Technical Features:**
- **Offset-based Pagination**: Prevents participant skipping when content is trimmed for message length limits
- **Dynamic Page Sizing**: Automatically adjusts number of participants per page to stay under 4096 character limit
- **Continuity Guarantee**: Ensures all participants are accessible across pages without gaps or duplicates
- **State Management**: Maintains current position and role context during navigation

### Empty Result Handling
Graceful handling when no participants exist for selected role.

**Empty Team List:**
```
Участники не найдены.
```

**Empty Candidate List:**
```
Участники не найдены.
```

### Use Case Examples

#### Event Logistics Planning
**Scenario**: Event organizer needs clothing sizes for all team members
1. Click "📋 Получить список" → "👥 Команда"
2. Review complete team list with sizes displayed for each participant
3. Navigate through pages to access all 45+ team members
4. Export or reference information for logistics planning

#### Candidate Review Process  
**Scenario**: Review committee needs complete candidate roster
1. Click "📋 Получить список" → "🎯 Кандидаты"
2. View numbered list of all candidates with church affiliations
3. Use pagination to systematically review all candidates
4. Reference participant numbers for committee discussions

#### Administrative Tasks
**Scenario**: Quick access to specific participant categories without search queries
1. Instant access via main menu button (2-click workflow)
2. No search terms or filters required - complete category view
3. Efficient server-side filtering prevents loading unnecessary data
4. Consistent formatting for easy scanning and reference

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
- Displays: Name (Russian/English), Role, Department, Demographics (Date of Birth, Age), Match Quality
- "Подробнее" (Details) button for each participant
- Pagination with "Назад" (Back) and "Далее" (Next) buttons
- Enhanced display format includes demographic info: "Date of Birth: YYYY-MM-DD | Age: XX years" (or "N/A" for missing data)

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
- 🎂 Date of Birth: [YYYY-MM-DD or Не указано] *Fixed display issue 2025-09-11*
- 🔢 Age: [XX years or Не указано] *Fixed display issue 2025-09-11*
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

3. **"Изменить дату рождения" (Edit Date of Birth)** 🔧 *Fixed 2025-09-11*
   - Click button → Bot prompts: "📅 Введите дату рождения в формате ГГГГ-ММ-ДД (например: 1990-05-15):"
   - Type date → Validation (YYYY-MM-DD format) → Complete participant display with updated information
   - **Clearing Support**: Send only whitespace to clear field (displays "Не указано")
   - **Fixed JSON Serialization**: Resolves "Object of type date is not JSON serializable" error
   - Error message if invalid: "❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД (например: 1990-05-15)" + InfoMessages guidance

4. **"Изменить возраст" (Edit Age)** 🔧 *Fixed 2025-09-11*
   - Click button → Bot prompts: "🔢 Введите возраст (от 0 до 120):"
   - Type age → Validation (0-120 integer range) → Complete participant display with updated information
   - **Clearing Support**: Send only whitespace to clear field (displays "Не указано")
   - **Fixed Display**: Resolves missing age field in participant reconstruction after editing
   - Error messages if invalid: "❌ Возраст должен быть от 0 до 120" or "❌ Возраст должен быть числом" + InfoMessages guidance

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
- **"👤 По имени" (Name Search)**: Traditional participant name search
- **"🚪 По комнате" (Room Search)**: Search by room number  
- **"🏢 По этажу" (Floor Search)**: Search by floor with room breakdown

**Navigation Flow:**
1. User clicks main menu "🔍 Поиск участников" button
2. Bot displays search mode selection keyboard
3. User selects desired search mode by clicking the appropriate button
4. Bot prompts for appropriate input (name, room number, or floor)
5. Results displayed with option to return to mode selection

**Critical Fix (2025-09-10)**: Search mode buttons now correctly transition to input waiting states instead of being processed as search queries. The buttons "👤 По имени", "🚪 По комнате", and "🏢 По этажу" properly trigger prompt messages and wait for user input rather than immediately searching for the button text itself.

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

### Room Search Flow (Enhanced 2025-01-15)
1. User clicks "🔍 Поиск участников" in main menu
2. Bot displays search mode selection keyboard
3. User clicks "🏠 Поиск по комнате" (Room Search)
4. Bot prompts: "Введите номер комнаты для поиска:" (single clean prompt)
5. User types: `205` OR clicks "❌ Отмена" to return to main menu
6. Bot displays room search results with participant list
7. User can click "Подробнее" to view/edit participant details
8. Navigation options: return to search mode selection or main menu

**Enhanced User Experience (2025-01-15)**:
- **Single Clean Prompt**: Room search mode sends exactly one message asking for room number
- **Proper Cancel Support**: Cancel button works correctly during room input without validation errors
- **No Duplicate Messages**: Eliminated duplicate prompts that previously confused users
- **Consistent Pattern**: Room search now mirrors floor search behavior for UI consistency

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

## Data Export Commands

### /export
Interactive export conversation flow for administrative data export. Available to authorized administrators only. Converts the direct export command into a conversation with 6 targeted export options.

**Admin-Only Access Control**:
- Command validates user authorization using `auth_utils.is_admin_user()` function
- Unauthorized users receive appropriate error message: "Доступ запрещён. Эта команда доступна только администраторам."
- Admin user IDs configured via `ADMIN_USER_IDS` environment variable
- Comprehensive logging for security monitoring and access control

**Interactive Export Conversation Flow**:
1. User (admin) types: `/export`
2. Bot validates admin access and displays interactive selection menu
3. **Export Selection Menu**: 6 export options with Russian localization:
   - "Экспорт всех данных" (Export All) - Complete participant database
   - "Экспорт команды" (Export Team) - Team members only
   - "Экспорт кандидатов" (Export Candidates) - Candidates only
   - "Экспорт по департаменту" (Export by Department) - Department-specific export
   - "Экспорт Bible Readers" (Export Bible Readers) - Bible reading assignments
   - "Экспорт ROE" (Export ROE) - ROE session data
4. **Department Selection Workflow**: When "Export by Department" is selected, displays submenu with all 13 departments
5. **Export Processing**: Selected export type processed with progress notifications
6. **Progress Notifications**: Real-time export progress updates with throttled notifications (minimum 2-second intervals)
7. **File Delivery**: CSV file sent to user via Telegram file upload
8. **Navigation**: Cancel option returns to main menu, back navigation between selection screens

**Features**:
- **Complete Data Export**: All participant fields included with exact Airtable field names
- **UTF-8 Encoding**: Proper Russian text support in exported files
- **Progress Updates**: Throttled progress notifications prevent Telegram rate limiting
- **File Size Validation**: 50MB Telegram upload limit compliance
- **Secure Processing**: Temporary file creation with automatic cleanup
- **Error Handling**: User-friendly error messages for various failure scenarios

**Interactive Export Selection Example**:
```
Admin: /export
Bot: Выберите тип экспорта:
[6 export option buttons displayed]

Admin clicks: "Экспорт по департаменту"
Bot: Выберите департамент:
[13 department buttons displayed: ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate]

Admin clicks: "Setup"
Bot: 🔄 Начинается экспорт данных департамента Setup...
Bot: 📈 Экспорт: 50% завершено (25/50 участников)
Bot: ✅ Экспорт завершён! Отправляю файл...
Bot: 📁 Файл успешно отправлен!
[CSV file attachment: setup_export_YYYY-MM-DD_HH-MM.csv]

# Alternative workflow - Export All:
Admin: /export
Admin clicks: "Экспорт всех данных"
Bot: 🔄 Начинается экспорт данных участников...
Bot: 📈 Экспорт: 25% завершено (250/1000 участников)
Bot: 📈 Экспорт: 50% завершено (500/1000 участников)
Bot: 📈 Экспорт: 75% завершено (750/1000 участников)
Bot: ✅ Экспорт завершён! Отправляю файл...
Bot: 📁 Файл успешно отправлен!
[CSV file attachment: participants_export_YYYY-MM-DD_HH-MM.csv]
```

**Interactive Conversation Features**:
- **Conversation Flow**: ConversationHandler-based state management with export selection workflow
- **Service Factory Integration**: All 6 export types integrated through service factory for unified access
- **State Management**: Proper conversation states for selection → processing → completion workflow
- **Export Selection Keyboards**: Mobile-optimized inline keyboards with Russian localization
- **Department Selection Interface**: Secondary keyboard for department-specific exports with all 13 departments
- **Progress Tracker**: ExportProgressTracker class manages throttled notifications across all export types
- **Service Integration**: Uses multiple export services (ParticipantExportService, BibleReadersExportService, ROEExportService)
- **Repository Pattern**: Leverages existing data access layer with multi-table support
- **3-Layer Architecture**: Follows established bot → service → data pattern
- **Telegram File Upload**: Direct CSV delivery via Telegram document upload API
- **Navigation & Cancellation**: Cancel options at each step, back navigation between selection screens
- **File Size Validation**: Pre-upload validation against 50MB Telegram limit
- **Resource Management**: Guaranteed file cleanup with try-finally blocks
- **Error Recovery**: Comprehensive retry logic for transient failures
- **Audit Logging**: Complete user interaction logging for administrative monitoring

**Error Scenarios with File Delivery**:
- **Unauthorized Access**: "Доступ запрещён. Эта команда доступна только администраторам."
- **Export Failure**: "Произошла ошибка при экспорте данных. Попробуйте позже."
- **File Size Exceeded**: "Файл слишком большой для отправки через Telegram (максимум 50MB)."
- **Network Issues**: "Ошибка сети. Попробуйте позже."
- **File Upload Failures**: Comprehensive error handling for Telegram API failures:
  - **RetryAfter Errors**: Automatic retry with exponential backoff (up to 3 attempts)
  - **BadRequest Errors**: File format or size validation with user-friendly messages
  - **NetworkError**: Connection retry mechanism with progress preservation
  - **TelegramError**: General API error handling with detailed logging
- **File Cleanup**: Automatic temporary file removal ensures no disk space accumulation

### Extended Fields Usage Examples (2025-01-14)

#### Church Leader Management
1. User searches for participant: `/search Иван Петров`
2. Bot displays search results with Church Leader field ("⛪ Церковный лидер: —")
3. User clicks "Подробнее" → "Изменить церковного лидера"
4. Bot prompts: "Отправьте имя церковного лидера"
5. User types: "Отец Владимир"
6. Bot displays complete participant profile with updated church leader information

#### Table Assignment for Candidates
1. User searches for candidate: `/search Мария Козлова`
2. Bot displays search results with Table Name field visible (role=CANDIDATE)
3. User clicks "Подробнее" → "Изменить название стола"
4. Bot prompts: "Отправьте название стола"
5. User types: "Стол 12A"
6. Bot displays complete participant profile with table assignment
7. **Role Restriction**: If user changes role to TEAM, Table Name button disappears

#### Multiline Notes Management
1. User selects participant and clicks "Изменить заметки"
2. Bot prompts: "Отправьте заметки"
3. User types multiline text:
   ```
   Нуждается в особом питании
   Аллергия на орехи
   Прибывает в пятницу
   ```
4. Bot displays complete participant profile with full notes preserved
5. Search results show truncated version: "📝 Заметки: Нуждается в особом питании..."

### Integration with Existing Features

The new participant fields (ChurchLeader, TableName, Notes) are fully integrated with all existing bot functionality:

#### Save/Cancel Workflow Integration
- **Change Confirmation**: New fields appear in confirmation screens showing "Current Value → **New Value**" format
- **Save Success**: Complete participant display includes all new fields after successful save
- **Cancel Workflow**: All new field changes are properly discarded when user cancels
- **Retry Mechanism**: Failed saves preserve new field values during retry attempts

#### Search Integration
- **Name Search Results**: New fields displayed with appropriate formatting and role-based visibility
- **List View Integration**: Team and candidate lists show new fields where appropriate
- **Multi-field Search**: Notes field content is searchable via existing search functionality

#### Role-Based Business Logic
- **Dynamic Interface**: TableName edit button visibility changes based on participant role
- **Validation Rules**: Business rules prevent saving TableName for TEAM role participants
- **Error Handling**: Clear Russian error messages for role-based validation failures
