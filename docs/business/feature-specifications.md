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
- [x] ✅ **Save confirmation workflow** with change preview and explicit user confirmation
- [x] ✅ **Cancel workflow** discards changes and returns to main menu cleanly
- [x] ✅ **Error handling with retry** preserves user changes during failed save operations
- [x] ✅ Complete test coverage (33 tests total including integration, 100% pass rate)
- [x] ✅ Russian localization across all UI elements including error messages
- [x] ✅ Integration with existing search functionality and conversation flows

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

## Save/Cancel Workflow with Airtable Integration

### Overview
Complete save/cancel workflow system with change confirmation, error handling, and Airtable integration for the participant editing feature.

**Status**: ✅ Implemented (2025-08-29)
**Implementation**: Enhanced edit_participant_handlers.py with confirmation screens and retry logic
**Test Coverage**: 33 tests total (21 unit + 8 repository + 4 integration tests) - 100% pass rate

### Core Features

#### 1. Save Confirmation Screen
- **Change Preview**: Shows all pending changes in "Current Value → **New Value**" format
- **Explicit Confirmation**: Requires user confirmation before committing to Airtable
- **Change Summary**: Groups all field modifications in a single confirmation view
- **Actions**: "Подтвердить сохранение" (Confirm) or "Отмена" (Cancel)

#### 2. Cancel Workflow
- **Change Discard**: Cancel discards all pending changes without saving
- **Clean State**: Returns user to main menu with clean conversation state
- **Confirmation**: "Вернуться в главное меню" confirmation option
- **Context Reset**: Clears editing context to prevent state conflicts

#### 3. Error Handling and Retry
- **Automatic Retry**: Failed save operations show "Попробовать снова" (Try Again) button
- **Change Preservation**: User changes preserved during retry attempts
- **Error Details**: Clear Russian error messages explaining failure reasons
- **Recovery Path**: Multiple retry attempts allowed until success or user cancellation

#### 4. Airtable Integration
- **Atomic Updates**: All changes committed in single Airtable update operation
- **Rate Limiting**: Respects Airtable API rate limits (5 requests/second)
- **Field Mapping**: Proper translation between internal models and Airtable schema
- **Error Classification**: Network, validation, and API errors handled appropriately

### Technical Implementation

#### Save Confirmation Flow
- **Function**: `show_save_confirmation()` (lines 506-591)
- **Change Tracking**: Modified fields tracked in conversation context
- **Confirmation Display**: Russian field names with before/after values
- **User Actions**: Confirmation or cancellation buttons

#### Retry Mechanism
- **Function**: `retry_save()` (lines 594-614)
- **Error Classification**: Distinguishes between different failure types
- **User Feedback**: Specific error messages for network vs validation issues
- **State Recovery**: Maintains editing context through retry cycles

#### Integration Testing
- **Test Suite**: `tests/integration/test_search_to_edit_flow.py` (314 lines)
- **Coverage**: Complete user journeys from search through edit to save
- **Scenarios**: Success, cancel, retry, and validation workflows
- **Quality Assurance**: All 4 integration tests passing

### Acceptance Criteria

- [x] ✅ Save confirmation displays all pending changes clearly
- [x] ✅ Cancel workflow discards changes and returns to main menu
- [x] ✅ Error recovery allows retry without data loss
- [x] ✅ Airtable integration handles all error scenarios gracefully
- [x] ✅ Complete conversation flow integration without state conflicts
- [x] ✅ Russian localization for all user-facing messages
- [x] ✅ Comprehensive test coverage (100% pass rate)