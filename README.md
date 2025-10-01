# Tres Dias Telegram Bot v3

A Telegram bot for managing event participants with enterprise-grade architecture, comprehensive testing, and seamless Airtable integration.

---

## 🎯 What This Bot Does

This bot serves as a **centralized participant management system** for Tres Dias spiritual retreats, providing real-time access to participant data through an intuitive Telegram interface.

### Core Capabilities

**🔍 Participant Search & Discovery**
- Multi-language name search (Russian/English) with fuzzy matching and transliteration
- Room-based participant lookup with structured results
- Floor-based discovery with room-by-room breakdown
- Interactive floor discovery with clickable selection
- Department-based filtering for team organization

**✏️ Participant Management**
- Interactive profile editing with 13 editable fields
- Real-time field validation and change confirmation
- Save/cancel workflows with retry mechanisms
- Complete change tracking and audit trail
- Role-based editing permissions (coordinator+)

**📊 Data Export & Reports**
- Multi-table CSV export (Participants, ROE, Bible Readers)
- Role-based filtering (Team/Candidates)
- Department-specific exports
- Line-numbered exports for easy reference
- View-aligned column ordering matching Airtable
- Progress tracking for large datasets

**📋 Bulk Operations**
- Pre-filtered participant lists by role
- Department-based list filtering with 13 departments
- Paginated results handling 1500+ records
- Chief identification with crown emoji (👑)
- Church affiliation tracking

**🔐 Security & Access Control**
- Three-tier role hierarchy (Admin > Coordinator > Viewer)
- Handler-level authorization enforcement
- Role-based data filtering preventing PII exposure
- Authorization cache with sub-50ms resolution
- Privacy-compliant logging with hashed IDs

**📅 Schedule Management** (Feature Flagged)
- Four-day Tres Dias schedule display
- Interactive date selection with inline keyboards
- Section-based formatting with Russian localization
- Cached service calls (10-minute TTL)
- Refresh/back navigation

**📈 Daily Statistics**
- Automated daily statistics notifications
- Timezone-aware scheduling
- Candidate count tracking
- Department distribution reporting
- Russian localization

---

## 📱 Available Commands

### Core Commands (All Users)
| Command | Description | Access Level |
|---------|-------------|--------------|
| `/start` | Welcome message and main menu | All users |
| `/help` | Comprehensive bot guidance with all commands | All users |

### Search Commands (Viewer+)
| Command | Description | Access Level |
|---------|-------------|--------------|
| `/search [query]` | Search participants by name (Russian/English) | Viewer+ |
| `/search_room [number]` | Find participants in specific room | Viewer+ |
| `/search_floor [number]` | View all participants on a floor | Viewer+ |

### Data Export (Admin Only)
| Command | Description | Access Level |
|---------|-------------|--------------|
| `/export` | Interactive export conversation with 6 options | Admin |

### Schedule (Feature Flagged, Viewer+)
| Command | Description | Access Level |
|---------|-------------|--------------|
| `/schedule` | Display four-day Tres Dias schedule | Viewer+ |

### Administrative Commands (Admin Only)
| Command | Description | Access Level |
|---------|-------------|--------------|
| `/auth_refresh` | Clear authorization caches without restart | Admin |
| `/notifications` | View/manage daily statistics settings | Admin |
| `/set_notification_time [HH:MM] [TZ]` | Configure notification time and timezone | Admin |
| `/test_stats` | Send immediate test statistics notification | Admin |
| `/logging` | Toggle logging settings | Admin |

### Button-Based Navigation
- **🔍 Поиск участников** - Access search mode selection (Viewer+)
- **📋 Получить список** - View pre-filtered participant lists (Viewer+)
- **🏠 Главное меню** - Return to main menu (All users)

---

## 🏗️ Technical Architecture

### Clean 3-Layer Architecture

The project implements a strict separation of concerns through a 3-layer architecture pattern:

```
┌─────────────────────────────────────────────────┐
│            Bot Layer (src/bot/)                 │
│  • Telegram Handlers & Conversation Management  │
│  • Keyboard Factories & UI Components           │
│  • User State Management                        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Service Layer (src/services/)           │
│  • Business Logic & Validation                  │
│  • Data Transformation & Formatting             │
│  • Multi-Table Export Services with Filtering   │
│  • Participant Hydration & Progress Tracking    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           Data Layer (src/data/)                │
│  • Repository Pattern (Abstract Interfaces)     │
│  • Airtable Implementation                      │
│  • Rate Limiting & Error Recovery               │
└─────────────────────────────────────────────────┘
```

