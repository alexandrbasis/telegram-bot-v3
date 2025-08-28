# Task: Enhanced Search Results with Participant Editing
**Created**: 2025-08-28 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
### Primary Objective
Transform search results from basic text display into an interactive participant management interface with enhanced result presentation and comprehensive editing capabilities.

### Use Cases
1. **Enhanced Search Results Display**
   - **Scenario**: User searches for "Александр" and receives multiple results
   - **Current**: Shows "100%" match percentage with basic participant info
   - **New**: Shows clear match labels ("Точное совпадение", "Высокое совпадение", "Совпадение") instead of raw percentages
   - **Acceptance**: Each search result displays human-readable match quality labels

2. **Interactive Search Results Navigation**
   - **Scenario**: User receives 1-5 search results for "Александр" 
   - **Current**: Static text display only
   - **New**: Each result becomes a clickable button showing "FirstName LastName" (e.g., "Александр Басис", "Александр Петров")
   - **Behavior**: Always show buttons regardless of result count (1 button for 1 result, up to 5 buttons for 5 results)
   - **Acceptance**: User can click any result button to enter participant editing mode

3. **Comprehensive Participant Editing Interface**
   - **Scenario**: User clicks on "Александр Басис" from search results
   - **Current**: No editing capability from search
   - **New**: Displays complete participant profile with all fields editable via buttons
   - **Acceptance**: Shows all participant data fields with individual "Изменить [Field]" buttons

4. **Predefined Field Editing (Select Fields)**
   - **Scenario**: User wants to change participant's "Роль" (Role)
   - **Fields**: Role, Department, Gender, Size (any field with predefined options)
   - **Behavior**: Click "Изменить роль" → Show inline keyboard with all available role options
   - **Acceptance**: User selects new value from buttons, field updates immediately

5. **Text Field Editing (Free Text Fields)**
   - **Scenario**: User wants to change participant's "Имя" (First Name)
   - **Fields**: Russian Name, English Name, Church, Phone, etc.
   - **Behavior**: Click "Изменить имя" → Bot prompts "Отправьте новое имя" → User types new name → Field updates
   - **Acceptance**: Bot waits for text input, validates, and updates field

6. **Save/Cancel Workflow**
   - **Scenario**: User has made several field changes
   - **Options**: "Сохранить изменения" button and "Вернуться в главное меню" button
   - **Behavior**: Save commits all changes to Airtable, Cancel discards changes and returns to main menu
   - **Acceptance**: Changes are persisted only after explicit save confirmation

### Success Metrics
- [ ] Search results display improved readability (match quality labels vs percentages)
- [ ] 100% of search results become interactive (clickable buttons for all 1-5 results)
- [ ] Complete participant editing interface accessible from search results
- [ ] All predefined fields (Role, Department, Gender, Size) editable via button selection
- [ ] All text fields editable via text input workflow
- [ ] Changes saved to Airtable only after explicit user confirmation
- [ ] User can cancel editing and return to main menu without saving changes

### Constraints
- **Technical**: Must integrate with existing Universal Search Enhancement (recently implemented)
- **UX**: Must maintain conversation flow patterns established in current bot
- **Data**: Must respect Airtable field validation and constraints
- **Performance**: Field updates should complete within 3 seconds
- **Compatibility**: Must not break existing search functionality

---

**APPROVAL GATE 1**: ✅ **APPROVED** - Business requirements confirmed

---

# Test Plan: Enhanced Search Results with Participant Editing
**Status**: Awaiting Test Plan Approval | **Created**: 2025-08-28

## Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

## Proposed Test Categories
### Business Logic Tests
- [ ] **Search Result Button Generation Test** - Verify 1-5 interactive buttons created for any search result count
- [ ] **Match Quality Label Translation Test** - Validate percentage-to-label conversion ("100%" → "Точное совпадение", "85%" → "Высокое совпадение", "70%" → "Совпадение")
- [ ] **Participant Profile Loading Test** - Confirm complete participant data retrieval when clicking result button
- [ ] **Field Type Classification Test** - Verify correct identification of predefined vs text fields for editing interface
- [ ] **Change Tracking Test** - Validate temporary change storage before save/cancel decision

