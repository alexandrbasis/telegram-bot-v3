# Security Architecture & Guidelines

## Overview

The Tres Dias Telegram Bot implements a comprehensive security framework designed to protect participant data and ensure proper access control. This document outlines the security architecture, threat model, and implementation details.

## Role-Based Access Control (RBAC)

### Security Model

The bot implements a three-tier role-based access control system designed to enforce the principle of least privilege:

**Role Hierarchy**: Admin > Coordinator > Viewer

#### Role Definitions

**Admin Role**:
- **Access Level**: Full system access
- **Data Access**: All participant fields including PII, financial, and sensitive information
- **Permissions**: Export functionality, user management, system administration
- **Use Case**: System administrators, senior leadership

**Coordinator Role**:
- **Access Level**: Operational access with restrictions
- **Data Access**: Most participant fields excluding financial/payment information
- **Permissions**: Participant search, editing, list access (no exports)
- **Use Case**: Event coordinators, team leaders, operational staff

**Viewer Role**:
- **Access Level**: Limited read-only access
- **Data Access**: Basic participant information only (name, role, department)
- **Permissions**: Participant search and viewing (no editing, no sensitive data)
- **Use Case**: Volunteers, assistants, limited access users

### Data Classification & Protection

#### Sensitive Data Fields (Admin Only)
- **PII**: Phone numbers, email addresses, physical addresses
- **Financial**: Payment amounts, payment status, financial records
- **Medical**: Medical conditions, dietary restrictions
- **Contact**: Emergency contact information

#### Restricted Data Fields (Coordinator+ Only)
- **Operational**: Room assignments, scheduling information
- **Administrative**: Department assignments, leadership roles
- **Logistics**: Transportation, accommodation details

#### Public Data Fields (All Roles)
- **Basic Identity**: Name (Russian/English), nickname
- **General Info**: Role (TEAM/CANDIDATE), department (general)
- **Non-sensitive**: Basic profile information

## Security Architecture Components

### Configuration Security

#### Environment-Based Role Management
```bash
# Role hierarchy configuration
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_COORDINATOR_IDS=555666777,444333222
TELEGRAM_VIEWER_IDS=111222333,999888777
```

**Security Features**:
- **Type Safety**: Robust validation of user ID formats
- **Input Sanitization**: Protection against injection attacks
- **Configuration Validation**: Startup validation with clear error messages
- **Secure Defaults**: Unknown configurations default to no access

### Authentication & Authorization

#### Multi-Layer Authentication
1. **Telegram User Validation**: Bot verifies user identity via Telegram's authentication
2. **Role Resolution**: System determines user's highest role from configuration
3. **Permission Checking**: Each operation validates required permissions
4. **Data Filtering**: Results filtered based on user role before display

#### Authorization Utilities (`src/utils/auth_utils.py`)

**Core Functions**:
- `get_user_role(user_id, settings)`: Resolves highest user role with caching
- `is_admin_user(user_id, settings)`: Validates admin access (backward compatible)
- `is_coordinator_user(user_id, settings)`: Validates coordinator or higher access
- `is_viewer_user(user_id, settings)`: Validates any authorized user access

**Security Features**:
- **Role Hierarchy Enforcement**: Higher roles inherit lower role permissions
- **Performance Caching**: 5-minute TTL cache for <50ms response times
- **Privacy Protection**: User IDs hashed in logs to protect privacy
- **Secure by Default**: Unknown roles default to no access

### Access Control Middleware

#### Decorator-Based Authorization (`src/utils/access_control.py`)

**Available Decorators**:
- `@require_admin()`: Admin-only access
- `@require_coordinator_or_above()`: Coordinator/admin access
- `@require_viewer_or_above()`: Any authorized user access
- `@require_role(roles)`: Flexible multi-role authorization

