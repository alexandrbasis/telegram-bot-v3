# Task: Bot Access Approval Workflow
**Created**: 2025-09-22 | **Status**: Implementation Complete | **Started**: 2025-09-23 | **Completed**: 2025-09-23

## Tracking & Progress
### Linear Issue
- **ID**: AGB-67
- **URL**: https://linear.app/alexandrbasis/issue/AGB-67/bot-access-approval-workflow

### PR Details
- **Branch**: feature/agb-67-bot-access-approval-workflow
- **PR URL**: [Will be added during implementation]
- **Status**: Draft

## Business Requirements
**Status**: ✅ Approved | **Approved by**: Alexandr Basis | **Date**: 2025-09-22

### Business Context
Admins can review and approve new bot users directly in Telegram without modifying deployment configuration files.

### Primary Objective
Deliver an in-bot approval workflow that captures, tracks, and resolves user access requests from submission through approval or denial.

### Use Cases
1. **Pending user requests access**  
   - Given a first-time user starts the bot, when they request access, then the system records a pending request, confirms receipt to the user, and notifies admins.
   - Given an admin opens the pending requests list, when they approve the user, then the requester is promoted to approved status, informed via message, and can immediately use bot features.
2. **Admin denies or revisits a request**  
   - Given an admin views a pending request, when they deny it, then the requester receives a courteous denial message with next steps, and the record is marked as denied with the acting admin recorded.
   - Given an admin re-opens an existing request, when they switch the status (e.g., denied → approved), then the audit log captures the change and the user receives the updated decision.

### Success Metrics
- [ ] 100% of new access requests funnel through the in-bot workflow (no manual config changes) during the first full release cycle.
- [ ] Median approval turnaround time < 1 hour after notification (tracked via request timestamps) within two weeks of launch.

### Constraints
- Airtable must expose a new `BotAccessRequests` table reachable with existing API credentials and matching the schema defined below.
- Approval and denial messaging must support both Russian and English phrasing consistent with current bot localization.
- Deployment must avoid downtime; migrations of credentials or environment variables should be backward compatible until rollout completes.

### Airtable Table Schema
| Field Name | Field ID | Type | Description |
|------------|----------|------|-------------|
| TelegramUserId | fldeiF3gxg4fZMirc | Number (Integer) | Primary key storing the Telegram user ID for lookup and uniqueness enforcement. |
| TelegramUsername | fld1RzNGWTGl8fSE4 | Single line text | Telegram username captured without the `@` prefix; optional if the user has none. |
| Status | fldcuRa8qeUDKY3hN | Single select (Pending, Approved, Denied) | Tracks the current request state; defaults to `Pending` on creation. |
| AccessLevel | fldRBCoHwrJ87hdjr | Single select (VIEWER, COORDINATOR, ADMIN) | Effective permissions granted after approval; defaults to `VIEWER`. |

**Views & Indexing**
- Default view filtered to `Status = Pending` sorted by `TelegramUserId` ascending for admin queue.
- Secondary view filtered to `Status = Approved` for quick roster of active users.

**Configuration Notes**
- Primary Airtable view: `Grid view` (viwVDrguxKWbRS9Xz) used for admin queue.
- Register the field IDs above in `src/config/field_mappings.py` under a new `BotAccessRequests` mapping section (table ID `tblQWWEcHx9sfhsgN`).
- Add `AIRTABLE_ACCESS_REQUESTS_TABLE_NAME=BotAccessRequests` and `AIRTABLE_ACCESS_REQUESTS_TABLE_ID=tblQWWEcHx9sfhsgN` to environment/config so the repository can resolve IDs.

## Test Plan
**Status**: ✅ Approved | **Approved by**: Alexandr Basis | **Date**: 2025-09-22

### Test Coverage Strategy
Target: 90%+ coverage across all implementation areas

### Test Categories
#### Business Logic Tests
- [ ] `tests/unit/test_services/test_access_request_service.py::test_submit_request_creates_pending_record`
- [ ] `tests/unit/test_services/test_access_request_service.py::test_approve_request_transitions_state`

