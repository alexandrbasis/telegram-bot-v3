# Task: Bot Access Approval Workflow
**Created**: 2025-09-22 | **Status**: Ready for Implementation

## Tracking & Progress
### Linear Issue
- **ID**: AGB-67
- **URL**: https://linear.app/alexandrbasis/issue/AGB-67/bot-access-approval-workflow

### PR Details
- **Branch**: basisalexandr/agb-67-bot-access-approval-workflow
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
- [ ] Step 1: Establish user access request data layer
  - [ ] Sub-step 1.1: Introduce models and repositories for Airtable access requests
    - **Directory**: `src/data/`
    - **Files to create/modify**: `src/models/user_access_request.py`, `src/data/repositories/user_access_repository.py`, `src/data/airtable/airtable_user_access_repo.py`, `src/services/__init__.py`
    - **Accept**: Repository supports create, list-by-status, approve/deny transitions with approval metadata persisted in Airtable, exposes a `UserAccessRepository` abstract interface mirroring `ParticipantRepository`, and wires field IDs through `src/config/field_mappings.py`.
    - **Tests**: `tests/unit/test_models/test_user_access_request.py`, `tests/unit/test_data/test_airtable/test_user_access_repository.py`
    - **Done**: `pytest tests/unit/test_models/test_user_access_request.py tests/unit/test_data/test_airtable/test_user_access_repository.py`
    - **Changelog**: Populate with file path and line references after implementation.
- [ ] Step 2: Add bot onboarding capture and admin review flows
  - [ ] Sub-step 2.1: Update handlers and services to capture requests and expose `/requests`
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/auth_handlers.py`, `src/bot/handlers/admin_handlers.py`, `src/bot/keyboards/admin_keyboards.py`, `src/services/access_request_service.py`
    - **Accept**: First-time user triggers pending request message; `/requests` shows paginated (5 records per page) pending list with inline callbacks using format `access:{action}:{record_id}` where `{action}` ∈ {`approve`,`deny`,`setlevel`}; navigation buttons (`Prev`, `Next`, `Refresh`) reuse the same pattern and maintain cursor state in `context.user_data`.
    - **Tests**: `tests/integration/test_bot_handlers/test_user_onboarding_access.py`, `tests/integration/test_bot_handlers/test_admin_requests.py`
    - **Done**: `pytest tests/integration/test_bot_handlers/test_user_onboarding_access.py tests/integration/test_bot_handlers/test_admin_requests.py`
    - **Changelog**: Populate with file path and line references after implementation.
- [ ] Step 3: Implement notifications, localization, and logging
  - [ ] Sub-step 3.1: Wire notification service and localization strings
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/notification_service.py`, `src/locale/messages.py`, `src/utils/auth_utils.py`, `src/main.py`
    - **Accept**: Admins receive immediate notification on new request; requesters receive localized pending/approval/denial updates using templates defined below; extend existing `src/utils/auth_utils.py` to combine env-configured viewers/coordinators/admins with approved Airtable records for authorization and AccessLevel enforcement; all notifications log success/failures and retry transient errors.
    - **Tests**: `tests/unit/test_services/test_notification_service.py`, `tests/integration/test_notifications/test_admin_alerts.py`
    - **Done**: `pytest tests/unit/test_services/test_notification_service.py tests/integration/test_notifications/test_admin_alerts.py`
    - **Changelog**: Populate with file path and line references after implementation.

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

## Notes for Other Devs (Optional)
- Coordinate rollout so existing admin list remains authoritative until new workflow is live; consider feature flagging `/requests` command during beta.
- Review rate limiting implications if notification volume increases; update Airtable throttling configuration if necessary.
