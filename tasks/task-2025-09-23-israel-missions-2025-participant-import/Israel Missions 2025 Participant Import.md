# Task: Israel Missions 2025 Participant Import
**Created**: 2025-09-23 | **Status**: Business Review

## GATE 1: Business Requirements Approval (MANDATORY)
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-23

### Business Context
Ensure Israel Missions 2025 participant data from Google Form responses is safely integrated into the production Airtable Participants table.

### Primary Objective
Establish a reliable mapping and ingestion workflow that adds each CSV participant record to Airtable without risking data corruption.

### Use Cases
1. **CSV Mapping Workflow**
   - **Acceptance Criteria**: Every required Airtable field is populated from the CSV, defaulted, or explicitly flagged for manual follow-up before import.
2. **Participant Import Execution**
   - **Acceptance Criteria**: Script runs against production Airtable, logs success/failure per record, skips duplicates based on configured key, and never overwrites existing data without confirmation logic.

### Success Metrics
- [ ] 100% of CSV rows produce validated Airtable payloads without missing required fields.
- [ ] Script completes without creating duplicate or malformed participant records, confirmed by spot-checking and import log review.

### Constraints
- Must preserve integrity of the live Airtable production base.
- CSV schema must be mapped to existing Airtable fields; any mismatches documented before execution.
- Solution should support dry-run mode for verification prior to live inserts.

## GATE 2: Test Plan Review & Approval (MANDATORY)
**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-23

### Test Coverage Strategy
Target: 90%+ coverage focused on CSV-to-Airtable mapping validation, safe write sequencing, and duplicate prevention logic.

### Test Categories
- **Business Logic Tests**
  - [ ] Mapping populates all required Airtable fields for a representative CSV row.
  - [ ] Validation rejects rows missing critical identifiers (e.g., email, full name).
  - [ ] Duplicate-detection logic correctly flags existing participants.
- **State Transition Tests**
  - [ ] Dry-run → live-run mode transition retains validated payloads without mutation.
  - [ ] Per-record insert sequence advances to next record only after success/failure logging.
  - [ ] Error state returns the script to idle without partial writes.
- **Error Handling Tests**
  - [ ] Airtable API failure triggers retry/backoff without duplicate writes.
  - [ ] Malformed CSV row logs error and continues processing remaining rows.
  - [ ] Network interruption yields graceful abort with resume guidance.
- **Integration Tests**
  - [ ] Airtable client mock ensures field mapping produces expected payload structure.
  - [ ] Repository layer writes a single record with correct field/value pairs.
  - [ ] End-to-end dry-run writes nothing but outputs comprehensive plan.
- **User Interaction Tests**
  - [ ] CLI prompts acknowledge dry-run vs live confirmation.
  - [ ] Logging output reports per-record status in human-readable format.
  - [ ] Summary report enumerates successes, skips, and failures for post-run review.

### Test-to-Requirement Mapping
- Business Requirement 1 → Tests: Mapping populates required fields; Validation rejects missing identifiers; Airtable client mock payload structure.
- Business Requirement 2 → Tests: Duplicate-detection logic; Per-record sequencing; API failure handling; Dry-run confirmation; Summary reporting.

## Knowledge Gaps
- Confirm CSV headers beyond the sample rows (need full schema to ensure no hidden fields).
- Determine authoritative duplicate key (ContactInformation, FullNameRU, or combination) that aligns with prod Airtable policies.
- Validate whether gender/role values in CSV match Airtable single-select option values or require normalization.
- Clarify if Age should be computed from DateOfBirth or sourced directly.

## Technical Requirements
- [ ] Produce an explicit column-to-field mapping reference stored alongside existing Airtable field documentation.
- [ ] Implement an import script with dry-run mode, idempotent duplicate checks, and structured logging.
- [ ] Ensure script relies on repository/domain models rather than raw API calls for consistency.
- [ ] Provide automated tests covering mapping, deduplication, and dry-run reporting using mocked Airtable client.
- [ ] Document execution steps, environment variables, and safety guidelines for operators.

