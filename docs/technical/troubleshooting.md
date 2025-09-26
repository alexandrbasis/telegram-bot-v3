# Troubleshooting

## Participant Editing Issues

### Date of Birth and Age Field Issues (Fixed 2025-09-11)

#### Critical Bug: Fields Not Displaying and JSON Serialization Error
**Problem**: Age and date of birth fields not displaying correctly in edit interface and causing "Object of type date is not JSON serializable" errors during save operations.

**Symptoms**:
- Age and date of birth show as "Не указано" even when data exists
- Save operations fail with JSON serialization error: "Object of type date is not JSON serializable"  
- Missing fields in edit menu and confirmation screens
- Values don't persist or display after successful edits

**Root Causes**:
1. **Participant Reconstruction**: `display_updated_participant()` function missing `date_of_birth` and `age` fields in Participant constructor
2. **Date Serialization**: Airtable repository missing date_of_birth serialization (only handled payment_date)
3. **UI Integration**: Missing Russian labels and formatting in edit menu and confirmation screens

**Resolution (Implemented)**:
1. **Fixed Participant Reconstruction**: Added date_of_birth and age fields to participant construction in edit handlers
2. **Extended Date Serialization**: Updated `_convert_field_updates_to_airtable()` to serialize date_of_birth to ISO format  
3. **Enhanced UI Integration**: Added proper Russian labels (🎂 Дата рождения, 🔢 Возраст) in all display contexts
4. **Robust Clearing Behavior**: Implemented whitespace-only input → None clearing for both fields
5. **Enhanced Error Messages**: Improved validation errors with ❌ prefix and InfoMessages guidance

**Files Modified**:
- `src/bot/handlers/edit_participant_handlers.py`: Participant reconstruction and UI labels
- `src/data/airtable/airtable_participant_repo.py`: Date serialization extension  
- `src/services/participant_update_service.py`: Clearing behavior and error messaging

**Verification**: 116/116 tests pass, including comprehensive clearing behavior and end-to-end serialization tests

### Display Regression Issues (2025-09-02)

#### Participant Information Not Visible During Editing
**Problem**: Users see no participant information after field updates, breaking the complete participant display feature
**Root Cause**: `context.user_data.get("current_participant")` returns None during field editing sessions, causing handlers to fall back to simple success messages instead of calling `display_updated_participant()`
**Symptoms**:
- Field edits succeed but no participant context displayed
- Users see basic "field updated" messages without participant information
- Complete information loss during editing workflow

**Resolution**:
1. **Enhanced Error Handling**: Implemented comprehensive try-catch blocks around display function calls
2. **REGRESSION Logging**: Added detailed logging with REGRESSION markers for production debugging
3. **Graceful Degradation**: Meaningful user feedback when context is lost with recovery guidance
4. **Context Recovery**: Clear instructions for users when display functionality fails
5. **Monitoring**: Enhanced logging enables proactive detection of similar issues

**Prevention**: Comprehensive regression tests (TestDisplayRegressionIssue and TestComprehensiveDisplayRegressionPrevention) ensure future detection of context corruption scenarios

#### Save Success Missing Participant Context
**Problem**: Save success shows basic confirmation message instead of complete updated participant information
**Root Cause**: Save success flow was not enhanced to display complete participant context as specified in business requirements
**Resolution**: Implemented format_participant_result() call in save_changes function with comprehensive error handling and fallback to simple message if display fails

### Save Operation Failures

#### Airtable API Errors
**Problem**: User gets "Ошибка при сохранении данных в Airtable" message
**Causes**: 
- Network connectivity issues
- Airtable API rate limit exceeded
- Invalid Airtable API key or permissions
- Airtable service outage

**Resolution**:
1. User clicks "Попробовать снова" (Try Again) button that appears automatically
2. Bot preserves all user changes and retries the save operation
3. If retry fails, check network connectivity and Airtable service status
4. For persistent failures, verify `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID` configuration

