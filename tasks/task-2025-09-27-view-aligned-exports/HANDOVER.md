# 🔄 View-Aligned Exports Implementation Handover

## 📋 **PROJECT STATUS**

**Current Status**: Foundation Phase Complete (Steps 1-3 of 8)
**Next Phase**: Export Service Integration (Steps 4-8)
**Branch**: `feature/agb-74-view-aligned-exports`
**Linear Issue**: [AGB-74](https://linear.app/alexandrbasis/issue/AGB-74/view-aligned-exports-align-bot-exports-with-airtable-views-for)

---

## ✅ **COMPLETED WORK (Steps 1-3)**

### **Step 1: Repository Interface Standardization**
- ✅ Added `list_view_records(view: str)` abstract method to ROE and Bible Readers repository interfaces
- ✅ Ensured consistency with existing Participant repository interface
- ✅ Updated all repository tests with mock implementations
- **Files Modified**:
  - `src/data/repositories/roe_repository.py:151-165`
  - `src/data/repositories/bible_readers_repository.py:137-151`
  - Test files with mock updates
- **Tests**: 9/9 repository interface tests passing

### **Step 2: Concrete View Support Implementation**
- ✅ Implemented `list_view_records()` in `AirtableROERepository`
- ✅ Implemented `list_view_records()` in `AirtableBibleReadersRepository`
- ✅ Both follow identical pattern with proper error handling and logging
- **Files Modified**:
  - `src/data/airtable/airtable_roe_repo.py:349-371`
  - `src/data/airtable/airtable_bible_readers_repo.py:317-339`
- **Tests**: 26/26 ROE + 27/27 Bible Readers repository tests passing

### **Step 3: View Configuration Management**
- ✅ Added configurable view names to `DatabaseSettings`
- ✅ Environment variables: `AIRTABLE_PARTICIPANT_EXPORT_VIEW`, `AIRTABLE_ROE_EXPORT_VIEW`, `AIRTABLE_BIBLE_READERS_EXPORT_VIEW`
- ✅ Default values: `Кандидаты`, `РОЕ: Расписание`, `Чтецы: Расписание`
- ✅ Comprehensive validation and TDD tests
- **Files Modified**:
  - `src/config/settings.py:134-143,187-195`
  - `tests/unit/test_config/test_settings.py:818-863`
- **Tests**: 49/49 settings tests passing

---

## 🎯 **REMAINING WORK (Steps 4-8)**

### **Step 4: Export Utilities Enhancement** ⚠️ **NEXT TO IMPLEMENT**
- **Goal**: Extend existing export utilities to handle view-based column ordering
- **Key Challenge**: Preserve `#` line numbers as first column while respecting view field order
- **Files to Modify**: `src/utils/export_utils.py`
- **Pattern**: Examine existing utilities and extend to derive column order from Airtable view records

### **Step 5: Participant Export Service Update**
- **Goal**: Update participant export to use configured view `Кандидаты`
- **Files to Modify**: `src/services/participant_export_service.py`
- **Pattern**: Replace `list_all()` calls with `list_view_records(settings.participant_export_view)`

### **Step 6: ROE Export Service Update**
- **Goal**: Update ROE export to use configured view `РОЕ: Расписание`
- **Files to Modify**: `src/services/roe_export_service.py`
- **Pattern**: Use `list_view_records(settings.roe_export_view)` for data retrieval

### **Step 7: Bible Readers Export Service Update**
- **Goal**: Update Bible Readers export to use configured view `Чтецы: Расписание`
- **Files to Modify**: `src/services/bible_readers_export_service.py`
- **Pattern**: Use `list_view_records(settings.bible_readers_export_view)` for data retrieval

### **Step 8: Logging and Documentation**
- **Goal**: Enhanced logging for view usage and documentation updates
- **Files to Modify**: Handler files, `CHANGELOG.md`, documentation

---

## 🔧 **TECHNICAL GUIDANCE**

### **Architecture Pattern Established**
```python
# Repository Layer (✅ COMPLETE)
async def list_view_records(self, view: str) -> List[Dict[str, Any]]:
    """Retrieve raw Airtable records for a specific view."""
    try:
        records = await self.client.list_records(view=view)
        return records
    except AirtableAPIError as e:
        raise RepositoryError(f"Failed to list records for view '{view}': {e}")

# Configuration Layer (✅ COMPLETE)
@dataclass
class DatabaseSettings:
    participant_export_view: str = field(default_factory=lambda: os.getenv("AIRTABLE_PARTICIPANT_EXPORT_VIEW", "Кандидаты"))
    # ... other view configs
```

### **TDD Approach Established**
1. **RED**: Write failing test first
2. **GREEN**: Implement minimal code to pass
3. **REFACTOR**: Clean up while maintaining green tests
4. **Pattern**: Every function has comprehensive success and error case tests

### **Key Implementation Notes**
- All view names use Russian text as per business requirements
- Error handling follows established repository patterns
- Logging includes view name context for debugging
- Environment variable support enables deployment flexibility
- Line number utilities must be preserved in export flows

---

## 🧪 **TESTING STRATEGY**

### **Test Coverage Status**
- **Repository Tests**: 62/62 passing (includes new view functionality)
- **Settings Tests**: 49/49 passing (includes view configuration)
- **Total Foundation Tests**: 111/111 passing ✅

### **Testing Patterns to Follow**
```python
# Service Layer Test Pattern (for Steps 5-7)
async def test_export_uses_configured_view(self, service, mock_repository, mock_settings):
    """Test that export service uses configured view name."""
    mock_settings.participant_export_view = "Custom View"
    mock_repository.list_view_records.return_value = [mock_record]

    await service.export_to_csv_async()

    mock_repository.list_view_records.assert_called_once_with("Custom View")

# Utility Layer Test Pattern (for Step 4)
def test_view_header_ordering_preserves_line_numbers(self):
    """Test that view-based headers include # as first column."""
    view_records = [{"fields": {"Field1": "val1", "Field2": "val2"}}]

    headers = extract_view_headers(view_records)

    assert headers[0] == "#"
    assert "Field1" in headers
    assert "Field2" in headers
```

---

## 📁 **KEY FILE LOCATIONS**

### **Already Modified (Foundation)**
```
src/data/repositories/
├── roe_repository.py                    ✅ Abstract method added
├── bible_readers_repository.py          ✅ Abstract method added

src/data/airtable/
├── airtable_roe_repo.py                 ✅ Concrete implementation
├── airtable_bible_readers_repo.py       ✅ Concrete implementation

src/config/
├── settings.py                          ✅ View configuration added

tests/unit/
├── test_data/test_repositories/         ✅ Interface tests updated
├── test_data/test_airtable/             ✅ Implementation tests added
├── test_config/test_settings.py         ✅ Configuration tests added
```

### **Next to Modify (Export Services)**
```
src/utils/
├── export_utils.py                      ⚠️ STEP 4: Extend for view ordering

src/services/
├── participant_export_service.py        ⚠️ STEP 5: Use participant view
├── roe_export_service.py                ⚠️ STEP 6: Use ROE view
├── bible_readers_export_service.py      ⚠️ STEP 7: Use Bible Readers view

src/bot/handlers/
├── export_conversation_handlers.py      ⚠️ STEP 8: Enhanced logging

docs/
├── CHANGELOG.md                         ⚠️ STEP 8: Document changes
```

---

## 🚀 **QUICK START FOR NEXT DEVELOPER**

### **1. Environment Setup**
```bash
cd /Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3
git checkout feature/agb-74-view-aligned-exports
source venv/bin/activate
```

### **2. Verify Foundation**
```bash
# Confirm all foundation tests pass
./venv/bin/pytest tests/unit/test_data/test_repositories/ -v
./venv/bin/pytest tests/unit/test_data/test_airtable/ -v
./venv/bin/pytest tests/unit/test_config/test_settings.py -v

# Should see: 111/111 tests passing
```

### **3. Start Step 4 (Export Utilities)**
```bash
# Examine current export utilities
cat src/utils/export_utils.py

# Look at how line numbers are currently handled
grep -r "format_line_number" src/

# Start with TDD - write failing test first
# Focus on view header extraction while preserving # column
```

### **4. Reference Existing Patterns**
- **Repository Pattern**: See `src/data/airtable/airtable_participant_repo.py:list_view_records`
- **Configuration Usage**: See `src/config/settings.py:get_airtable_config`
- **Export Service Pattern**: See `src/services/participant_export_service.py`
- **Error Handling**: Follow established `RepositoryError` patterns

---

## ⚠️ **CRITICAL REQUIREMENTS**

### **Business Requirements (Must Preserve)**
1. **Line Numbers**: `#` column must remain first in all exports
2. **View Ordering**: Column order must match Airtable view 1:1 (after # column)
3. **View Names**: Use exact Russian names per business requirements
4. **Backward Compatibility**: Existing export functionality must not break

### **Technical Requirements (Must Follow)**
1. **TDD Approach**: Red-Green-Refactor for all new code
2. **Error Handling**: Graceful degradation if views unavailable
3. **Logging**: Include view context in debug/error messages
4. **Configuration**: Use settings from `DatabaseSettings` class
5. **Testing**: Maintain 90%+ test coverage

---

## 📞 **SUPPORT RESOURCES**

### **Task Documentation**
- **Main Task**: `tasks/task-2025-09-27-view-aligned-exports/View-Aligned Exports.md`
- **Linear Issue**: https://linear.app/alexandrbasis/issue/AGB-74/
- **Implementation Guide**: This handover document

### **Code References**
- **Existing Export Logic**: `src/services/participant_export_service.py`
- **Repository Pattern**: `src/data/airtable/airtable_participant_repo.py`
- **Configuration Pattern**: `src/config/settings.py`
- **Test Patterns**: `tests/unit/test_data/test_airtable/test_airtable_participant_repo.py`

### **Quality Gates**
```bash
# Before any commit, ensure:
./venv/bin/mypy src --no-error-summary      # Type checking
./venv/bin/flake8 src tests                 # Linting
./venv/bin/pytest tests/ -v                 # All tests pass
```

---

## 🎯 **SUCCESS CRITERIA**

### **Technical Completion**
- [ ] All 8 implementation steps marked complete in task document
- [ ] All existing tests continue to pass (no regressions)
- [ ] New functionality has comprehensive test coverage
- [ ] Code follows established patterns and conventions

### **Functional Completion**
- [ ] Candidate exports use `Кандидаты` view with correct column ordering
- [ ] ROE exports use `РОЕ: Расписание` view with correct column ordering
- [ ] Bible Readers exports use `Чтецы: Расписание` view with correct column ordering
- [ ] All exports preserve `#` line numbers as first column
- [ ] Graceful fallback behavior if views unavailable

### **Ready for Review**
- [ ] Task document shows all steps completed
- [ ] Implementation changelog updated
- [ ] PR created with proper description
- [ ] Linear issue updated to "Ready for Review"

---

**Foundation Phase: COMPLETE ✅**
**Next Phase: Export Service Integration**
**Estimated Remaining Effort**: 4-6 hours (Steps 4-8)

**Good luck with the implementation! The foundation is solid and well-tested.** 🚀