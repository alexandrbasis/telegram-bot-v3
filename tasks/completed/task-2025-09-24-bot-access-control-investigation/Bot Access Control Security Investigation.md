# Task: Bot Access Control Security Investigation
**Created**: 2025-09-24 | **Status**: Business Review

## Business Requirements (Gate 1 - Approval Required)

### Business Context
Critical security vulnerability: unauthorized users can access bot functionality despite not being in authorized user lists (viewers, coordinators, admins)

### Primary Objective
Identify and fix the access control bypass vulnerability to ensure only authorized users can interact with the bot, protecting sensitive participant data and bot functionality

### Use Cases
1. **Unauthorized User Access Prevention**
   - Scenario: User with Telegram ID not present in Airtable `AuthorizedUsers` table attempts to use bot
   - Expected: Bot denies access and shows "unauthorized" message
   - Acceptance Criteria:
     - [ ] Bot retrieves and caches Airtable `AuthorizedUsers` records and checks user ID against them
     - [ ] Non-authorized users receive clear denial message
     - [ ] Access attempt is logged for security audit including Airtable sync metadata

2. **Authorized User Access Flow**
   - Scenario: User with Telegram ID in Airtable `AuthorizedUsers` view uses bot
   - Expected: Bot grants appropriate access based on role
   - Acceptance Criteria:
     - [ ] Bot correctly identifies user role from Airtable `AccessLevel` field
     - [ ] Appropriate commands/features are accessible based on role
     - [ ] Role-based permissions are enforced consistently

3. **Dynamic Authorization Updates**
   - Scenario: Admin adds/removes user from Airtable `AuthorizedUsers` table
   - Expected: Changes take effect without bot restart (automatic sync within TTL or manual refresh trigger)
   - Acceptance Criteria:
     - [ ] Authorization cache refreshes in <60s automatically and on-demand via admin command
     - [ ] No restart required for authorization updates
    - [ ] Clear audit trail of authorization changes captured via bot security audit logs (including Airtable record IDs, `Status`, and `AccessLevel` snapshots)

### Success Metrics
- [ ] 100% of unauthorized access attempts are blocked
- [ ] Zero false positives (authorized users incorrectly denied)
- [ ] Access control verification completes in <100ms
- [ ] Security audit log captures all access attempts
- [ ] All existing authorized users retain their access levels

### Constraints
- Must maintain backward compatibility with existing user lists
- Cannot disrupt service for currently authorized users
- Must complete fix within 24 hours due to security criticality
- Solution must work with current Telegram Bot API limitations
- Must preserve existing role hierarchy (admin > coordinator > viewer)

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-24

---

## Test Plan (Gate 2 - Approval Required)

### Test Coverage Strategy
Target: 95%+ coverage across all access control implementation areas including edge cases and security scenarios

### Proposed Test Categories

#### Business Logic Tests
- [ ] **test_unauthorized_user_blocked**: Verify user ID not in Airtable `AuthorizedUsers` active view is denied access
- [ ] **test_viewer_role_permissions**: Validate viewer-level users from Airtable get appropriate access
- [ ] **test_coordinator_role_permissions**: Validate coordinator-level users get enhanced access
- [ ] **test_admin_role_permissions**: Validate admin users get full access
- [ ] **test_role_hierarchy_enforcement**: Verify admin > coordinator > viewer permission levels sourced from Airtable
- [ ] **test_authorization_check_performance**: Ensure access check completes <100ms when served from cache

#### State Transition Tests
- [ ] **test_unauthorized_to_authorized_flow**: User added to Airtable `AuthorizedUsers` active view gains access after next sync or manual refresh
- [ ] **test_authorized_to_unauthorized_flow**: User removed or status changed in Airtable loses access without restart
- [ ] **test_role_change_transitions**: User AccessLevel updated in Airtable yields correct new permissions
- [ ] **test_bot_restart_auth_persistence**: Authorization state persists across bot restarts and rehydrates from Airtable
- [ ] **test_manual_refresh_command**: Admin `/auth_refresh` command forces immediate cache refresh