#### State Transition Tests
- [ ] `tests/integration/test_bot_handlers/test_admin_requests.py::test_admin_flows_through_pending_to_approved`
- [ ] `tests/integration/test_bot_handlers/test_admin_requests.py::test_denial_flow_and_audit_logging`
- [ ] `tests/integration/test_bot_handlers/test_admin_requests.py::test_reapproval_updates_status`

#### Error Handling Tests
- [ ] `tests/unit/test_services/test_access_request_service.py::test_submit_request_handles_airtable_failure`
- [ ] `tests/unit/test_bot_handlers/test_admin_requests_errors.py::test_invalid_callback_data_rejected`
- [ ] `tests/unit/test_bot_handlers/test_admin_requests_errors.py::test_notification_failure_retries`

#### Integration Tests
- [ ] `tests/integration/test_data/test_airtable/test_user_access_repository.py::test_repository_crud_roundtrip`
- [ ] `tests/integration/test_data/test_airtable/test_user_access_repository.py::test_status_filters`
- [ ] `tests/integration/test_notifications/test_admin_alerts.py::test_admin_notified_on_new_request`

#### User Interaction Tests
- [ ] `tests/integration/test_bot_handlers/test_user_onboarding_access.py::test_first_time_user_gets_pending_message`
- [ ] `tests/integration/test_bot_handlers/test_user_onboarding_access.py::test_user_receives_approval_message`
- [ ] `tests/integration/test_bot_handlers/test_user_onboarding_access.py::test_denied_user_receives_guidance`

### Test-to-Requirement Mapping
- Business Requirement 1 → Tests: `test_submit_request_creates_pending_record`, `test_admin_flows_through_pending_to_approved`, `test_user_receives_approval_message`
- Business Requirement 2 → Tests: `test_denial_flow_and_audit_logging`, `test_reapproval_updates_status`, `test_denied_user_receives_guidance`

## TECHNICAL TASK
**Status**: ✅ Plan Reviewed | **Reviewed by**: Plan Reviewer Agent | **Date**: 2025-09-22

### Technical Requirements
- [ ] Provide Airtable-backed persistence for user access requests with CRUD operations, status fields, audit metadata, and indexing by Telegram user ID.
- [ ] Implement admin-only Telegram command handlers and keyboards to list, approve, deny, and revisit access requests with optimistic concurrency safety.
- [ ] Send localized notifications to both admins and requesters, leveraging existing logging and error handling patterns.
- [ ] Ensure onboarding flow integrates with access control checks, gating main features until approval is confirmed.

### Implementation Steps & Change Log
- [x] ✅ Step 1: Establish user access request data layer - Completed 2025-09-23
  - [x] ✅ Sub-step 1.1: Introduce models and repositories for Airtable access requests - Completed 2025-09-23
    - **Directory**: `src/data/`, `src/models/`, `src/config/`
    - **Files created/modified**:
      - `src/models/user_access_request.py:1-59` - UserAccessRequest model with enums
      - `src/data/repositories/user_access_repository.py:1-139` - Abstract repository interface
      - `src/data/airtable/airtable_user_access_repo.py:1-270` - Airtable implementation with field mapping
      - `src/config/field_mappings.py:605-733` - BotAccessRequestsFieldMapping configuration
      - `src/config/field_mappings/__init__.py:35,44,53,64,67` - Export new mapping class
      - `src/models/__init__.py:1` - Updated module description
    - **Accept**: ✅ Repository supports CRUD operations, status filtering, approve/deny with audit metadata, proper Airtable field mapping with display value conversion
    - **Tests**: `tests/unit/test_models/test_user_access_request.py` (13 tests), `tests/unit/test_data/test_airtable/test_user_access_repository.py` (9 tests)
    - **Done**: ✅ All 22 tests passing - `pytest tests/unit/test_models/test_user_access_request.py tests/unit/test_data/test_airtable/test_user_access_repository.py`
    - **Coverage**: Model 100%, Repository 81% - Comprehensive TDD implementation
    - **Changelog**:
      - **Files**: `src/models/user_access_request.py:1-59` - Pydantic model with AccessLevel/AccessRequestStatus enums, timezone-aware datetime handling
      - **Files**: `src/data/repositories/user_access_repository.py:1-139` - Abstract repository with async CRUD interface
      - **Files**: `src/data/airtable/airtable_user_access_repo.py:1-270` - Full Airtable integration with proper enum-to-display-value mapping
      - **Files**: `src/config/field_mappings.py:605-733` - Complete field mapping with table/view configuration matching task specifications
      - **Summary**: Established complete data layer for user access requests with comprehensive test coverage
      - **Impact**: Enables bot access approval workflow with persistent Airtable storage and audit trails
      - **Tests**: 22 comprehensive tests covering model validation, repository CRUD, error handling, and field mapping integration
      - **Verification**: All tests pass with high coverage, proper enum handling, and Airtable field ID translation
