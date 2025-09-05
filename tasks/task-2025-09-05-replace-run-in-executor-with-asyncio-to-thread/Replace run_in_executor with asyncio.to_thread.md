# Task: Replace run_in_executor with asyncio.to_thread for blocking Airtable operations
**Created**: 2025-09-05 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)
**Status**: Awaiting Business Approval | **Created**: 2025-09-05

### Business Context
Increase maintainability and future-compatibility by standardizing on `asyncio.to_thread` for offloading blocking Airtable SDK calls. This reduces boilerplate, aligns with modern asyncio best practices (Py 3.11+), and clarifies intent without changing runtime behavior.

### Primary Objective
Replace all usages of `loop.run_in_executor(None, ...)` with `asyncio.to_thread(...)` in blocking I/O call sites while keeping identical behavior and performance.

### Use Cases
1. Developer readability and consistency: Engineers can more easily reason about thread offloads and reduce lambda/partial noise in code.
   - Acceptance: All targeted sites use `asyncio.to_thread(...)`; no `run_in_executor(None, ...)` remains in `src/`.
2. Future maintenance: Code conforms to modern asyncio patterns, easing upgrades and reducing confusion around event loop access.
   - Acceptance: No reliance on `asyncio.get_event_loop()`/`get_running_loop()` for simple thread offloads in the affected module(s).

### Success Metrics
- [ ] All unit/integration tests pass with no regressions.
- [ ] `rg -n "run_in_executor\(" src` returns 0 matches (after change).

### Constraints
- Keep exact behavior, logging, error handling, and rate-limiting intact.
- Do not introduce new dependencies or change PTB lifecycle.
- Keep type hints and linting clean (mypy/flake8 must pass).

---

## Test Plan (Gate 2 - Approval Required)
**Status**: Awaiting Test Plan Approval | **Created**: 2025-09-05

### Test Coverage Strategy
Leverage existing unit/integration tests for Airtable client and add static verification steps to ensure the refactor doesn’t change behavior.

### Proposed Test Categories
#### Business Logic Tests
- [ ] Existing Airtable client CRUD and listing tests continue to pass unchanged.

#### Error Handling Tests
- [ ] Existing tests covering API failures, network errors, and retry behavior continue to pass.

#### Integration Tests
- [ ] Existing integration tests that exercise Airtable repository flows continue to pass.

#### User Interaction Tests
- [ ] N/A (no user-facing behavior change).

### Static/Tooling Checks
- [ ] `./venv/bin/flake8 src tests` → no new issues.
- [ ] `./venv/bin/mypy src --no-error-summary` → no new issues.
- [ ] `rg -n "run_in_executor\(" src` → zero matches in application code.

### Test-to-Requirement Mapping
- Business Requirement 1 (Readability/Consistency) → Static grep check, code review diffs.
- Business Requirement 2 (No behavior change) → Existing unit/integration test suites passing.

---

## TECHNICAL TASK
**Status**: Business Review (technical work will start after Gates 1 & 2 approvals)

### Technical Requirements
- [ ] Replace `await asyncio.get_running_loop().run_in_executor(None, func)` with `await asyncio.to_thread(func, *args, **kwargs)` at all blocking Airtable SDK call sites.
- [ ] Preserve logging, error wrapping (`AirtableAPIError`), and rate limiting semantics exactly.
- [ ] Maintain type correctness (mypy clean) and style (flake8 clean).
- [ ] No API/signature changes to public methods.

### Implementation Steps & Change Log
- [ ] Step 1: Refactor Airtable client executor calls
  - [ ] Sub-step 1.1: Replace executor calls in `src/data/airtable/airtable_client.py`
    - **Directory**: `src/data/airtable/`
    - **Files to create/modify**: `src/data/airtable/airtable_client.py`
    - **Accept**: No occurrences of `run_in_executor(` remain; all changed to `asyncio.to_thread(...)`
    - **Tests**: `tests/unit/test_data/test_airtable/test_airtable_client.py`
    - **Done**: All tests pass; lints/types clean; `rg -n "run_in_executor\(" src` → 0
    - **Changelog**: Replace calls approximately at lines (indicative ranges):
      - ~150–160: `self.table.schema()`
      - ~182–190: `self.table.create(...)`
      - ~212–220: `self.table.get(record_id)`
      - ~252–260: `self.table.update(record_id, ...)`
      - ~282–290: `self.table.delete(record_id)`
      - ~338–345: `list(self.table.all(**params))`
      - ~377–383: `self.table.batch_create(batch)`
      - ~418–424: `self.table.batch_update(batch)`
      - ~488–494: `self.table.schema()`

- [ ] Step 2: Repo-wide scan & confirm
  - [ ] Sub-step 2.1: Search for any other executor-based offloads
    - **Directory**: `src/`
    - **Files to create/modify**: N/A unless matches found
    - **Accept**: No `run_in_executor(` usage remains in application code
    - **Tests**: Re-run full unit/integration suites
    - **Done**: `rg -n "run_in_executor\(" src` → 0
    - **Changelog**: Document any additional files if found

### Constraints
- Must not alter behavior, performance, or public APIs.
- Keep changes minimal and focused to the targeted refactor.

### Task Splitting Evaluation
**Status**: Evaluated | **Decision**: No Split Needed
**Reasoning**: Small, mechanical refactor in a single module; covered by existing tests.

## Notes for Other Devs (Optional)
- `asyncio.to_thread` is available in 3.9+; consistent with our Python 3.13 runtime.
- No need to interact with event loop directly for simple thread offloads.
- Cancellation semantics remain the same as `run_in_executor` for blocking calls.

