# Bot Commands Reference

## Search Commands

### /search [query] and Search Button
Search for participants by name (Russian or English), nickname, or other details. Available via command or main menu "🔍 Поиск участников" button.

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
- **"Отмена" (Cancel)**: Discards all changes and returns to main menu
- **"Назад к поиску" (Back to Search)**: Returns to search results without saving
- **"Вернуться в главное меню" (Return to Main Menu)**: Cancel confirmation option

#### Error Handling and Retry
- **Save Failure**: Automatic retry buttons appear on Airtable update errors
- **"Попробовать снова" (Try Again)**: Retry failed save operation preserving changes
- **Error Messages**: User-friendly Russian error messages with actionable instructions
- **Data Preservation**: User changes maintained during retry operations
- **Display Error Recovery**: Enhanced error handling prevents silent display failures during field editing with comprehensive logging (REGRESSION markers) and meaningful user feedback
- **Context Loss Handling**: Graceful degradation when participant context is lost, providing clear error messages and recovery guidance

## Error Handling

### Validation Errors
- Clear Russian error messages for invalid input
- Prompts user to retry with correct format
- Field-specific validation rules enforced

### System Errors  
- Graceful handling of Airtable API errors
- Rate limiting protection (5 requests/second)
- Connection timeout recovery

## Usage Flow Example

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

### Error Recovery Flow

1. User attempts to save changes
2. **Airtable Error Occurs** (network/API issue)
3. Bot displays: "Ошибка при сохранении данных в Airtable" 
4. **Retry Button**: "Попробовать снова" appears automatically
5. User clicks retry → Bot attempts save again with preserved changes
6. Success: Changes saved and user notified
7. Failure: Retry option remains available
