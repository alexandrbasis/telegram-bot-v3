# Tres Dias Telegram Bot v3

A Telegram bot for managing event participants with enterprise-grade architecture, comprehensive testing, and seamless Airtable integration.

## 🎯 Project Overview

This bot serves as a centralized participant management system for Tres Dias spiritual retreats, providing real-time access to participant data through an intuitive Telegram interface. Built with scalability, maintainability, and user experience as core principles.

### Key Capabilities
- **Multi-language Search**: Advanced fuzzy matching across Russian/English names with transliteration support
- **Interactive Editing**: In-place participant profile editing with validation and change confirmation workflows
- **Enhanced Export Services**: Multi-table CSV export with filtering and participant hydration
  - **Participant Filtering**: Role-based (TEAM/CANDIDATE) and department-based export filtering
  - **BibleReaders Export**: Bible reading assignments with participant name resolution
  - **ROE Export**: Session data with presenter/assistant/prayer partner details
- **Location-based Search**: Room and floor-based participant discovery with interactive UI
- **Role-based Access Control**: Three-tier authorization hierarchy (admin/coordinator/viewer) with granular data filtering and handler-level enforcement
- **Enhanced Security**: Role-based data filtering prevents unauthorized access to sensitive participant information

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

## 🔧 Technical Solutions

### Rate Limiting & Resilience

```python
class AirtableClient:
    def __init__(self, rate_limit: int = 5):
        self.rate_limiter = RateLimiter(rate_limit)

    async def make_request(self, endpoint: str):
        await self.rate_limiter.acquire()
        # ... request logic with retry
```

### Security Measures

1. **Formula Injection Prevention**: Input sanitization for Airtable queries
2. **MarkdownV2 Escaping**: Protection against formatting injection attacks
3. **Environment-based Secrets**: No hardcoded credentials
4. **Non-root Container Execution**: Enhanced Docker security

### Performance Optimizations

- **Caching**: 5-minute TTL for floor discovery queries
- **Pagination**: Dynamic page sizing for large result sets
- **Streaming CSV**: Memory-efficient export for 1500+ records
- **Progress Throttling**: 2-second intervals to prevent rate limits

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
