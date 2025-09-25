# Development Workflow

## Environment Setup

### Prerequisites
- Python 3.9+ (tested with Python 3.11)
- Git
- Telegram bot token from @BotFather
- Airtable API key and base access

### Initial Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd telegram-bot-v3
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Development dependencies (includes testing and linting tools)
   pip install -r requirements/dev.txt

   # Production dependencies only
   pip install -r requirements/base.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (see Configuration section below)
   ```

### Environment Configuration

Create a `.env` file with the following configuration:

```bash
# Required - Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Required - Airtable Integration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC

# Role-Based Authorization (Role hierarchy: admin > coordinator > viewer)
TELEGRAM_ADMIN_IDS=your_telegram_user_id,other_admin_id
TELEGRAM_COORDINATOR_IDS=coordinator_user_id_1,coordinator_user_id_2
TELEGRAM_VIEWER_IDS=viewer_user_id_1,viewer_user_id_2

# Optional Configuration
AIRTABLE_TABLE_NAME=Participants
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy
LOG_LEVEL=DEBUG
ENVIRONMENT=development
TELEGRAM_CONVERSATION_TIMEOUT_MINUTES=30
```

**Role Configuration Notes**:
- Users can have multiple roles - system assigns the highest role
- Admin role inherits all coordinator and viewer permissions
- Coordinator role inherits all viewer permissions
- Viewer role provides basic read-only access to non-sensitive data
- Unauthorized users (not in any role list) have no access

### Development Commands

#### Testing

```bash
# Run all tests with coverage
./venv/bin/pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test categories
./venv/bin/pytest tests/unit/ -v                    # Unit tests only
./venv/bin/pytest tests/integration/ -v             # Integration tests only

# Run handler security tests (Added 2025-09-25)
./venv/bin/pytest tests/unit/test_bot_handlers/ -k "authorization" -v
./venv/bin/pytest tests/unit/test_bot_handlers/test_search_handlers.py -k "TestStartCommandAuthorization" -v
./venv/bin/pytest tests/unit/test_bot_handlers/test_admin_handlers.py -k "TestAuthRefreshCommand" -v

# Run specific test files
./venv/bin/pytest tests/unit/test_utils/test_auth_utils.py -v
./venv/bin/pytest tests/integration/test_handler_role_enforcement.py -v

# Run tests with specific markers
./venv/bin/pytest -m "auth" -v                      # Authorization-related tests
./venv/bin/pytest -m "security" -v                  # Security tests
```

#### Code Quality

```bash
# Type checking
./venv/bin/mypy src --no-error-summary

# Linting
./venv/bin/flake8 src tests

# Code formatting
./venv/bin/black src tests
./venv/bin/isort src tests

# Run all quality checks
make lint  # If Makefile is configured
```

#### Running the Bot

```bash
# Using startup script (recommended)
./start_bot.sh

# Direct Python execution
python -m src.main

# With specific log level
LOG_LEVEL=DEBUG python -m src.main
```

## Development Guidelines

### Security Considerations

When developing features that involve user data or access control:

1. **Always Implement Role-Based Access Control**
   ```python
   from src.utils.auth_utils import get_user_role
   from src.utils.participant_filter import filter_participants_by_role

   async def your_handler(update, context):
       user_id = update.effective_user.id
       user_role = get_user_role(user_id, get_settings())

       # Apply role-based filtering to all data
       participants = await repo.get_data()
       filtered_data = filter_participants_by_role(participants, user_role)
   ```

2. **Use Access Control Decorators**
   ```python
   from src.utils.access_control import require_admin, require_coordinator_or_above

   @require_admin()
   async def admin_only_handler(update, context):
       # Admin-only functionality
       pass

   @require_coordinator_or_above()
   async def coordinator_handler(update, context):
       # Coordinator/admin functionality
       pass
   ```

3. **Validate User Permissions in Repository Calls**
   ```python
   # Always pass user_role to repository methods
   results = await participant_repo.find_by_name(query, user_role=user_role)
   ```

4. **Test Security Boundaries**
   - Write tests for each role level
   - Verify unauthorized access is properly blocked
   - Test data filtering for each role
   - Include integration tests for complete authorization flows

### Code Standards

#### Authorization Testing Patterns

```python
import pytest
from unittest.mock import MagicMock
from src.utils.auth_utils import get_user_role, invalidate_role_cache