#### Error Handling Tests
- [ ] **test_malformed_user_id_handling**: Invalid/malformed Telegram IDs handled gracefully
- [ ] **test_empty_authorized_users_view**: Bot handles Airtable view returning zero active users (defaults to env fallback)
- [ ] **test_duplicate_user_ids_across_sources**: User appearing in Airtable and env fallback gets highest permission level
- [ ] **test_config_loading_failures**: Bot fails safely when Airtable credentials missing and fallback invalid
- [ ] **test_network_timeout_scenarios**: Access checks work during Airtable outages using cached/fallback data
- [ ] **test_sync_retry_backoff**: Authorization sync errors trigger retry with backoff

#### Integration Tests
- [ ] **test_telegram_api_user_verification**: Integration with Telegram's user verification
- [ ] **test_airtable_authorized_users_sync**: Airtable records pulled into cache and applied to handlers
- [ ] **test_environment_variable_fallback**: Authorization fallback lists loaded correctly when Airtable unavailable
- [ ] **test_config_file_integration**: Alternative config file loading works correctly
- [ ] **test_logging_integration**: All access attempts and sync cycles logged to security audit trail
- [ ] **test_manual_refresh_integration**: Admin manual refresh updates cache and unlocks newly authorized user

#### User Interaction Tests
- [ ] **test_unauthorized_user_message**: Unauthorized users receive clear denial message with support contact info
- [ ] **test_authorized_user_welcome**: Authorized users receive appropriate welcome/menu
- [ ] **test_command_filtering_by_role**: Commands filtered based on user role
- [ ] **test_security_audit_logging**: All access attempts logged with timestamp, user ID, result, and sync metadata
- [ ] **test_manual_refresh_feedback**: `/auth_refresh` command returns success/failure details to admin users

#### Security-Specific Tests
- [ ] **test_bypass_attempt_protection**: Common bypass techniques (spoofing, injection) blocked
- [ ] **test_rate_limiting_auth_checks**: Rapid auth check requests handled properly
- [ ] **test_sensitive_data_exposure**: No sensitive auth or Airtable data leaked in error messages
- [ ] **test_timing_attack_protection**: Auth checks have consistent timing regardless of result
- [ ] **test_cache_poisoning_protection**: Cache rejects malformed Airtable records and guards against replay attacks

### Test-to-Requirement Mapping
- **Unauthorized User Access Prevention** → Tests: test_unauthorized_user_blocked, test_unauthorized_user_message, test_bypass_attempt_protection
- **Authorized User Access Flow** → Tests: test_viewer_role_permissions, test_coordinator_role_permissions, test_admin_role_permissions, test_authorized_user_welcome
- **Dynamic Authorization Updates** → Tests: test_unauthorized_to_authorized_flow, test_authorized_to_unauthorized_flow, test_role_change_transitions

**Status**: ✅ Approved | **Approved by**: User | **Date**: 2025-09-24

---

## Tracking & Progress
### Linear Issue
- **ID**: AGB-68
- **URL**: https://linear.app/alexandrbasis/issue/AGB-68/critical-fix-bot-access-control-security-vulnerability
- **Priority**: Urgent
- **Status**: Backlog

### PR Details
- **Branch**: [Will be created during implementation]
- **PR URL**: [Will be added during implementation]
- **Status**: [Not started]

## TECHNICAL TASK
**Status**: Ready for Implementation | **Created**: 2025-09-24

### Investigation Findings

#### Critical Security Vulnerability Identified
After thorough codebase investigation, the root cause of the access control bypass has been identified:

**MAIN ISSUE**: The primary search conversation handler (`src/bot/handlers/search_conversation.py:110-337`) which handles 95% of bot functionality including `/start`, participant search, room search, floor search, and list generation has **ZERO** access control checks.

**CURRENT IMPLEMENTATION**: Only specific admin functions have authorization:
- `src/bot/handlers/export_handlers.py:25` - Uses `is_admin_user()` check
- `src/bot/handlers/export_conversation_handlers.py:47` - Uses `is_admin_user()` check
- `src/bot/handlers/admin_handlers.py:19` - Uses `is_admin_user()` check

**MISSING AUTHORIZATION**: No viewer/coordinator role definitions exist:
- Only `TELEGRAM_ADMIN_IDS` environment variable exists (line `src/config/settings.py:274`)
- No `TELEGRAM_VIEWER_IDS` or `TELEGRAM_COORDINATOR_IDS` variables defined
- No role-based permission system implemented

