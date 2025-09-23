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
- Airtable must expose a new `BotAccessRequests` table (schema to be confirmed) reachable with existing API credentials.
- Approval and denial messaging must support both Russian and English phrasing consistent with current bot localization.
- Deployment must avoid downtime; migrations of credentials or environment variables should be backward compatible until rollout completes.

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
    - **Accept**: Repository supports create, list-by-status, approve/deny transitions with audit metadata persisted in Airtable.
    - **Tests**: `tests/unit/test_models/test_user_access_request.py`, `tests/unit/test_data/test_airtable/test_user_access_repository.py`
    - **Done**: `pytest tests/unit/test_models/test_user_access_request.py tests/unit/test_data/test_airtable/test_user_access_repository.py`
    - **Changelog**: Populate with file path and line references after implementation.
- [ ] Step 2: Add bot onboarding capture and admin review flows
  - [ ] Sub-step 2.1: Update handlers and services to capture requests and expose `/requests`
    - **Directory**: `src/bot/handlers/`
    - **Files to create/modify**: `src/bot/handlers/auth_handlers.py`, `src/bot/handlers/admin_handlers.py`, `src/bot/keyboards/admin_keyboards.py`, `src/services/access_request_service.py`
    - **Accept**: First-time user triggers pending request message; `/requests` shows paginated pending list with approve/deny callbacks.
    - **Tests**: `tests/integration/test_bot_handlers/test_user_onboarding_access.py`, `tests/integration/test_bot_handlers/test_admin_requests.py`
    - **Done**: `pytest tests/integration/test_bot_handlers/test_user_onboarding_access.py tests/integration/test_bot_handlers/test_admin_requests.py`
    - **Changelog**: Populate with file path and line references after implementation.
- [ ] Step 3: Implement notifications, localization, and logging
  - [ ] Sub-step 3.1: Wire notification service and localization strings
    - **Directory**: `src/services/`
    - **Files to create/modify**: `src/services/notification_service.py`, `src/locale/messages.py`, `src/utils/auth_utils.py`, `src/main.py`
    - **Accept**: Admins receive immediate notification on new request; requesters receive localized approval/denial updates with logging entries.
    - **Tests**: `tests/unit/test_services/test_notification_service.py`, `tests/integration/test_notifications/test_admin_alerts.py`
    - **Done**: `pytest tests/unit/test_services/test_notification_service.py tests/integration/test_notifications/test_admin_alerts.py`
    - **Changelog**: Populate with file path and line references after implementation.

### Task Splitting Evaluation
**Status**: ✅ Evaluated | **Evaluated by**: Task Splitter Agent | **Date**: 2025-09-22
**Decision**: No Split Needed
**Reasoning**: Scope remains cohesive around a single approval workflow; dependencies between data layer, handlers, and notifications are tightly coupled and manageable within one implementation effort.

## Knowledge Gaps
- Confirm Airtable table name, schema, and required field IDs for storing access requests and audit metadata.
- Determine finalized Russian/English copy for approval, denial, and pending messages to maintain established tone.
- Validate whether external notification channels (e.g., email, Slack) are needed beyond in-app alerts.

## Notes for Other Devs (Optional)
- Coordinate rollout so existing admin list remains authoritative until new workflow is live; consider feature flagging `/requests` command during beta.
- Review rate limiting implications if notification volume increases; update Airtable throttling configuration if necessary.