#### Validation Errors During Save
**Problem**: Save fails due to field validation issues
**Common Validation Failures**:
- Russian name field empty (required field)
- Payment amount not a valid integer
- Payment date not in YYYY-MM-DD format

**Resolution**: 
- Bot shows specific Russian error message for failed validation
- User can edit the problematic field again before retry
- Changes to valid fields are preserved during validation failure recovery

### Conversation State Issues

#### Search Button Not Responding
**Problem**: "Поиск Участников" (Participant Search) button click does not respond or trigger search functionality
**Causes**:
- ConversationHandler state collision between different enum states (SearchStates vs EditStates)
- Improper ConversationHandler per_message configuration causing CallbackQueryHandler tracking issues
- Handler registration conflicts

**Resolution**:
1. **State Collision Fix**: Ensure different ConversationHandler state enums use non-overlapping values
   - Example: SearchStates (10,11,12) vs EditStates (0,1,2)
   - Check `src/bot/handlers/search_handlers.py` for SearchStates enum values
2. **ConversationHandler Configuration**: Verify per_message parameter is set correctly
   - For mixed handler types (MessageHandler + CallbackQueryHandler): use `per_message=None`
   - Check `src/bot/handlers/search_conversation.py` ConversationHandler initialization
3. **Handler Pattern Verification**: Confirm CallbackQueryHandler pattern matches button callback_data
   - Search button uses `callback_data="search"` with pattern `"^search$"`
4. **Testing**: Run regression test `tests/unit/test_search_button_regression.py` to validate functionality

#### Name Search Button Processed as Query (Fixed 2025-09-10)
**Problem**: Search mode buttons ("👤 По имени", "🚪 По комнате", "🏢 По этажу") were being processed as search queries instead of navigation commands
**Root Cause**: Missing `NAV_SEARCH_*` constants in WAITING state MessageHandler exclusion filters
**Symptoms**:
- Clicking "👤 По имени" button triggers search for "👤 По имени" text instead of transitioning to input waiting state
- "No participants found" error when clicking search mode buttons
- Affected all three search modes (name, room, floor)

**Fixed Implementation**:
1. **Filter Pattern Fix**: Added navigation button constants to exclusion regex patterns in `search_conversation.py`:
   - Line 133: Added `NAV_SEARCH_NAME` to WAITING_FOR_NAME filter exclusion
   - Line 172: Added `NAV_SEARCH_ROOM` to WAITING_FOR_ROOM filter exclusion
   - Line 205: Added `NAV_SEARCH_FLOOR` to WAITING_FOR_FLOOR filter exclusion
2. **Consistent Behavior**: All three search modes now follow correct button→prompt→input pattern
3. **Test Coverage**: Comprehensive test suite in `test_search_conversation_name.py` prevents regression

#### Room Search Flow Issues (Fixed 2025-01-15)
**Problem**: Room search shows duplicate messages and broken cancel functionality
**Causes**:
- Room mode handler delegating to command handler instead of direct prompt
- Missing NAV_CANCEL handler in WAITING_FOR_ROOM state
- Cancel text being processed as room input causing validation errors

**Fixed Implementation**:
1. **Direct Prompt Pattern**: `handle_search_room_mode()` now sends single prompt and returns `WAITING_FOR_ROOM` (mirrors floor search)
2. **Cancel Handler Added**: NAV_CANCEL button properly registered in `RoomSearchStates.WAITING_FOR_ROOM` 
3. **Input Filter Fixed**: Cancel text excluded from room number processing to prevent premature validation
4. **Consistent UX**: Room search now provides same clean user experience as floor search

#### Lost Editing Context
**Problem**: User editing session becomes unresponsive or shows unexpected behavior
**Causes**:
- Bot restart during active editing session
- Conversation timeout (ConversationHandler timeout)
- Multiple concurrent editing sessions
- State collision between different ConversationHandler instances