### Database Abstraction Strategy

The repository pattern enables seamless database backend switching without affecting business logic:

```python
# Abstract interface
class ParticipantRepository(ABC):
    @abstractmethod
    async def find_by_name(self, query: str) -> List[Participant]:
        pass

# Concrete implementation (easily replaceable)
class AirtableParticipantRepo(ParticipantRepository):
    async def find_by_name(self, query: str) -> List[Participant]:
        # Airtable-specific implementation
```

**Benefits:**
- **Database Agnostic**: Switch from Airtable to PostgreSQL/MongoDB with minimal code changes
- **Testability**: Mock repositories for comprehensive unit testing
- **Separation of Concerns**: Business logic remains independent of data storage

### Advanced Search Architecture

Multi-dimensional search with intelligent fuzzy matching:

1. **Language Detection**: Automatic Cyrillic/Latin script detection
2. **Multi-field Matching**: Searches across Russian names, English names, and nicknames
3. **Similarity Scoring**: Advanced Levenshtein distance calculations with configurable thresholds
4. **Result Ranking**: Intelligent sorting by match quality and relevance

### Conversation State Management

Sophisticated state machine implementation using python-telegram-bot's ConversationHandler:

```python
ConversationHandler(
    entry_points=[CommandHandler("search", search_start)],
    states={
        SearchStates.MODE_SELECTION: [CallbackQueryHandler(...)],
        SearchStates.AWAITING_INPUT: [MessageHandler(...)],
        SearchStates.SHOWING_RESULTS: [CallbackQueryHandler(...)],
        # ... additional states
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    conversation_timeout=1800  # 30-minute timeout
)
```

**Features:**
- **State Collision Prevention**: Non-overlapping enum values across handlers
- **Automatic Timeout Handling**: Graceful session cleanup after inactivity
- **Context Preservation**: User data maintained across state transitions
- **Mixed Handler Support**: Seamless integration of MessageHandler and CallbackQueryHandler

---

## 🔧 Technical Challenges & Solutions

This section documents the key technical challenges faced during development and the architectural solutions implemented.

### Challenge 1: Multi-Language Search with Fuzzy Matching

**Problem**: Users needed to search for participants using Russian names, English transliterations, or nicknames, often with typos or partial matches.

**Solution**: Implemented intelligent multi-field fuzzy matching system
- **Language Detection**: Automatic Cyrillic/Latin script detection using Unicode ranges
- **Multi-field Search**: Searches across Russian names, English names, nicknames, church, and location
- **Similarity Scoring**: Levenshtein distance calculations with configurable thresholds
- **Result Ranking**: Intelligent sorting by match quality (Excellent/Good/Partial)
- **Performance**: Optimized algorithm handles 1500+ records efficiently

```python
# Language detection example
if any('\u0400' <= char <= '\u04FF' for char in query):
    # Cyrillic detected - prioritize Russian name fields
else:
    # Latin detected - prioritize English name fields
```

### Challenge 2: Telegram Message Size Limits

**Problem**: Telegram enforces a 4096-character limit per message, but participant lists and search results often exceed this.

**Solution**: Dynamic pagination with offset-based navigation
- **Dynamic Page Sizing**: Automatically adjusts entries per page to stay under limit
- **Offset-based Pagination**: Prevents participant skipping when content is trimmed
- **Continuity Guarantee**: Ensures all participants accessible without gaps or duplicates
- **State Management**: Maintains position and context during navigation
- **Smart Truncation**: Multiline fields (notes) show truncated preview with ellipsis

### Challenge 3: State Collision in Concurrent Conversations

**Problem**: Multiple ConversationHandlers with overlapping state values caused conflicts and unexpected behavior.

**Solution**: Non-overlapping state enum architecture
- **Unique State Ranges**: Each handler assigned distinct enum value ranges (0-9, 10-19, 20-29, etc.)
- **State Documentation**: Clear comments documenting state ownership
- **Collision Prevention**: Build-time validation preventing duplicate values
- **Mixed Handlers**: Proper integration of MessageHandler and CallbackQueryHandler

```python
# Example state enum design
class SearchStates(IntEnum):
    MODE_SELECTION = 10
    AWAITING_INPUT = 11
    SHOWING_RESULTS = 12

class EditStates(IntEnum):
    FIELD_SELECTION = 20
    TEXT_INPUT = 21
    BUTTON_INPUT = 22
```