- [x] ✅ Step 2: Add bot onboarding capture and admin review flows - Completed 2025-09-23
  - [x] ✅ Sub-step 2.1: Update handlers and services to capture requests and expose `/requests` - Completed 2025-09-23
    - **Directory**: `src/bot/handlers/`, `src/services/`
    - **Files created/modified**:
      - `src/services/access_request_service.py:1-260` - Business logic service with request management, approval/denial workflows
      - `src/bot/handlers/auth_handlers.py:1-237` - User onboarding, access control decorators, start command handler
      - `src/bot/handlers/admin_handlers.py:71-346` - Admin `/requests` command, callback handling, approval/denial actions
    - **Accept**: ✅ All acceptance criteria met - First-time users get pending message, `/requests` shows paginated interface (5 per page), callback format `access:{action}:{record_id}` implemented, navigation buttons with state management
    - **Tests**: `tests/unit/test_services/test_access_request_service.py` (11 tests), `tests/integration/test_bot_handlers/test_user_onboarding_access.py` (6 tests), `tests/integration/test_bot_handlers/test_admin_requests.py` (5 tests)
    - **Done**: ✅ All 22 tests passing - `pytest tests/unit/test_services/test_access_request_service.py tests/integration/test_bot_handlers/test_user_onboarding_access.py tests/integration/test_bot_handlers/test_admin_requests.py`
    - **Coverage**: AccessRequestService 77%, comprehensive integration test coverage
    - **Changelog**:
      - **Files**: `src/services/access_request_service.py:1-260` - Complete business logic service with CRUD operations, approval workflows, admin validation
      - **Files**: `src/bot/handlers/auth_handlers.py:1-237` - User access control system with decorators, start command handling all user states (new/pending/approved/denied)
      - **Files**: `src/bot/handlers/admin_handlers.py:71-346` - Admin interface with paginated `/requests` command, inline keyboard callbacks, approve/deny workflows
      - **Summary**: Implemented complete bot interface for user onboarding and admin review with comprehensive access control
      - **Impact**: Users can request access via `/start`, admins can review via `/requests` with full approval/denial workflow
      - **Tests**: 22 comprehensive tests covering service logic, user flows, admin callbacks, pagination, and error handling
      - **Verification**: All tests pass, TDD methodology followed with Red-Green-Refactor cycles, robust error handling and state management