### State Transition Tests  
- [ ] **Search Results → Edit Mode Transition** - Test navigation from search results to participant editing interface
- [ ] **Field Edit State Management** - Verify state transitions for individual field editing (text input waiting, predefined selection)
- [ ] **Save/Cancel State Handling** - Test proper state cleanup on save confirmation or cancellation
- [ ] **Main Menu Return Flow** - Validate clean return to main menu without saving changes

### Error Handling Tests
- [ ] **Invalid Text Input Handling** - Test validation for text field edits (empty strings, length limits, special characters)
- [ ] **Airtable Update Failure Recovery** - Test graceful handling of save operation failures
- [ ] **Button Click Error Recovery** - Validate error handling for invalid participant selection or field access
- [ ] **Concurrent Edit Protection** - Test behavior when participant data changes during editing session

### Integration Tests
- [ ] **Airtable Field Update Integration** - End-to-end test of field changes persisted to Airtable
- [ ] **Search Service Integration** - Verify integration with existing Universal Search Enhancement
- [ ] **Keyboard Generation Integration** - Test dynamic inline keyboard creation for predefined fields
- [ ] **Conversation Handler Integration** - Validate proper integration with existing conversation flow patterns

### User Interaction Tests
- [ ] **Single Result Button Display** - Test interactive button creation for single search result
- [ ] **Multiple Result Button Display** - Test 2-5 interactive buttons with unique participant names
- [ ] **Predefined Field Selection** - Test Role/Department/Gender/Size button-based editing
- [ ] **Text Field Input Workflow** - Test Name/Church/Phone text-based editing with input validation
- [ ] **Save Confirmation Flow** - Test complete save workflow with success confirmation
- [ ] **Cancel Without Save Flow** - Test cancellation workflow preserving original data

## Test-to-Requirement Mapping
- **Enhanced Search Results Display** → Match Quality Label Translation Test, Search Result Button Generation Test
- **Interactive Search Results Navigation** → Single/Multiple Result Button Display Tests, Search Results → Edit Mode Transition
- **Comprehensive Participant Editing Interface** → Participant Profile Loading Test, Field Type Classification Test
- **Predefined Field Editing** → Predefined Field Selection Test, Keyboard Generation Integration Test
- **Text Field Editing** → Text Field Input Workflow Test, Invalid Text Input Handling Test
- **Save/Cancel Workflow** → Save Confirmation Flow Test, Cancel Without Save Flow Test, Change Tracking Test

---

**APPROVAL GATE 2**: ✅ **APPROVED** - Test plan confirmed

---

## Technical Requirements

### Business Context
Enhance search results with interactive participant editing capabilities, building on the existing Universal Search Enhancement foundation.

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

