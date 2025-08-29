# Troubleshooting

## Participant Editing Issues

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

#### Lost Editing Context
**Problem**: User editing session becomes unresponsive or shows unexpected behavior
**Causes**:
- Bot restart during active editing session
- Conversation timeout (ConversationHandler timeout)
- Multiple concurrent editing sessions

**Resolution**:
1. Use "Отмена" (Cancel) button to cleanly exit editing mode
2. Return to main menu via "Вернуться в главное меню"
3. Start fresh search session with `/search` command
4. Changes not explicitly saved are automatically discarded

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

### Logging and Debugging

#### Enable Debug Logging
Set environment variable: `LOG_LEVEL=DEBUG`

#### Key Log Locations
- **Save Operations**: Look for "Saving changes" and Airtable update logs
- **Error Handling**: Search for "Error occurred" in error handling functions
- **State Transitions**: Conversation handler state change logs
- **Retry Operations**: Retry attempt logs with error details

#### Common Log Patterns
```
INFO - Saving changes for participant [ID]
ERROR - Airtable update failed: [error details]
DEBUG - Retry attempt [N] for participant save
INFO - Changes saved successfully, returning to search results
```