- [x] ✅ Step 3: Implement notifications, localization, and logging - Completed 2025-09-23
  - [x] ✅ Sub-step 3.1: Wire notification service and localization strings - Completed 2025-09-23
    - **Directory**: `src/services/`, `src/bot/`, `src/utils/`, `src/main.py`
    - **Files created/modified**:
      - `src/services/notification_service.py:1-219` - Complete notification service with retry mechanism, localization support, admin alerts
      - `src/bot/messages.py:9-47` - Localized access request messages for Russian/English support
      - `src/utils/auth_utils.py:63-157` - Enhanced auth utils with Airtable integration, dual-source authorization
      - `src/bot/handlers/auth_handlers.py:13-18,52-91` - Integrated notification service and localized messages in start handler
      - `src/bot/handlers/admin_handlers.py:17-19,271-290,288-307` - Integrated notification service in approval/denial workflows
      - `src/main.py:17,20,143-159` - Registered access control handlers: start, requests, callback handlers
    - **Accept**: ✅ All acceptance criteria met - Admins receive immediate notifications on new requests, users receive localized messages, auth utils combine env/Airtable sources, comprehensive error handling and retry logic
    - **Tests**: `tests/unit/test_services/test_notification_service.py` (11 tests), `tests/integration/test_notifications/test_admin_alerts.py` (7 tests)
    - **Done**: ✅ All 18 tests passing - `pytest tests/unit/test_services/test_notification_service.py tests/integration/test_notifications/test_admin_alerts.py`
    - **Coverage**: NotificationService 87%, comprehensive integration test coverage with retry mechanisms
    - **Changelog**:
      - **Files**: `src/services/notification_service.py:1-219` - Complete notification service with concurrent admin alerts, user decision notifications, exponential backoff retry, Russian/English localization
      - **Files**: `src/bot/messages.py:9-47` - Added AccessRequestMessages class with localized templates for all user interactions and admin notifications
      - **Files**: `src/utils/auth_utils.py:63-157` - Enhanced auth utilities with async Airtable integration, dual-source authorization (config admins + database users)
      - **Files**: `src/bot/handlers/auth_handlers.py:13-18,52-91` - Integrated notification service in start handler, replaced hardcoded messages with localized templates, real-time admin notifications
      - **Files**: `src/bot/handlers/admin_handlers.py:17-19,271-290,288-307` - Integrated notification service in admin approval/denial workflows with proper error handling
      - **Files**: `src/main.py:17,20,143-159` - Registered access control handlers in bot application: CommandHandler for start/requests, CallbackQueryHandler for approve/deny actions
      - **Summary**: Complete access control workflow with real-time notifications, localization, and comprehensive error handling
      - **Impact**: Full end-to-end bot access approval system - users request via /start, admins review via /requests, all parties receive immediate notifications
      - **Tests**: 18 comprehensive tests covering notification service, admin alerts, retry mechanisms, localization, and error handling
      - **Verification**: All access control tests passing (62 total), notification service fully integrated, admin workflows functional, comprehensive TDD implementation

### Localization Templates
- Pending (RU): "Запрос на доступ принят. Мы уведомим вас, как только админ его обработает."
- Pending (EN): "Your access request has been recorded. We'll notify you as soon as an admin reviews it."
- Approved (RU): "Доступ подтверждён! Ваша роль: {access_level}."
- Approved (EN): "You're all set! Assigned access level: {access_level}."
- Denied (RU): "К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором."
- Denied (EN): "We weren't able to approve your access right now. Contact an admin if you believe this is a mistake."
- Admin alert (RU): "Новый запрос на доступ: {display_name} (@{username} / {user_id})."
- Admin alert (EN): "New access request from {display_name} (@{username} / {user_id})."
- Decision footer (RU): append `Комментарий администратора: {notes}` when notes supplied.
- Decision footer (EN): append `Admin note: {notes}` when notes supplied.

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-22
**Decision**: No Split Needed
**Reasoning**: Scope remains cohesive around a single approval workflow; dependencies between data layer, handlers, and notifications are tightly coupled and manageable within one implementation effort.

## Knowledge Gaps
- Confirm Airtable base permissions allow maintaining the `BotAccessRequests` table (ID `tblQWWEcHx9sfhsgN`) and that AccessLevel choices remain aligned with env-configured viewer/coordinator/admin roles (VIEWER/COORDINATOR/ADMIN).
- Decide whether admin notifications should also be mirrored to Slack/email in addition to Telegram alerts.
- Validate operational process for cleaning up stale denied requests older than 90 days (manual vs automated).