### Challenge 4: Rate Limiting and API Resilience

**Problem**: Airtable API rate limits (5 requests/second) caused failures during bulk operations and exports.

**Solution**: Comprehensive rate limiting and retry mechanism
- **Token Bucket Rate Limiter**: 5 requests/second with configurable limits
- **Exponential Backoff**: Automatic retry with increasing delays (1s, 2s, 4s)
- **Circuit Breaker**: Prevents cascade failures during outages
- **Progress Throttling**: 2-second minimum intervals for progress notifications
- **Error Recovery**: Graceful degradation with user-friendly messages

```python
class RateLimiter:
    def __init__(self, rate_limit: int = 5):
        self.rate_limit = rate_limit
        self.semaphore = asyncio.Semaphore(rate_limit)

    async def acquire(self):
        await self.semaphore.acquire()
        # Release after 1 second
```

### Challenge 5: Role-Based Authorization Without Database

**Problem**: Needed three-tier role hierarchy without adding database dependency.

**Solution**: Environment-based authorization with caching
- **Configuration-Based Roles**: Role IDs stored in environment variables
- **Hierarchy Implementation**: Admin inherits Coordinator, Coordinator inherits Viewer
- **Performance Caching**: 5-minute TTL cache achieves sub-50ms resolution
- **Handler-Level Enforcement**: Reusable decorators (`@require_admin`, `@require_coordinator_or_above`)
- **Privacy-Compliant Logging**: Hashed user IDs in audit logs
- **Runtime Refresh**: `/auth_refresh` command clears cache without restart

```python
@require_coordinator_or_above
async def edit_participant(update, context):
    # Only coordinators and admins can access
```

### Challenge 6: CSV Export with Airtable View Alignment

**Problem**: Exported CSV column order didn't match Airtable views, causing confusion during data review.

**Solution**: View-based export with fallback strategy
- **View-Driven Architecture**: Exports leverage configured Airtable views for column ordering
- **Fallback Logic**: Automatic fallback to repository filtering when views unavailable
- **Error Detection**: 422 VIEW_NAME_NOT_FOUND errors gracefully handled
- **Column Order Preservation**: Maintains exact Airtable view ordering
- **Line Numbers**: Sequential numbering as first column for reference
- **Progress Tracking**: Real-time updates during large exports (1500+ records)

### Challenge 7: Participant Editing with Data Integrity

**Problem**: Users needed to edit multiple fields with validation, change confirmation, and error recovery.

**Solution**: Comprehensive save/cancel workflow
- **Change Confirmation Screens**: Shows "Current Value → **New Value**" for all changes
- **Explicit Save Confirmation**: Two-step save process prevents accidental updates
- **Retry Mechanism**: Failed saves preserve changes with "Try Again" option
- **State Preservation**: User changes maintained during error recovery
- **Field Validation**: Type-specific validation (dates, amounts, age ranges)
- **Complete Display**: Shows full participant profile after updates for context

### Challenge 8: Conversation Timeout and Recovery

**Problem**: Users getting stuck in stale conversation states after inactivity.

**Solution**: Automatic timeout with recovery mechanism
- **Configurable Timeout**: Default 30 minutes via environment variable
- **Graceful Cleanup**: Automatic conversation context cleanup
- **Recovery Button**: "Return to Main Menu" button appears on timeout
- **Universal Coverage**: Applied to all conversation types (search, edit, export)
- **State Reset**: Complete cleanup prevents memory leaks

### Challenge 9: Security - Formula Injection Prevention

**Problem**: User input in Airtable queries could enable formula injection attacks.

**Solution**: Input sanitization and parameterization
- **Formula Escaping**: Special characters escaped in Airtable filter formulas
- **Parameterized Queries**: Use of Airtable API's native filtering instead of string concatenation
- **MarkdownV2 Escaping**: Protection against Telegram formatting injection
- **Validation Layers**: Input validation at bot, service, and data layers
- **Audit Logging**: All queries logged for security monitoring

### Challenge 10: Large Dataset Performance

**Problem**: Bot performance degraded with 1500+ participant records, especially during search and export.

**Solution**: Multi-layer optimization strategy
- **Server-Side Filtering**: Efficient Airtable queries with role/department filters
- **Caching**: 5-minute TTL for floor discovery and role lookups
- **Streaming CSV**: Memory-efficient export without loading full dataset
- **Async Architecture**: Non-blocking operations support concurrent users
- **Progress Indicators**: Real-time feedback during long operations (exports, searches)
- **Repository Pattern**: Allows easy migration to faster databases (PostgreSQL, MongoDB)