**Resolution**:
1. Use "Отмена" (Cancel) button to cleanly exit editing mode
2. Return to main menu via "Вернуться в главное меню"
3. Start fresh search session with `/search` command
4. Changes not explicitly saved are automatically discarded
5. **State Collision Check**: If issue persists, verify ConversationHandler state enum values don't conflict

### Conversation Timeout Issues

#### Timeout Not Triggering
**Problem**: Conversations don't timeout after configured period, users remain stuck in stale states
**Causes**:
- Missing `conversation_timeout` parameter in ConversationHandler configuration
- Incorrect timeout value conversion (minutes to seconds)
- Missing TIMEOUT handler registration in conversation states
- Invalid `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` environment variable

**Resolution**:
1. **Configuration Check**: Verify ConversationHandler includes timeout parameter:
   ```python
   conversation_handler = ConversationHandler(
       entry_points=[...],
       states={...},
       fallbacks=[...],
       conversation_timeout=telegram_settings.conversation_timeout_minutes * 60
   )
   ```
2. **Handler Registration**: Ensure TIMEOUT state is mapped to timeout handler:
   ```python
   states = {
       SearchStates.WAITING_FOR_NAME: [...],
       # Other states...
       ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, handle_conversation_timeout)]
   }
   ```
3. **Environment Variable**: Verify `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` is set correctly (1-1440 range)
4. **Settings Loading**: Check that settings are loaded properly: `get_telegram_settings().conversation_timeout_minutes`

#### Timeout Message Not Displaying
**Problem**: Timeout triggers but user doesn't see "Сессия истекла, начните заново" message
**Causes**:
- Error in timeout handler message sending
- Missing or incorrect keyboard generation
- Network issues during message delivery
- Bot token permissions

**Resolution**:
1. **Error Handling Check**: Timeout handler includes try/catch around message sending
2. **Keyboard Generation**: Verify main menu keyboard is created properly
3. **Network Connectivity**: Check bot's network connection and Telegram API accessibility
4. **Graceful Termination**: Even if message fails, conversation should still end properly
5. **Debug Logging**: Enable DEBUG logging to see timeout handler execution details

#### Timeout Period Too Short/Long
**Problem**: Conversations timeout too quickly or take too long to timeout
**Causes**:
- Incorrect `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES` value
- Misunderstanding of timeout period requirements
- Different needs for different conversation types

**Resolution**:
1. **Environment Configuration**: Adjust `TELEGRAM_CONVERSATION_TIMEOUT_MINUTES`:
   - Development: 5-10 minutes for testing
   - Production: 30-60 minutes for user comfort
   - Complex operations: 60-120 minutes
2. **Validation Check**: Ensure value is within valid range (1-1440 minutes)
3. **Restart Required**: Bot restart needed for configuration changes to take effect
4. **User Communication**: Inform users about timeout period if changed significantly

#### Timeout State Cleanup Issues
**Problem**: After timeout, conversation context not properly cleaned up, causing state conflicts
**Causes**:
- Missing `ConversationHandler.END` return in timeout handler
- Incomplete context cleanup in timeout handler
- Memory leaks from uncleared conversation data

**Resolution**:
1. **Handler Return**: Ensure timeout handler returns `ConversationHandler.END`:
   ```python
   async def handle_conversation_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
       # Handle timeout message...
       return ConversationHandler.END  # Critical for state cleanup
   ```
2. **Context Cleanup**: Clear relevant context data if needed (though PTB handles most cleanup automatically)
3. **Memory Monitoring**: Monitor bot memory usage for potential leaks
4. **Testing**: Use integration tests to verify proper state transitions after timeout

#### Cancel Operation Not Working
**Problem**: Cancel button doesn't return user to main menu
**Causes**: 
- Conversation state conflicts
- Handler registration issues
- Missing NAV_CANCEL handlers in conversation waiting states

**Resolution**:
1. Use "Вернуться в главное меню" button from confirmation screen
2. If unresponsive, restart bot session
3. Check logs for conversation handler errors
4. **Room Search Cancel Fix** (2025-01-15): Ensure NAV_CANCEL handlers are properly registered in all waiting states, especially RoomSearchStates.WAITING_FOR_ROOM