## 🔄 HANDOVER TO NEXT DEVELOPER

### Current Status
**COMPLETED**: Steps 1 & 2 (Data Layer + Bot Handlers) - ✅ 44 tests passing
**REMAINING**: Step 3 (Notifications & Localization) + Final Integration

### What's Been Implemented
✅ **Complete Data Foundation**
- UserAccessRequest model with full Pydantic validation
- AirtableUserAccessRepository with CRUD operations
- BotAccessRequestsFieldMapping with proper field ID mappings
- All tests passing (22 tests) with high coverage

✅ **Complete Bot Interface**
- User onboarding flow via `/start` command with status-based responses
- Admin review interface via `/requests` command with pagination
- Access control decorators (`@require_access`, `@require_admin_access`)
- Callback handling for approve/deny actions with user notifications
- All tests passing (22 tests) covering user flows and admin workflows

### What Needs To Be Done (Step 3)

**CRITICAL**: The implementation is 95% complete but missing key integration pieces:

#### 3.1 Admin Notification System
**File**: `src/services/notification_service.py` (needs creation)
- Trigger admin alerts when new requests are submitted
- Currently logged in `auth_handlers.py:79` but not sent to admins
- Use existing admin list from settings to broadcast notifications

#### 3.2 Localization Integration
**Files**: Update existing `src/locale/messages.py` or create new localization structure
- Messages are hardcoded in Russian in handlers
- Need to support both RU/EN based on user preferences
- Templates defined in task spec (lines 127-137)

#### 3.3 Auth Utils Integration
**File**: `src/utils/auth_utils.py` (needs updating)
- Current implementation uses simple username pattern matching
- Need to integrate with existing admin configuration
- Combine env-configured admins with Airtable approved records

#### 3.4 Main Application Integration
**File**: `src/main.py` (needs handler registration)
- Register new handlers: `start_command_handler`, `requests_command_handler`, `access_callback_handler`
- Add to bot dispatcher with appropriate filters
- Ensure proper order in handler registration

### Quick Start for Next Developer

1. **Run existing tests to verify setup**:
   ```bash
   ./venv/bin/pytest tests/unit/test_models/test_user_access_request.py tests/unit/test_data/test_airtable/test_user_access_repository.py tests/unit/test_services/test_access_request_service.py tests/integration/test_bot_handlers/ -v
   ```
   Should show: **44 tests passing**

2. **Key Files to Review**:
   - `src/models/user_access_request.py` - Data model
   - `src/services/access_request_service.py` - Business logic
   - `src/bot/handlers/auth_handlers.py` - User flows
   - `src/bot/handlers/admin_handlers.py` - Admin interface

3. **Test the current implementation** (Step 3 work will be integration-focused):
   - All core functionality exists and is tested
   - Focus on notification service and localization
   - Final integration in main.py

### Architecture Notes
- Clean 3-layer architecture: Data → Service → Handlers
- Repository pattern with abstract interfaces
- Comprehensive TDD implementation with Red-Green-Refactor
- Proper error handling and logging throughout
- Field mapping system handles Airtable integration complexity

### Integration Points for Step 3
1. **Notification Service**: Hook into `auth_handlers.py:79` TODO comment
2. **Localization**: Replace hardcoded Russian strings in handlers
3. **Auth Integration**: Update `auth_handlers.py:165` admin validation
4. **Handler Registration**: Add to `src/main.py` bot setup

## Notes for Other Devs (Implementation Notes)
- Coordinate rollout so existing admin list remains authoritative until new workflow is live; consider feature flagging `/requests` command during beta.
- Review rate limiting implications if notification volume increases; update Airtable throttling configuration if necessary.
- All enum handling uses Pydantic's `use_enum_values=True` for proper Airtable integration
- Callback data format: `access:{action}:{record_id}` where action ∈ {approve, deny}
- Pagination state stored in `context.user_data['requests_page']`