**Example Implementation**:
```python
from src.utils.access_control import require_admin, require_coordinator_or_above

@require_admin()
async def export_handler(update, context):
    """Admin-only export functionality with audit logging"""
    user_id = update.effective_user.id
    logger.info(f"Export initiated by admin user: {hash(str(user_id))}")
    # Export logic...

@require_coordinator_or_above()
async def participant_edit_handler(update, context):
    """Coordinator/admin participant editing with validation"""
    # Edit logic with role-appropriate data access...
```

### Data Security

#### Role-Based Data Filtering (`src/utils/participant_filter.py`)

**Filtering Strategy**:
```python
def filter_participants_by_role(participants, user_role):
    """Apply role-based field filtering to participant data"""
    if user_role == "admin":
        return participants  # Full access
    elif user_role == "coordinator":
        return filter_coordinator_fields(participants)  # Remove financial data
    elif user_role == "viewer":
        return filter_viewer_fields(participants)  # Basic info only
    else:
        return []  # No access for unauthorized users
```

**Security Compliance**:
- **Field-Level Security**: Granular control over data exposure
- **PII Protection**: Automatic removal of personally identifiable information
- **Financial Data Protection**: Payment information restricted to admins only
- **Consistent Filtering**: Applied at multiple layers (handler, service, repository)

### Handler-Level Security

#### Search Handler Security (`src/bot/handlers/search_handlers.py`)

**Security Implementation**:
1. **Role Resolution**: User role determined at conversation start
2. **Parameter Passing**: User role passed to all repository operations
3. **Fallback Security**: All code paths include role-based filtering
4. **Bypass Prevention**: Multiple validation layers prevent security bypass

**Critical Security Fix Applied**:
- **Problem**: Handlers were not passing user roles to repository methods
- **Impact**: Could allow unauthorized data access through fallback search paths
- **Solution**: Added mandatory role resolution and parameter passing
- **Validation**: Comprehensive integration tests verify role enforcement

### Repository-Level Security

#### Secure Data Access (`src/data/repositories/`)

**Interface Updates**:
- All search methods accept `user_role` parameter
- Repository implementations apply role-based filtering
- Abstract interfaces enforce security compliance
- Integration tests validate security at repository level

**Example Secure Repository Method**:
```python
async def find_by_name(self, query: str, user_role: str = None) -> List[Participant]:
    """Search participants with role-based filtering"""
    # Execute search query
    participants = await self._execute_search(query)

    # Apply role-based filtering before returning
    return filter_participants_by_role(participants, user_role)
```

## Security Best Practices

### Privacy Protection

#### Logging Security
- **User ID Hashing**: All user IDs hashed in logs using secure hash functions
- **Minimal Logging**: Only essential information logged for security events
- **Log Level Controls**: Sensitive information logged at DEBUG level only
- **No PII in Logs**: Personal information never written to log files

#### Data Handling
- **In-Memory Processing**: No sensitive data persisted locally
- **Secure Communication**: All API calls use TLS encryption
- **Automatic Cleanup**: Temporary files automatically deleted after use
- **Session Management**: Conversation timeouts prevent stale sessions

### Input Validation & Sanitization

#### Protection Against Attacks
- **SQL/Formula Injection**: Input sanitization for Airtable queries
- **MarkdownV2 Escaping**: Protection against formatting injection
- **Type Validation**: Strict type checking for user inputs
- **Length Limits**: Message size limits prevent DoS attacks

#### Configuration Security
- **Environment Variables**: All secrets managed via environment variables
- **No Hardcoded Credentials**: Zero hardcoded API keys or tokens
- **Validation at Startup**: Configuration validated before bot start
- **Error Messages**: Secure error handling with no information leakage

### Performance Security

#### DoS Protection
- **Rate Limiting**: 5 requests/second to Airtable API
- **Response Time Limits**: Authorization checks under 50ms
- **Memory Management**: Efficient caching with TTL expiration
- **Resource Cleanup**: Automatic cleanup of conversation resources