**ACCESS PATTERNS COMPROMISED**:
- Any Telegram user can use `/start` command
- Any Telegram user can search for participants and access sensitive data
- Any Telegram user can view participant details, room assignments, floor information
- Only export and logging functions are properly protected

- [ ] **R1**: Create comprehensive authorization system with viewer/coordinator/admin roles sourced from Airtable `AuthorizedUsers`
- [ ] **R2**: Implement authorization cache with <60s TTL, manual refresh command, and resilient fallback to environment variables
- [ ] **R3**: Implement access control middleware for all conversation entry points
- [ ] **R4**: Add role-based permission checks throughout the application
- [ ] **R5**: Create environment variable configuration for all user roles as bootstrap/fallback
- [ ] **R6**: Integrate Airtable `AuthorizedUsers` table as the dynamic source of truth for authorization
- [ ] **R7**: Implement security audit logging for sync cycles and access attempts
- [ ] **R8**: Add graceful unauthorized access denial with clear messaging
- [ ] **R9**: Maintain backward compatibility with existing admin functionality and env fallback when Airtable unavailable
- [ ] **R10**: Ensure performance impact is minimal (<100ms access checks) including cache refresh overhead

### Subtask Breakdown Summary

This task has been split into 3 manageable subtasks to enable phased deployment while maintaining security integrity:

1. **Subtask 1: Authorization Foundation** (Steps 1-3, 7)
   - Core authorization infrastructure
   - Role configuration and utilities
   - Access control middleware
   - Environment documentation

2. **Subtask 2: Handler Security Implementation** (Steps 4-5, partial Step 6)
   - Apply authorization to all handlers
   - Secure conversation entry points
   - Role-based feature access

3. **Subtask 3: Security Audit and Testing** (Steps 6, 8)
   - Security audit logging
   - Performance optimization and cache refresh benchmarking
   - Comprehensive testing including Airtable sync scenarios
   - Documentation including operational runbooks for authorization sync

**Deployment Order**: Subtask 1 → Subtask 2 → Subtask 3

### Implementation Steps & Change Log

- [ ] **Step 1: Extend Configuration System** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-authorization-foundation/Authorization Foundation.md`
  - **Description**: Core authorization infrastructure with role-based access control
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: None - foundational component

- [ ] **Step 2: Create Authorization Utilities** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-authorization-foundation/Authorization Foundation.md`
  - **Description**: Authorization utility functions with role hierarchy
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: None - part of foundation

- [ ] **Step 3: Create Access Control Middleware & Authorization Cache** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-authorization-foundation/Authorization Foundation.md`
  - **Description**: Access control decorator/middleware system plus Airtable-backed authorization cache (TTL <60s, manual refresh, env fallback)
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: None - part of foundation

- [ ] **Step 4: Secure Main Entry Points** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-handler-security/Handler Security Implementation.md`
  - **Description**: Apply authorization to all search and entry point handlers
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: Requires subtask-1 (authorization foundation)

- [ ] **Step 5: Secure Additional Handler Files** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-2-handler-security/Handler Security Implementation.md`
  - **Description**: Apply authorization to room, floor, list, and edit handlers
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: Requires subtask-1 (authorization foundation)

- [ ] **Step 6: Implement Security Audit Logging and Sync Observability** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-audit-and-testing/Security Audit and Testing.md`
  - **Description**: Security audit logging service, authorization sync telemetry, and integration
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: Requires subtask-1 and subtask-2

- [ ] **Step 7: Update Environment Configuration** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-1-authorization-foundation/Authorization Foundation.md`
  - **Description**: Environment configuration documentation
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: None - part of foundation

- [ ] **Step 8: Performance Optimization & Testing** → **SPLIT INTO SUBTASK**
  - **Subtask**: `subtask-3-audit-and-testing/Security Audit and Testing.md`
  - **Description**: Performance optimization, authorization cache benchmarking, and comprehensive testing
  - **Linear Issue**: [Will be created for this subtask]
  - **Dependencies**: Requires subtask-1 and subtask-2

### Constraints
- Must maintain 100% backward compatibility with existing admin authorization
- Cannot disrupt service for currently authorized admin users during deployment
- Authorization checks must not impact user experience (<100ms response time)
- Must work within existing Telegram Bot API constraints and conversation handler framework
- Solution must be environment-configurable without code changes
- Must preserve all existing functionality while adding security layer