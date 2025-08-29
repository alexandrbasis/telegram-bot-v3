# Task: Participant Editing Interface
**Created**: 2025-08-28 | **Status**: In Progress | **Branch**: feature/agb-15-participant-editing-interface

## Business Requirements ✅ **APPROVED**
### Primary Objective
Implement a comprehensive participant profile editing interface with field selection menu and appropriate input methods for different field types.

### Use Cases
1. **Comprehensive Participant Editing Interface**
   - **Scenario**: User clicks on participant from search results
   - **Current**: No editing capability from search
   - **New**: Displays complete participant profile with all fields editable via buttons
   - **Acceptance**: Shows all participant data fields with individual "Изменить [Field]" buttons

2. **Predefined Field Editing (Select Fields)**
   - **Scenario**: User wants to change participant's "Роль" (Role) 
   - **Fields**: Role, Department, Gender, Size, PaymentStatus (any field with predefined options)
   - **Behavior**: Click "Изменить роль" → Show inline keyboard with all available role options
   - **Acceptance**: User selects new value from buttons, field updates immediately

3. **Text Field Editing (Free Text Fields)**
   - **Scenario**: User wants to change participant's "Имя" (First Name)
   - **Fields**: Russian Name, English Name, Church, Contact, etc.
   - **Behavior**: Click "Изменить имя" → Bot prompts "Отправьте новое имя" → User types new name → Field updates
   - **Acceptance**: Bot waits for text input, validates, and updates field

### Success Metrics
- [ ] Complete participant editing interface accessible from search results
- [ ] All predefined fields (Role, Department, Gender, Size, PaymentStatus) editable via button selection
- [ ] All text fields editable via text input workflow
- [ ] Field-specific validation prevents invalid data entry

### Constraints
- Depends on subtask-1 (Enhanced Search Display) completion
- Must handle all 13 participant fields with appropriate input methods
- Must maintain conversation state during editing

## Detailed Field Specifications for Editing Interface

### Button-Based Fields (Predefined Options)
**Implementation**: Inline keyboard with option buttons

1. **Gender (Пол)**
   - **Field**: `gender` 
   - **Options**: "M" (Мужской), "F" (Женский)
   - **UI**: `InlineKeyboardButton` for each option
   - **Behavior**: Click → Immediate field update

2. **Size (Размер)**
   - **Field**: `size`
   - **Options**: "XS", "S", "M", "L", "XL", "XXL", "3XL"
   - **UI**: `InlineKeyboardButton` for each size
   - **Behavior**: Click → Immediate field update

3. **Role (Роль)**
   - **Field**: `role`
   - **Options**: "CANDIDATE" (Кандидат), "TEAM" (Команда)
   - **UI**: `InlineKeyboardButton` for each role
   - **Behavior**: Click → Immediate field update

4. **Department (Департамент)**
   - **Field**: `department`
   - **Options**: "ROE", "Chapel", "Setup", "Palanka", "Administration", "Kitchen", "Decoration", "Bell", "Refreshment", "Worship", "Media", "Clergy", "Rectorate"
   - **UI**: `InlineKeyboardButton` for each department
   - **Behavior**: Click → Immediate field update

5. **Payment Status (Статус платежа)**
   - **Field**: `payment_status`
   - **Options**: "Paid" (Оплачено), "Partial" (Частично), "Unpaid" (Не оплачено)
   - **UI**: `InlineKeyboardButton` for each status
   - **Behavior**: Click → Immediate field update

### Text Input Fields (Free Text)
**Implementation**: Text input prompt workflow

1. **Full Name Russian (Имя на русском)** ⭐ *Required*
   - **Field**: `full_name_ru`
   - **UI**: "Изменить имя (русское)" button
   - **Behavior**: Click → Bot prompts "Отправьте новое имя на русском" → Wait for text → Validate (non-empty) → Update
   - **Validation**: Required, min_length=1

2. **Full Name English (Имя на английском)**
   - **Field**: `full_name_en`
   - **UI**: "Изменить имя (английское)" button
   - **Behavior**: Click → Bot prompts "Отправьте новое имя на английском" → Wait for text → Update
   - **Validation**: Optional

3. **Church (Церковь)**
   - **Field**: `church`
   - **UI**: "Изменить церковь" button
   - **Behavior**: Click → Bot prompts "Отправьте название церкви" → Wait for text → Update
   - **Validation**: Optional

4. **Country and City (Страна и город)**
   - **Field**: `country_and_city`
   - **UI**: "Изменить местоположение" button
   - **Behavior**: Click → Bot prompts "Отправьте страну и город" → Wait for text → Update
   - **Validation**: Optional

5. **Contact Information (Контакты)**
   - **Field**: `contact_information`
   - **UI**: "Изменить контакты" button
   - **Behavior**: Click → Bot prompts "Отправьте контактную информацию" → Wait for text → Update
   - **Validation**: Optional

6. **Submitted By (Подано кем)**
   - **Field**: `submitted_by`
   - **UI**: "Изменить отправителя" button
   - **Behavior**: Click → Bot prompts "Отправьте имя отправителя" → Wait for text → Update
   - **Validation**: Optional

### Special Fields (Numbers/Dates)

1. **Payment Amount (Сумма платежа)**
   - **Field**: `payment_amount`
   - **UI**: "Изменить сумму" button
   - **Behavior**: Click → Bot prompts "Отправьте сумму платежа (только цифры)" → Wait for text → Validate integer ≥ 0 → Update
   - **Validation**: Integer, ≥ 0

2. **Payment Date (Дата платежа)**
   - **Field**: `payment_date`
   - **UI**: "Изменить дату платежа" button
   - **Behavior**: Click → Bot prompts "Отправьте дату в формате ГГГГ-ММ-ДД" → Wait for text → Validate date format → Update
   - **Validation**: Valid date format (YYYY-MM-DD)

## Implementation Steps & Change Log
- [ ] Step 1: Create Participant Editing Conversation Handler
  - [ ] Sub-step 1.1: Create participant editing handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: ConversationHandler with states for field editing workflow
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Complete participant editing interface with field-specific edit buttons
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Implement Field-Specific Editing Keyboards and Prompts
  - [ ] Sub-step 2.1: Implement field-specific editing keyboards and prompts
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/edit_keyboards.py`
    - **Accept**: Functions for predefined field keyboards (Gender, Size, Role, Department, PaymentStatus) and text input prompts
    - **Tests**: `tests/unit/test_bot_keyboards/test_edit_keyboards.py`
    - **Done**: Separate keyboards for each field type with proper Russian labels
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Implement Field Update Logic with Validation
  - [ ] Sub-step 3.1: Create field update service with validation
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_update_service.py`
    - **Accept**: Functions to validate and update each field type (predefined, text, number, date)
    - **Tests**: `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Comprehensive field validation and temporary change storage before save
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: Handler logic in `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
- [ ] Unit tests: Keyboard generation in `tests/unit/test_bot_keyboards/test_edit_keyboards.py`
- [ ] Unit tests: Field validation in `tests/unit/test_services/test_participant_update_service.py`
- [ ] Integration tests: Complete field editing flow in `tests/integration/`

## Success Criteria
- [ ] All 13 fields accessible through editing interface
- [ ] Button-based fields show correct options with Russian labels
- [ ] Text-based fields accept and validate input correctly
- [ ] State management maintains editing context properly
- [ ] Field validation prevents invalid data entry with clear error messages
- [ ] Tests pass (100% required)
- [ ] Code review approved

## Dependencies
- **Requires**: Subtask-1 (Enhanced Search Display) completion for participant selection integration