#### Caching Security
- **Cache TTL**: 5-minute expiration for role resolution cache
- **Memory Limits**: Bounded cache prevents memory exhaustion
- **Cache Invalidation**: Manual invalidation for security updates
- **No Sensitive Caching**: User data not cached, only role resolutions

## Threat Model & Mitigation

### Identified Threats

#### T1: Unauthorized Data Access
- **Threat**: Users accessing data above their permission level
- **Mitigation**: Multi-layer role checking, data filtering, handler enforcement
- **Validation**: Integration tests verify role boundaries

#### T2: Privilege Escalation
- **Threat**: Users gaining higher-level access through system vulnerabilities
- **Mitigation**: Role hierarchy enforcement, secure defaults, comprehensive validation
- **Monitoring**: Audit logging of all authorization events

#### T3: Data Leakage
- **Threat**: Sensitive information exposed through logs or error messages
- **Mitigation**: PII filtering, hashed logging, secure error handling
- **Prevention**: Regular security audits and automated scanning

#### T4: Configuration Bypass
- **Threat**: Bypassing role configuration through alternative access paths
- **Mitigation**: Multiple validation layers, handler enforcement, repository security
- **Testing**: Comprehensive security regression tests

### Security Controls Summary

| Control Type | Implementation | Validation |
|-------------|----------------|------------|
| Authentication | Telegram user ID validation | Startup configuration check |
| Authorization | Role-based access control | Role hierarchy tests |
| Data Protection | Field-level filtering | Data exposure tests |
| Input Validation | Type checking, sanitization | Injection attack tests |
| Logging Security | Hashed user IDs, minimal data | Log content audits |
| Performance Security | Rate limiting, caching TTL | Performance benchmarks |
| Configuration Security | Environment variables, validation | Configuration tests |

## Security Testing

### Test Coverage

**Unit Tests** (22+ security-focused tests):
- Role resolution and caching functionality
- Authorization utilities comprehensive testing
- Data filtering validation across all roles
- Access control decorator functionality

**Integration Tests** (15+ end-to-end security tests):
- Handler-level role enforcement validation
- Repository security parameter passing
- Data filtering across complete request flows
- Authorization bypass prevention

**Security Regression Tests**:
- Authorization bypass vulnerability prevention
- PII leakage prevention in all code paths
- Role hierarchy enforcement across updates
- Fallback security path validation

### Continuous Security Validation

**CI/CD Security Checks**:
- Dependency vulnerability scanning with pip-audit
- Static code analysis for security patterns
- Automated security test execution
- Configuration validation in test environments

## Security Incident Response

### Monitoring & Alerting

**Security Events Logged**:
- Authorization failures with hashed user IDs
- Role resolution errors and fallbacks
- Configuration validation failures
- Unusual access patterns or errors

**Response Procedures**:
1. **Immediate**: Review logs for unauthorized access attempts
2. **Assessment**: Determine scope of potential security breach
3. **Mitigation**: Update role configurations if compromised
4. **Recovery**: Clear caches and restart bot if necessary
5. **Post-Incident**: Review and update security measures

### Security Updates

**Regular Maintenance**:
- Dependency updates with security patch reviews
- Role configuration audits and cleanup
- Security test expansion based on new threats
- Documentation updates reflecting security changes

## Future Security Enhancements

### Planned Improvements

#### Airtable Sync Integration
- **Dynamic Role Management**: Real-time role updates from Airtable
- **Audit Trail**: Complete role change history
- **Automated Provisioning**: User onboarding/offboarding workflows

#### Enhanced Monitoring
- **Security Dashboards**: Real-time security event monitoring
- **Anomaly Detection**: Unusual access pattern identification
- **Automated Response**: Automated role restriction for security events

#### Advanced Access Control
- **Time-Based Access**: Role restrictions based on time periods
- **IP-Based Restrictions**: Location-based access controls
- **Multi-Factor Authentication**: Additional authentication layers

This security framework ensures the Tres Dias Telegram Bot maintains the highest standards of data protection while providing appropriate access to authorized users based on their operational needs.