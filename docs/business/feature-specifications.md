# Feature Specifications

## Participant Editing Interface

### Overview
Comprehensive participant profile editing interface accessible through search results. Supports all 13 participant fields with appropriate input methods and validation.

**Status**: ✅ Implemented (2025-08-29)
**Implementation**: 4-state ConversationHandler with Russian localization
**Test Coverage**: 56 unit tests (100% pass rate)

### Core Features

#### 1. Participant Selection Interface
- **Access**: Click "Подробнее" (Details) button on any search result
- **Display**: Complete participant profile with all field values
- **Layout**: 13 individual "Изменить [Field]" edit buttons
- **Actions**: Save Changes, Cancel, Back to Search

#### 2. Field-Specific Editing Methods

**Button-Based Fields (5 fields)**
- Immediate selection through inline keyboards
- No text input required
- Instant field updates

Fields:
- **Gender (Пол)**: Мужской/Женский (2 options)
- **Size (Размер)**: XS, S, M, L, XL, XXL, 3XL (7 options) 
- **Role (Роль)**: Кандидат/Команда (2 options)
- **Department (Департамент)**: 13 department options
- **Payment Status (Статус платежа)**: Оплачено/Частично/Не оплачено (3 options)

**Text Input Fields (6 fields)**
- Prompted text input workflow
- Russian prompts and validation messages
- Optional/required field validation

Fields:
- **Full Name Russian (Имя русское)**: Required, min length 1
- **Full Name English (Имя английское)**: Optional
- **Church (Церковь)**: Optional
- **Location (Местоположение)**: Optional
- **Contact (Контакты)**: Optional 
- **Submitted By (Отправитель)**: Optional

**Special Validation Fields (2 fields)**
- Custom validation logic
- Format-specific error messages

Fields:
- **Payment Amount (Сумма платежа)**: Integer ≥ 0
- **Payment Date (Дата платежа)**: YYYY-MM-DD format

#### 3. Conversation Flow Management

**State Machine**: 4-state ConversationHandler
1. **FIELD_SELECTION**: Display participant profile with edit buttons
2. **TEXT_INPUT**: Handle text input for free text fields
3. **BUTTON_SELECTION**: Handle inline keyboard selections
4. **CONFIRMATION**: Save/cancel workflow

**State Transitions**:
- Field Selection → Text Input (for text fields)
- Field Selection → Button Selection (for predefined fields) 
- Text/Button Input → Field Selection (after update)
- Field Selection → Confirmation (save/cancel)

#### 4. Russian Localization

**User Interface Elements**:
- All button labels in Russian
- Field names translated (e.g., "Изменить пол", "Изменить размер")
- Navigation buttons ("Назад", "Далее", "Отмена")

**User Prompts**:
- Input prompts in Russian (e.g., "Отправьте новое имя на русском")
- Validation error messages in Russian
- Success/confirmation messages in Russian

**Field Values**:
- Enum values displayed in Russian (Мужской/Женский, Оплачено/Частично)
- Department names localized where applicable

#### 5. Data Validation & Error Handling

**Field-Specific Validation**:
- Required field enforcement (Russian name)
- Format validation (date: YYYY-MM-DD, amount: integer)
- Enum value conversion (Gender, Size, Role, etc.)

**Error Messages**:
- Russian error messages for all validation failures
- Clear instruction on correct input format
- Retry prompts after validation errors

**System Error Handling**:
- Airtable API error recovery
- Rate limiting protection
- Graceful conversation state cleanup

### Technical Architecture

#### Implementation Components
1. **Handler**: `src/bot/handlers/edit_participant_handlers.py` (501 lines)
2. **Keyboards**: `src/bot/keyboards/edit_keyboards.py` (160 lines)
3. **Service**: `src/services/participant_update_service.py` (151 lines)
4. **Repository**: Extended `airtable_participant_repo.py` with `update_by_id`

#### Integration Points
- Extends existing search conversation handler
- Integrates with Airtable repository pattern
- Uses participant update service for validation
- Maintains conversation context across state transitions

### Acceptance Criteria

- [x] ✅ All 13 participant fields accessible through editing interface
- [x] ✅ Button-based fields show correct options with Russian labels
- [x] ✅ Text fields accept and validate input with Russian prompts
- [x] ✅ State management maintains editing context properly
- [x] ✅ Field validation prevents invalid data with clear error messages
- [x] ✅ Complete test coverage (56 tests, 100% pass rate)
- [x] ✅ Russian localization across all UI elements
- [x] ✅ Integration with existing search functionality

### Future Enhancements

**Potential Improvements**:
- Bulk edit functionality for multiple participants
- Field history/audit trail
- Advanced validation rules (e.g., phone number format)
- Export functionality for edited data
- Role-based edit permissions

**Integration Opportunities**:
- Integration with participant import/export
- Reporting dashboard for field changes
- Notification system for significant updates