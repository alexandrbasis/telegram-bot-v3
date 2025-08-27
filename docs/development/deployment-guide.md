# Deployment Guide

## Project Setup for Deployment (Phase 1 - FOUNDATION READY)

The project foundation has been established with all necessary configuration and structure for future deployment.

## Prerequisites (Implemented)

### 1. Project Structure Validation
```bash
# Ensure all foundation components are present
pytest tests/test_project_structure.py -v

# Expected: All 7 structural validation tests pass
# - src/ directory structure ✅
# - tests/ directory structure ✅  
# - Python packages with __init__.py ✅
# - Python imports working ✅
# - Requirements files present ✅
# - Project config files present ✅
# - Supporting directories present ✅
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with production values
nano .env  # or your preferred editor
```

**Required Environment Variables**:
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_CHAT_ID=your_production_chat_id

# Airtable Configuration
AIRTABLE_API_KEY=your_production_airtable_key
AIRTABLE_BASE_ID=your_production_base_id
AIRTABLE_PARTICIPANTS_TABLE=Participants
AIRTABLE_PAYMENTS_TABLE=Payments

# Application Configuration
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### 3. Dependencies Installation
```bash
# Production environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install production dependencies
pip install -r requirements/base.txt

# For development/testing environments, also install:
pip install -r requirements/dev.txt
pip install -r requirements/test.txt
```

## Deployment Structure

### Current Project Layout (Phase 1 Complete)
```
telegram-bot-v3/
├── src/                           # Application source code
│   ├── bot/                       # Telegram bot layer
│   ├── services/                  # Business logic layer
│   ├── data/                      # Data access layer
│   ├── models/                    # Data models
│   ├── config/                    # Configuration management
│   └── utils/                     # Shared utilities
├── tests/                         # Test suite
├── requirements/                  # Dependency management
│   ├── base.txt                  # Production dependencies
│   ├── dev.txt                   # Development dependencies
│   └── test.txt                  # Testing dependencies
├── scripts/                       # Utility scripts
├── data/                          # Data storage
├── .env.example                   # Environment template
├── pyproject.toml                # Project configuration
└── README.md                     # Setup instructions
```

## Deployment Environments

### Development Environment (Current State)
**Status**: Fully configured and validated

**Setup Commands**:
```bash
# Clone and setup
git clone <repository>
cd telegram-bot-v3
python -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements/dev.txt
pip install -r requirements/base.txt
pip install -r requirements/test.txt

# Configure environment
cp .env.example .env
# Edit .env with development values

# Verify setup
python -c "import src.bot, src.services, src.data, src.models, src.config, src.utils"
pytest tests/test_project_structure.py -v
```

### Production Environment (Foundation Ready)
**Status**: Structure prepared, awaiting implementation

**Deployment Process** (Future Implementation):
```bash
# Production server setup
python -m venv production_venv
source production_venv/bin/activate

# Install production dependencies only
pip install -r requirements/base.txt

# Production environment configuration
cp .env.example .env.production
# Configure with production values

# Run bot
python src/main.py  # (to be implemented)
```

## Security Considerations (Implemented)

### Environment Variable Security
**File**: `.gitignore` - Comprehensive security exclusions
```gitignore
# Environment files
.env
.env.local
.env.*.local

# Sensitive configuration
config.ini
secrets.json
*.key
*.pem

# Development artifacts
.pytest_cache/
__pycache__/
*.pyc
.mypy_cache/
.coverage
```

### Security Best Practices
1. **Environment Variables**: All secrets in `.env` files (never committed)
2. **API Keys**: Secure storage of Telegram and Airtable credentials
3. **Dependencies**: Pinned versions in requirements files
4. **Configuration**: Structured configuration with validation

## Validation Commands

### Pre-deployment Validation
```bash
# 1. Structure validation
pytest tests/test_project_structure.py -v
# Must pass: All 7 structural tests

# 2. Import validation  
python -c "import src.config, src.models, src.services, src.data, src.bot, src.utils"
# Must succeed: All packages importable

# 3. Configuration validation
test -f .env && echo "Environment file exists" || echo "Missing .env file"
test -f pyproject.toml && echo "Project config exists" || echo "Missing project config"

# 4. Dependencies validation
pip list | grep -E "(telegram|airtable|pytest)" | wc -l
# Should show installed core dependencies
```

### Health Checks (Future Implementation)
```bash
# Bot connectivity test
python scripts/test_bot_connection.py  # (to be implemented)

# Airtable connectivity test  
python scripts/test_airtable_connection.py  # (to be implemented)

# Full system test
pytest tests/integration/ -v  # (to be implemented)
```

## Monitoring and Logging (Foundation Ready)

### Logging Configuration
**Location**: `src/utils/logger.py` (to be implemented)
**Configuration**: Environment variable `LOG_LEVEL`

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Important events that may need attention  
- **ERROR**: Serious problems that need immediate attention

### Log Storage
**Development**: Console output
**Production**: File-based logging (to be configured)

## Backup and Recovery (Structure Ready)

### Data Backup Structure (Implemented)
```
data/
├── backups/        # Automated Airtable backups
├── exports/        # Manual export files  
└── cache/          # Performance cache
```

### Backup Scripts (Foundation Ready)
**Location**: `scripts/` directory
- `backup_data.py` - Automated backup script (to be implemented)
- `migrate_data.py` - Data migration helpers (to be implemented)

## Implementation Status

### Phase 1: Foundation (COMPLETED)
- Complete project structure established
- Configuration management implemented  
- Dependencies and requirements organized
- Security practices implemented
- Testing framework configured
- All validation tests passing

### Phase 2: Core Implementation (Pending)
- Main application entry point (`src/main.py`)
- Bot initialization and handlers
- Service layer implementation
- Database connectivity

### Phase 3: Deployment Ready (Pending)  
- Production environment configuration
- Monitoring and logging implementation
- Backup automation
- Health check endpoints

### Phase 4: Production Operations (Pending)
- CI/CD pipeline setup
- Automated deployment
- Performance monitoring
- Error tracking and alerting

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all `__init__.py` files exist and virtual environment is active
2. **Missing Dependencies**: Run `pip install -r requirements/base.txt`
3. **Configuration Issues**: Verify `.env` file exists and contains required variables
4. **Structure Problems**: Run `pytest tests/test_project_structure.py -v` to diagnose

### Diagnostic Commands
```bash
# Check Python environment
which python
python --version

# Check package structure
find src/ -name "__init__.py" | wc -l  # Should show 10 files

# Check requirements
pip freeze | grep -E "(telegram|airtable|pytest)"

# Full structure validation
pytest tests/test_project_structure.py::test_src_directory_structure -v
```