### Challenge 11: Daily Statistics Scheduling Across Timezones

**Problem**: Needed automated daily statistics delivery at specific times in different timezones.

**Solution**: Timezone-aware scheduling with runtime configuration
- **APScheduler Integration**: CronTrigger with timezone support
- **Runtime Reconfiguration**: Admin commands update schedule without restart
- **Configurable Delivery Time**: `/set_notification_time` with HH:MM and timezone
- **Test Command**: `/test_stats` for immediate testing
- **Error Handling**: Graceful failures with retry logic
- **Russian Localization**: Complete message formatting in Russian

### Challenge 12: Interactive UI Without Overwhelming Users

**Problem**: Needed rich interactive features (floor discovery, department filtering) without complex UIs.

**Solution**: Progressive disclosure with mobile-optimized keyboards
- **Discovery Buttons**: "Show Available Floors" reveals options only when needed
- **Inline Keyboards**: Clickable options (3 per row) for mobile optimization
- **Dual Input Methods**: Both button selection and text input supported
- **Navigation Context**: Department filter preserved through pagination
- **Clear Back Navigation**: Intuitive return paths at each step
- **Error Fallback**: Manual input guidance when interactive features fail

### Challenge 13: Multi-Table Export with Relationship Resolution

**Problem**: Needed to export ROE and Bible Readers tables with participant names instead of IDs.

**Solution**: Participant hydration with service factory pattern
- **Service Factory**: Unified interface for all export types (Participants, ROE, Bible Readers)
- **Relationship Resolution**: Linked participant IDs hydrated to names during export
- **Parallel Processing**: Efficient batched lookups for linked records
- **Progress Tracking**: Separate progress indicators for fetch vs hydration
- **Configurable Views**: Each table uses appropriate Airtable view for column ordering

---

## 🚀 CI/CD Pipeline

### Comprehensive Quality Gates

The project implements a robust CI/CD pipeline with 6 parallel quality checks:

```yaml
jobs:
  lint:        # Code quality with flake8
  typing:      # Type checking with mypy
  format:      # Code formatting with black/isort
  tests:       # Unit + Integration tests with coverage
  security:    # Vulnerability scanning with pip-audit
  docker:      # Container build and smoke testing
```

### Quality Metrics
- **Test Coverage**: 90%+ coverage with 100+ tests
- **Type Safety**: Full mypy type checking with strict mode
- **Code Quality**: Enforced through flake8, black, and isort
- **Security**: Automated vulnerability scanning on all dependencies

### Deployment Strategy

```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim AS builder
# ... build steps

FROM python:3.11-slim AS runtime
# Security: Non-root user execution
RUN useradd --create-home app
USER app
# ... runtime configuration
```

**Features:**
- **Container Security**: Non-root user execution
- **Layer Caching**: Optimized dependency installation
- **Health Checks**: Built-in smoke tests for deployment validation
- **Environment Flexibility**: Configuration through environment variables

## 🎨 Features & Capabilities

### Interactive Participant Management

#### Search Functionality
- **Name Search**: Fuzzy matching across Russian/English with transliteration
- **Room Search**: Find participants by room assignment
- **Floor Search**: Interactive floor discovery with dynamic keyboard generation
- **Bulk Lists**: Paginated team/candidate lists with role-based filtering

#### Editing Workflow
1. Search for participant
2. View detailed profile with 13 editable fields
3. Edit fields using appropriate input methods (text/buttons)
4. Review changes in confirmation screen
5. Save with retry mechanism or cancel to discard

### Admin Features

#### CSV Export
- **Full Data Export**: All participant records with complete field mapping
- **Progress Tracking**: Real-time updates during long exports
- **File Delivery**: Direct Telegram document upload with size validation
- **Error Recovery**: Automatic retry with exponential backoff

#### Role-Based Authorization System
- **Three-Tier Hierarchy**: Admin > Coordinator > Viewer with proper inheritance
- **Environment Configuration**: Role-based user IDs (TELEGRAM_ADMIN_IDS, TELEGRAM_COORDINATOR_IDS, TELEGRAM_VIEWER_IDS)
- **Data Filtering**: Role-based access to participant data with PII protection for viewers
- **Handler Enforcement**: Authorization checks at handler level prevent unauthorized access
- **Caching**: Sub-50ms role resolution performance with 5-minute TTL caching
- **Access Control Middleware**: Reusable decorators (@require_admin, @require_coordinator_or_above)
- **Type-safe**: Robust validation with comprehensive edge case handling and Python 3.9+ compatibility
- **Audit Trail**: Privacy-compliant logging with hashed user IDs

