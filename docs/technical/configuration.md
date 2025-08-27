# Configuration

## Environment Configuration (Phase 1 - IMPLEMENTED)

The project uses a comprehensive configuration management system with environment variables and structured configuration files.

## Configuration Files

### 1. Environment Variables (.env)
**Template**: `.env.example` (implemented)

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Airtable Configuration  
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_base_id_here
AIRTABLE_PARTICIPANTS_TABLE=Participants
AIRTABLE_PAYMENTS_TABLE=Payments

# Application Configuration
LOG_LEVEL=INFO
DEBUG_MODE=False

# Development Configuration
PYTEST_CACHE_DIR=.pytest_cache
```

### 2. Project Configuration (pyproject.toml)
**File**: `pyproject.toml` (implemented)

```toml
[project]
name = "tres-dias-telegram-bot"
version = "0.1.0"
description = "Telegram bot for managing Tres Dias event participants"
python = ">=3.9"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*", "*Tests"] 
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose"
]

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | build
  | dist
)/
'''

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Configuration Management Structure

### Configuration Package (Implemented)
**Location**: `src/config/`

```
src/config/
├── __init__.py                # Package initialization
├── settings.py                # Main application settings (to be implemented)
└── field_mappings.py          # Data validation rules (to be implemented)
```

### Environment Loading Pattern
```python
# Future implementation pattern
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class BotConfig:
    telegram_token: str
    chat_id: str
    airtable_api_key: str
    airtable_base_id: str
    log_level: str = "INFO"
    debug_mode: bool = False
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        return cls(
            telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            airtable_api_key=os.getenv("AIRTABLE_API_KEY", ""),
            airtable_base_id=os.getenv("AIRTABLE_BASE_ID", ""),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            debug_mode=os.getenv("DEBUG_MODE", "False").lower() == "true"
        )
```

## Security Practices (Implemented)

### Environment Variable Security
**File**: `.gitignore` (comprehensive implementation)

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Sensitive configuration
config.ini
secrets.json
*.key
*.pem
```

### Security Guidelines
1. **Never commit** `.env` files to version control
2. **Use `.env.example`** to document required variables
3. **Validate environment** variables at startup
4. **Use strong defaults** where possible
5. **Log configuration errors** but not sensitive values

## Dependencies Configuration

### Requirements Files (Implemented)
**Structure**: `requirements/` directory

#### Base Dependencies (`requirements/base.txt`)
```text
# Core runtime dependencies
python-telegram-bot>=20.0
pyairtable>=2.0.0  
python-dotenv>=1.0.0
pydantic>=2.0.0
aiofiles>=23.0.0
```

#### Development Dependencies (`requirements/dev.txt`)  
```text
# Development and code quality tools
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
isort>=5.12.0
pre-commit>=3.0.0
```

#### Testing Dependencies (`requirements/test.txt`)
```text
# Testing framework and tools
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
responses>=0.23.0
pytest-mock>=3.10.0
```

## Development Environment Setup

### Quick Setup Process (Validated)
```bash
# 1. Environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements/dev.txt
pip install -r requirements/base.txt  
pip install -r requirements/test.txt

# 3. Configuration setup
cp .env.example .env
# Edit .env with actual values

# 4. Verify setup
python -c "import src.config"  # Validates package structure
pytest tests/test_project_structure.py -v  # Validates configuration
```

### Configuration Validation
The project includes structural validation for configuration:

```bash
# Test configuration files exist
pytest tests/test_project_structure.py::test_project_config_files_exist -v

# Test requirements files exist  
pytest tests/test_project_structure.py::test_requirements_files_exist -v
```

## Configuration Best Practices

### 1. Environment Variable Naming
```bash
# Use consistent prefixes
TELEGRAM_BOT_TOKEN     # Bot-specific
AIRTABLE_API_KEY      # Service-specific  
LOG_LEVEL             # Application-wide

# Use clear, descriptive names
AIRTABLE_PARTICIPANTS_TABLE  # Not just "TABLE_NAME"
```

### 2. Configuration Validation
```python
# Future implementation pattern
def validate_config(config: BotConfig) -> List[str]:
    errors = []
    if not config.telegram_token:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    if not config.airtable_api_key:
        errors.append("AIRTABLE_API_KEY is required")
    return errors
```

### 3. Environment-Specific Configuration
```bash
# Different environments
.env.development     # Local development
.env.testing        # Test environment
.env.production     # Production (never committed)
```

## Implementation Status

### Phase 1: Foundation (COMPLETED)
- Environment variables template (`.env.example`)
- Project configuration (`pyproject.toml`) with tool settings
- Requirements files structure (`requirements/` directory)
- Configuration package structure (`src/config/`)  
- Security practices implemented (`.gitignore`)
- Configuration validation tests

### Phase 2: Configuration Implementation
- Settings class implementation
- Environment variable validation
- Field mapping configuration
- Logging configuration

### Phase 3: Advanced Configuration
- Environment-specific configuration
- Configuration hot-reloading
- Configuration management for deployment

## Troubleshooting

### Common Configuration Issues
1. **Missing .env file**: Copy from `.env.example`
2. **Invalid environment variables**: Check variable names and values
3. **Package import errors**: Ensure `__init__.py` files exist
4. **Dependencies issues**: Verify all requirements files installed

### Validation Commands
```bash
# Check configuration structure
pytest tests/test_project_structure.py -v

# Validate Python imports
python -c "import src.config, src.models, src.services"

# Check requirements installation
pip list | grep -E "(telegram|airtable|pytest)"
```