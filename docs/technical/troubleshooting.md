# Troubleshooting

## Participant Editing Issues

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

#### Cancel Operation Not Working
**Problem**: Cancel button doesn't return user to main menu
**Causes**: 
- Conversation state conflicts
- Handler registration issues

**Resolution**:
1. Use "Вернуться в главное меню" button from confirmation screen
2. If unresponsive, restart bot session
3. Check logs for conversation handler errors

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
```

#### ConversationHandler Debugging
```bash
# Check for state conflicts
grep -r "class.*States.*IntEnum" src/bot/handlers/

# Verify handler registration
grep -r "ConversationHandler" src/bot/handlers/ -A 10

# Test specific button functionality
./venv/bin/pytest tests/unit/test_search_button_regression.py -v
```