### 🧭 Управление доступами простыми словами
1. **Настроить роли через `.env`.** В переменных `TELEGRAM_ADMIN_IDS`, `TELEGRAM_COORDINATOR_IDS`, `TELEGRAM_VIEWER_IDS` перечисляем Telegram ID пользователей. Эти три списка образуют иерархию «админ → координатор → зритель».
2. **Бот узнаёт роль по ID.** При обращении пользователя бот берёт его ID, определяет роль из настроек и кладёт результат в кэш на 5 минут — так ответы быстрые и не требуют постоянных проверок.
3. **Декораторы охраняют каждый хендлер.** Перед выполнением любого обработчика отрабатывает нужный декоратор (`@require_viewer_or_above`, `@require_coordinator_or_above`, `@require_admin`). Если прав не хватает, пользователь получает понятное «❌ Доступ только для …», а логика дальше не запускается.
4. **Права по ролям.**
   - *Viewer* может искать и смотреть списки, но видит только обезличенные данные.
   - *Coordinator* наследует права зрителя и дополнительно может редактировать участников.
   - *Admin* получает полный доступ и может вручную очистить кэш командой `/auth_refresh`, чтобы новые права вступили в силу мгновенно.
5. **Без дыр по обходам.** Любые кнопки, пагинация, возврат в меню и скрытые пути вызывают те же проверки. Обойти систему через «чёрный ход» нельзя.

Итого: для выдачи доступа достаточно занести ID в нужную роль, дальше бот сам применит ограничения и защиту во всех сценариях.

### Russian Localization

Complete Russian interface throughout:
- Field labels and validation messages
- Navigation buttons and prompts
- Error messages and confirmations
- Date formatting (DD.MM.YYYY)

## 💡 Key Technical Patterns