### Export Reliability Issues (Added 2025-09-26)

#### Export Failures Due to Missing Airtable Views
**Problem**: Candidate exports fail with VIEW_NAME_NOT_FOUND errors when Airtable view configurations change
**Symptoms**:
- Export commands complete but return empty files
- 422 error codes in export logs
- Users unable to retrieve candidate CSV files

**Automatic Resolution (Implemented)**:
- **Fallback Logic**: Candidate exports automatically detect VIEW_NAME_NOT_FOUND errors
- **Seamless Recovery**: System falls back to repository filtering with Role.CANDIDATE
- **Transparent Operation**: Users experience no interruption during fallback
- **Line Number Preservation**: Sequential numbering maintained regardless of export method

**Manual Verification**:
1. Check export service logs for "VIEW_NAME_NOT_FOUND" and fallback notifications
2. Verify candidate export CSV files contain expected participant counts
3. Confirm line numbers appear as first column starting from 1

#### Async Export Interface Issues
**Problem**: BibleReaders or ROE exports fail with AttributeError on export_to_csv_async method
**Symptoms**:
- Export handlers crash with missing method errors
- Inconsistent export interfaces between services
- Event loop errors during export operations

**Resolution (Implemented)**:
- **Unified Interfaces**: All export services now provide both async and sync methods
- **Event Loop Detection**: Sync wrappers automatically handle running event loops
- **Handler Compatibility**: Export conversation handlers work seamlessly with all services
- **Backward Compatibility**: Existing sync methods preserved for non-async contexts

**Verification**:
1. Confirm all export services have export_to_csv_async() and export_to_csv() methods
2. Test exports in both async handler context and sync utility usage
3. Verify progress callbacks continue functioning with new interfaces

### Data Consistency Issues

#### Changes Not Reflected in Airtable
**Problem**: User saves changes successfully but data not updated in Airtable
**Causes**:
- Airtable field mapping issues
- Field ID mismatches
- Permission restrictions on Airtable base

**Resolution**:
1. Verify Airtable field mappings in `src/config/field_mappings.py`
2. Check Airtable base permissions for the API key
3. Confirm field IDs match Airtable base schema
4. Review logs for field mapping errors

#### Partial Save Operations
**Problem**: Some fields save correctly while others fail
**Causes**:
- Field-specific validation in Airtable
- Field type mismatches
- Required field constraints in Airtable

**Resolution**:
1. Check Airtable base field requirements and constraints
2. Verify field type compatibility (text, select, number, date)
3. Review error messages for specific field failure details
4. Update field mappings if schema has changed

### Performance Issues

#### Slow Save Operations
**Problem**: Save operations take longer than expected
**Causes**:
- Airtable API rate limiting (5 requests/second)
- Network latency
- Large field update operations

**Resolution**:
1. Rate limiting is built into the client - wait for operation to complete
2. Avoid rapid successive save operations
3. Check network connectivity if consistently slow
4. Monitor Airtable API response times

### ConversationHandler Configuration Issues

#### CallbackQueryHandler Not Tracked
**Problem**: Callback queries (button clicks) not processed by ConversationHandler
**Causes**:
- Missing or incorrect per_message parameter in ConversationHandler
- Mixed handler types without proper configuration

**Resolution**:
1. **Configuration Check**: Verify ConversationHandler uses proper per_message setting:
   ```python
   conversation_handler = ConversationHandler(
       entry_points=[...],
       states={...},
       fallbacks=[...],
       per_message=None  # Allows auto-detection for mixed handler types
   )
   ```
2. **Handler Type Analysis**: For ConversationHandlers with both MessageHandler and CallbackQueryHandler:
   - Use `per_message=None` for automatic detection
   - Avoid `per_message=False` which can cause CallbackQueryHandler tracking issues