## Implementation Steps & Change Log
- [ ] Step 1: Author mapping reference and validation helpers
  - [ ] Sub-step 1.1: Capture CSV→Airtable mapping definition
    - **Directory**: `docs/data-integration/`
    - **Files to create/modify**: `docs/data-integration/israel-missions-2025-mapping.md`
    - **Accept**: Document lists each CSV column, target Airtable field, transformation/normalization notes, and unresolved gaps.
    - **Tests**: `tests/unit/test_docs/test_israel_missions_mapping.py`
    - **Done**: PR includes doc with approved mapping, unit test validates mapping dictionary constants.
    - **Changelog**: docs/data-integration/israel-missions-2025-mapping.md:1
  - [ ] Sub-step 1.2: Introduce mapping constants for reuse
    - **Directory**: `src/data/`
    - **Files to create/modify**: `src/data/importers/israel_missions_mapping.py`
    - **Accept**: Module exposes typed mapping dict plus normalization helpers (gender/role/size sanitizers).
    - **Tests**: `tests/unit/test_data/test_importers/test_israel_missions_mapping.py`
    - **Done**: Tests assert mapping covers required fields and handles normalization edge cases.
    - **Changelog**: src/data/importers/israel_missions_mapping.py:1-200
- [ ] Step 2: Build import workflow with safeguards
  - [ ] Sub-step 2.1: Implement importer service
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/israel_missions_import_service.py`
    - **Accept**: Service parses CSV rows, applies mapping, enforces duplicate policy, supports dry-run/live modes, yields per-row results.
    - **Tests**: `tests/unit/test_services/test_israel_missions_import_service.py`
    - **Done**: Unit tests simulate success, validation failure, duplicate skip, and API error retry.
    - **Changelog**: src/services/israel_missions_import_service.py:1-300
  - [ ] Sub-step 2.2: Add CLI entry point script
    - **Directory**: `scripts/`
    - **Files to create/modify**: `scripts/import_israel_missions_participants.py`
    - **Accept**: CLI accepts CSV path, --dry-run flag, optional rate limit override, and writes human-readable summary log.
    - **Tests**: `tests/integration/test_scripts/test_import_israel_missions_participants.py`
    - **Done**: Integration test uses fake repo to verify CLI orchestrates dry-run vs live flow without touching real Airtable.
    - **Changelog**: scripts/import_israel_missions_participants.py:1-200
- [ ] Step 3: Operationalize safely
  - [ ] Sub-step 3.1: Add operator guide and runbook
    - **Directory**: `docs/development/`
    - **Files to create/modify**: `docs/development/israel-missions-import-guide.md`
    - **Accept**: Runbook outlines prerequisites, dry-run verification checklist, live execution steps, rollback guidance.
    - **Tests**: `tests/unit/test_docs/test_israel_missions_import_guide.py`
    - **Done**: Doc linked from README or relevant index; test ensures commands referenced exist / pass lint (doctest-style or schema validation).
    - **Changelog**: docs/development/israel-missions-import-guide.md:1-120
  - [ ] Sub-step 3.2: Wire task references into project index
    - **Directory**: `project_index.json`
    - **Files to create/modify**: `project_index.json`
    - **Accept**: Index lists new docs/scripts ensuring discoverability.
    - **Tests**: `tests/unit/test_project_index.py`
    - **Done**: Test confirms new entries present with correct relative paths.
    - **Changelog**: project_index.json:1-400

### Constraints
- Respect Airtable API rate limits (5 req/sec) and implement adaptive sleep on retry.
- No destructive updates: importer may only create new records; updates require explicit future scope.
- Script must default to dry-run; live mode requires `--confirm-live` style acknowledgement.
- Logging should avoid leaking sensitive data (truncate contact info in logs).

## Linear / Tracking
- **Linear Issue**: Pending creation after Technical Plan Review approval.
- **Next Gate**: Technical Plan Review (Plan Reviewer agent).

## Notes for Other Devs
- Consider seeding dry-run output with anonymized sample data to help stakeholders validate before production run.
- Coordinate run timing with Airtable maintenance window to avoid simultaneous manual edits.