This project demonstrates several enterprise-grade patterns. See the [Technical Challenges & Solutions](#-technical-challenges--solutions) section above for detailed problem/solution documentation.

### Repository Pattern
```python
# Abstract interface enables database switching
class ParticipantRepository(ABC):
    @abstractmethod
    async def find_by_name(self, query: str) -> List[Participant]:
        pass

# Current Airtable implementation - easily replaceable
class AirtableParticipantRepo(ParticipantRepository):
    # Implementation details...
```

### Decorator-Based Authorization
```python
@require_coordinator_or_above
async def edit_participant(update, context):
    # Handler automatically protected
    # Only coordinators and admins can access
```

### Rate-Limited API Client
```python
class AirtableClient:
    def __init__(self, rate_limit: int = 5):
        self.rate_limiter = RateLimiter(rate_limit)

    async def make_request(self, endpoint: str):
        await self.rate_limiter.acquire()
        # Automatic retry with exponential backoff
```

### State Machine Conversations
```python
ConversationHandler(
    entry_points=[CommandHandler("search", search_start)],
    states={
        SearchStates.MODE_SELECTION: [CallbackQueryHandler(...)],
        SearchStates.AWAITING_INPUT: [MessageHandler(...)],
    },
    conversation_timeout=1800  # Automatic cleanup
)
```

## 📦 Project Structure

```
telegram-bot-v3/
├── src/
│   ├── bot/                 # Telegram interface layer
│   │   ├── handlers/        # Command and conversation handlers
│   │   └── keyboards/       # UI components
│   ├── services/            # Business logic layer
│   │   ├── participant_service.py
│   │   └── participant_export_service.py
│   ├── data/                # Data access layer
│   │   ├── airtable/        # Airtable implementation
│   │   └── repositories/    # Abstract interfaces
│   ├── models/              # Pydantic data models
│   ├── config/              # Configuration management
│   └── utils/               # Shared utilities
├── tests/
│   ├── unit/                # Component-level tests
│   ├── integration/         # End-to-end tests
│   └── fixtures/            # Shared test data
├── docs/
│   ├── architecture/        # System design documentation
│   ├── business/            # Feature specifications
│   └── technical/           # API documentation
└── .github/
    └── workflows/
        └── ci-pipeline.yml  # GitHub Actions CI/CD
```

## 🚦 Development Workflow

### Quick Start

```bash
# 1. Clone and setup environment
git clone <repository>
cd telegram-bot-v3
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements/dev.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run tests
pytest tests/ -v

# 5. Start bot
./start_bot.sh  # or: python -m src.main
```

### Development Commands

```bash
# Testing
./venv/bin/pytest tests/ --cov=src --cov-report=html  # With coverage
./venv/bin/pytest tests/unit/ -v                       # Unit tests only
./venv/bin/pytest tests/integration/ -v                # Integration tests

# Code Quality
./venv/bin/mypy src --no-error-summary                 # Type checking
./venv/bin/flake8 src tests                           # Linting
./venv/bin/black src tests                            # Format code
./venv/bin/isort src tests                            # Sort imports

# Docker
docker build -t telegram-bot:latest .
docker run --env-file .env telegram-bot:latest
```

### Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
AIRTABLE_API_KEY=your_api_key
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC

# Role-Based Authorization (Role hierarchy: admin > coordinator > viewer)
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_COORDINATOR_IDS=555666777,444333222
TELEGRAM_VIEWER_IDS=111222333,999888777

# Daily Statistics Notifications (Optional - disabled by default)
DAILY_STATS_ENABLED=false  # Set to true to enable
NOTIFICATION_TIME=09:00     # 24-hour format (HH:MM)
NOTIFICATION_TIMEZONE=UTC   # e.g., Europe/Moscow, America/New_York
NOTIFICATION_ADMIN_USER_ID=123456789  # Required when enabled

# Optional
AIRTABLE_TABLE_NAME=Participants
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy
LOG_LEVEL=INFO
ENVIRONMENT=development
TELEGRAM_CONVERSATION_TIMEOUT_MINUTES=30
```

## 🧪 Testing Strategy

### Test Coverage
- **100+ Unit Tests**: Component-level validation
- **Integration Tests**: End-to-end conversation flows
- **Mock Repositories**: Isolated service layer testing
- **Fixture Management**: Shared test data and utilities

### Testing Patterns
```python
# Repository mocking for service tests
@pytest.fixture
def mock_repository():
    repo = MagicMock(spec=ParticipantRepository)
    repo.find_by_name.return_value = [test_participant]
    return repo

# Conversation state simulation
async def test_search_conversation(update, context):
    # Simulate user input and verify state transitions
```

## 📈 Scalability & Performance

### Current Capabilities
- **Dataset Size**: Tested with 1500+ participant records
- **Rate Limiting**: 5 requests/second to Airtable API
- **Message Size**: Dynamic pagination for Telegram's 4096-char limit
- **File Size**: CSV exports up to 50MB
- **Concurrent Users**: Async architecture supports multiple conversations

### Future Enhancements
- **Database Migration**: PostgreSQL/MongoDB for improved performance
- **Redis Caching**: Reduce API calls for frequently accessed data
- **Event Sourcing**: Audit trail for all participant changes
- **Webhook Mode**: Production deployment with webhook support
- **Horizontal Scaling**: Multi-instance deployment with shared state

## 🔒 Security & Compliance

### Security Measures
- **Role-Based Access Control**: Three-tier hierarchy with granular permissions and data filtering
- **Authorization Middleware**: Handler-level access control with reusable decorators
- **PII Protection**: Role-based data filtering prevents viewers from accessing sensitive information
- **Input Sanitization**: Protection against injection attacks and formula injection
- **Privacy-Compliant Logging**: Hashed user IDs in authorization logs to protect privacy
- **Secure by Default**: Unknown roles default to viewer-level access
- **Performance Security**: Sub-50ms authorization checks with caching to prevent DoS
- **Secure File Handling**: Automatic cleanup of temporary files
- **Environment Isolation**: Secrets management through environment variables
- **Container Security**: Non-root user execution in Docker

### Data Protection
- **No Data Persistence**: Bot doesn't store participant data locally
- **Secure Communication**: TLS encryption for all API calls
- **Access Control**: Role-based permissions for sensitive operations

## 🤝 Contributing

### Code Style
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google-style for all public methods
- **Testing**: Minimum 80% coverage for new features
- **Linting**: Must pass flake8, mypy, black, and isort

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all CI checks pass
4. Update documentation as needed
5. Submit PR with detailed description

## 📄 License

Proprietary - Alexandr Basis. All rights reserved.

## 🙏 Acknowledgments

Built for the Tres Dias community to streamline participant management and enhance the retreat experience through modern technology solutions.

---

**Technical Stack**: Python 3.11, python-telegram-bot, Airtable API, Docker, GitHub Actions, pytest, mypy, black, flake8