- [ ] Step 1: Enhance Search Result Display with Match Quality Labels
  - [ ] Sub-step 1.1: Update search service to generate human-readable match labels
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/search_service.py`
    - **Accept**: Function `format_match_quality()` converts percentages to Russian labels ("Точное совпадение", "Высокое совпадение", "Совпадение")
    - **Tests**: `tests/unit/test_services/test_search_service.py::test_format_match_quality_labels`
    - **Done**: Search results display readable match quality instead of raw percentages
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 2: Create Interactive Search Results with Participant Selection Buttons
  - [ ] Sub-step 2.1: Modify search handlers to generate participant selection keyboards
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/search_handlers.py`
    - **Accept**: Function `create_participant_selection_keyboard()` generates 1-5 buttons with participant names
    - **Tests**: `tests/unit/test_bot_handlers/test_search_handlers.py::test_participant_selection_buttons`
    - **Done**: All search results (1-5) display as clickable buttons with "FirstName LastName" labels
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 3: Implement Participant Profile Editing Interface
  - [ ] Sub-step 3.1: Create participant editing conversation handler
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: ConversationHandler with states for field editing workflow
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py`
    - **Done**: Complete participant editing interface with field-specific edit buttons
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 3.2: Implement field-specific editing keyboards and prompts
    - **Directory**: `src/bot/keyboards/`
    - **Files to create/modify**: `src/bot/keyboards/edit_keyboards.py`
    - **Accept**: Functions for predefined field keyboards (Gender, Size, Role, Department, PaymentStatus) and text input prompts
    - **Tests**: `tests/unit/test_bot_keyboards/test_edit_keyboards.py`
    - **Done**: Separate keyboards for each field type with proper Russian labels
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 4: Implement Field Update Logic with Validation
  - [ ] Sub-step 4.1: Create field update service with validation
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/participant_update_service.py`
    - **Accept**: Functions to validate and update each field type (predefined, text, number, date)
    - **Tests**: `tests/unit/test_services/test_participant_update_service.py`
    - **Done**: Comprehensive field validation and temporary change storage before save
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 4.2: Integrate participant repository update methods
    - **Directory**: `src/data/repositories/`
    - **Files to create/modify**: `src/data/repositories/participant_repository.py`
    - **Accept**: Method `update_participant_fields()` for selective field updates
    - **Tests**: `tests/unit/test_data/test_repositories/test_participant_repository.py::test_update_participant_fields`
    - **Done**: Repository supports atomic field updates with rollback capability
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 5: Implement Save/Cancel Workflow
  - [ ] Sub-step 5.1: Create change tracking and confirmation system
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/edit_participant_handlers.py`
    - **Accept**: Functions to track changes, display confirmation, and handle save/cancel
    - **Tests**: `tests/unit/test_bot_handlers/test_edit_participant_handlers.py::test_save_cancel_workflow`
    - **Done**: Users can save all changes or cancel and return to main menu
    - **Changelog**: [Record changes made with file paths and line ranges]

  - [ ] Sub-step 5.2: Add confirmation messages and user feedback
    - **Directory**: `src/bot/`
    - **Files to create/modify**: `src/bot/messages.py`
    - **Accept**: Messages for field update confirmations, save success, and cancel confirmation
    - **Tests**: `tests/unit/test_bot/test_messages.py::test_edit_participant_messages`
    - **Done**: Clear user feedback for all editing operations
    - **Changelog**: [Record changes made with file paths and line ranges]

- [ ] Step 6: Integration Testing and Conversation Flow Updates
  - [ ] Sub-step 6.1: Update main conversation handler to include edit flow
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/main_handler.py`
    - **Accept**: Integration of participant editing into main bot conversation flow
    - **Tests**: `tests/integration/test_search_to_edit_flow.py`
    - **Done**: Seamless transition from search results to editing and back to main menu
    - **Changelog**: [Record changes made with file paths and line ranges]

## Testing Strategy
- [ ] Unit tests: All service, handler, and keyboard components in `tests/unit/`
- [ ] Integration tests: Complete search-to-edit-to-save workflow in `tests/integration/`
- [ ] Field validation tests: All field types with valid/invalid inputs in `tests/unit/test_services/`

## Success Criteria
- [ ] All acceptance criteria met for enhanced search results display
- [ ] Interactive buttons generated for all search result counts (1-5)
- [ ] Complete participant editing interface accessible from search results
- [ ] All field types (predefined, text, number, date) editable with proper validation
- [ ] Changes persisted to Airtable only after explicit save confirmation
- [ ] Clean cancel workflow returning to main menu without saving
- [ ] Tests pass (100% required)
- [ ] No regressions to existing search functionality
- [ ] Code review approved

---

**APPROVAL GATE 3**: Technical decomposition created with detailed field specifications

**Ready for Gate 4: Plan Review by Plan Reviewer agent**

## Context from Recent Development
Based on CHANGELOG.md analysis, we've recently implemented:
- Universal Search Enhancement with language detection and multi-field search
- Rich participant result formatting with match confidence scoring
- Enhanced repository layer with `search_by_name_enhanced()` method
- 67 comprehensive tests with 100% pass rate

This task builds directly on that foundation, adding interactivity and editing capabilities to the search results.