3. **Testing**: PTB may emit warnings about per_message configuration - these are often informational

#### State Enum Collision Detection
**Problem**: Multiple ConversationHandlers with overlapping state values causing handler conflicts
**Diagnostic Steps**:
1. Check all ConversationHandler state enums for value conflicts:
   ```python
   # Example conflict:
   class SearchStates(IntEnum):
       MAIN_MENU = 0          # Conflicts with EditStates.FIELD_SELECTION = 0
       WAITING_FOR_NAME = 1
       SHOWING_RESULTS = 2
   ```
2. **Resolution Pattern**: Use non-overlapping ranges for different handlers:
   ```python
   # Fixed version:
   class SearchStates(IntEnum):
       MAIN_MENU = 10         # No longer conflicts
       WAITING_FOR_NAME = 11
       SHOWING_RESULTS = 12
   ```

### Logging and Debugging

#### Enable Debug Logging
Set environment variable: `LOG_LEVEL=DEBUG`

#### Key Log Locations
- **Save Operations**: Look for "Saving changes" and Airtable update logs
- **Error Handling**: Search for "Error occurred" in error handling functions
- **State Transitions**: Conversation handler state change logs
- **Retry Operations**: Retry attempt logs with error details
- **Display Regression Issues**: Search for "REGRESSION" markers in logs for display-related errors
- **Context Corruption**: Look for "current_participant is None" or "context missing" messages
- **Display Function Failures**: Search for "display_updated_participant" error logs
- **ConversationHandler Issues**: Search for "ConversationHandler" and "CallbackQueryHandler" logs
- **State Conflicts**: Look for handler registration and state transition errors
- **Timeout Handling**: Search for "timeout" and "TIMEOUT" for conversation timeout events
- **Configuration Loading**: Look for "conversation_timeout_minutes" in settings loading logs

#### Common Log Patterns
```
INFO - Saving changes for participant [ID]
ERROR - Airtable update failed: [error details]
DEBUG - Retry attempt [N] for participant save
INFO - Changes saved successfully, returning to search results
ERROR - REGRESSION: Failed to display updated participant: [error details]
WARN - REGRESSION: current_participant is None, falling back to simple message
INFO - REGRESSION: Context corruption detected, providing user recovery guidance
WARN - per_message=False with mixed handler types (informational)
ERROR - Handler registration conflict for state [N]
INFO - Conversation timeout triggered for user [ID] after [N] minutes
DEBUG - Sending timeout message: "Сессия истекла, начните заново"
ERROR - Failed to send timeout message: [error details]
INFO - Timeout handler completed, conversation ended
DEBUG - Loading conversation_timeout_minutes: [N] from settings

# Export Reliability Logs (Added 2025-09-26)
INFO - Starting candidate export using view: Кандидаты
ERROR - VIEW_NAME_NOT_FOUND: View 'Кандидаты' not found in base
INFO - Triggering fallback for candidate export
DEBUG - Using repository filtering with Role.CANDIDATE for fallback
INFO - Fallback candidate export completed: [N] participants
DEBUG - BibleReaders export using async interface
DEBUG - ROE export using async interface
INFO - Event loop detected, using async delegation
DEBUG - Line numbers preserved in fallback export
```

#### ConversationHandler Debugging
```bash
# Check for state conflicts
grep -r "class.*States.*IntEnum" src/bot/handlers/

# Verify handler registration
grep -r "ConversationHandler" src/bot/handlers/ -A 10

# Test specific button functionality
./venv/bin/pytest tests/unit/test_search_button_regression.py -v

# Test timeout functionality
./venv/bin/pytest tests/unit/test_bot_handlers/test_timeout_handlers.py -v
./venv/bin/pytest tests/integration/test_bot_handlers/test_conversation_timeout_integration.py -v

# Check timeout configuration
python -c "from src.config.settings import get_telegram_settings; print(f'Timeout: {get_telegram_settings().conversation_timeout_minutes} minutes')"
```