class TestYourFeature:
    def setup_method(self):
        """Clear role cache before each test"""
        invalidate_role_cache()

    @pytest.mark.parametrize("user_role,expected_fields", [
        ("admin", ["all", "fields", "including", "sensitive"]),
        ("coordinator", ["most", "fields", "except", "financial"]),
        ("viewer", ["basic", "fields", "only"]),
        (None, [])  # Unauthorized user
    ])
    async def test_role_based_access(self, user_role, expected_fields):
        # Test implementation...
```

#### Security Code Review Checklist (Updated 2025-09-25)

- [x] **Handler Security Implementation Complete**: All handlers protected with appropriate decorators
- [x] All handlers resolve user roles before processing
- [x] Repository methods receive and use user_role parameter
- [x] Data filtering applied at multiple layers (handler, service, repository)
- [x] Access control decorators used for all endpoints (@require_viewer_or_above, @require_coordinator_or_above, @require_admin)
- [x] No PII or sensitive data in log messages
- [x] **Comprehensive Security Test Coverage**: 35+ authorization tests across all handler modules
- [x] Role-based tests cover all permission boundaries
- [x] Integration tests verify complete authorization flows with updated mocks
- [x] Error handling doesn't leak sensitive information
- [x] **Admin Cache Management**: /auth_refresh command enables real-time role updates
- [x] **Zero Authorization Bypass**: No unauthorized access paths remain in codebase

### Git Workflow

#### Branch Naming
- `feature/TDB-###-description` - New features
- `fix/TDB-###-description` - Bug fixes
- `security/TDB-###-description` - Security fixes
- `docs/TDB-###-description` - Documentation updates

#### Commit Guidelines
- Use conventional commit format: `type(scope): description`
- Include Linear issue ID in commit messages
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

Example:
```bash
git commit -m "feat(auth): implement role-based access control

- Add three-tier role hierarchy (admin/coordinator/viewer)
- Implement data filtering by role
- Add access control decorators
- Include comprehensive security tests

Fixes: TDB-71"
```

#### Pull Request Process

1. **Pre-PR Checklist**
   - [ ] All tests pass locally
   - [ ] Code quality checks pass (mypy, flake8, black, isort)
   - [ ] Security tests included for access control features
   - [ ] Documentation updated for new features
   - [ ] Environment variables documented in .env.example

2. **PR Requirements**
   - Descriptive title with Linear issue ID
   - Detailed description of changes
   - Screenshots for UI changes
   - Security considerations documented
   - Test coverage maintained or improved

3. **Review Process**
   - Automated CI/CD checks must pass
   - Security review for authorization changes
   - Code review by team member
   - Documentation review for user-facing changes

#### CI/CD Pipeline

The project includes comprehensive automated checks:

```yaml
# .github/workflows/ci.yml
jobs:
  lint:        # Code quality with flake8
  typing:      # Type checking with mypy
  format:      # Code formatting with black/isort
  tests:       # Unit + Integration tests with coverage
  security:    # Vulnerability scanning with pip-audit
```

**Quality Gates**:
- Test coverage must be ≥80%
- All linting and type checking must pass
- Security audit must pass with no high/critical vulnerabilities
- All authorization tests must pass

### Debugging & Troubleshooting

#### Common Development Issues

**Authorization Problems**:
```bash
# Check role resolution
LOG_LEVEL=DEBUG python -c "
from src.config.settings import get_settings
from src.utils.auth_utils import get_user_role
settings = get_settings()
print(f'User role: {get_user_role(YOUR_USER_ID, settings)}')
"

# Verify environment configuration
python -c "
from src.config.settings import get_settings
settings = get_settings()
print(f'Admin IDs: {settings.telegram.admin_user_ids}')
print(f'Coordinator IDs: {settings.telegram.coordinator_user_ids}')
print(f'Viewer IDs: {settings.telegram.viewer_user_ids}')
"
```

**Test Failures**:
- Clear role cache: Call `invalidate_role_cache()` in test setup
- Check mock configurations match expected role hierarchy
- Verify test data includes proper role assignments

**Configuration Issues**:
- Validate .env file exists and is properly formatted
- Check user ID format (must be integers, not strings)
- Ensure role hierarchy is properly configured (no overlapping roles)

#### Performance Monitoring

**Authorization Performance**:
```python
import time
from src.utils.auth_utils import get_user_role

# Measure role resolution performance
start_time = time.time()
role = get_user_role(user_id, settings)
duration = time.time() - start_time

# Should be < 50ms for cached results
assert duration < 0.05, f"Role resolution too slow: {duration}s"
```

This development workflow ensures consistent, secure, and maintainable code development while enforcing proper authorization practices throughout the development lifecycle.