# Development Workflow

## Project Setup (Phase 1 - COMPLETED)

### Quick Start
```bash
# 1. Clone and setup environment
git clone [repository]
cd telegram-bot-v3
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 2. Install dependencies  
pip install -r requirements/dev.txt  # Includes testing and linting tools
pip install -r requirements/base.txt # Core runtime dependencies

# 3. Configuration
cp .env.example .env
# Edit .env with your bot token and API keys

# 4. Verify setup
python -c "import src.bot, src.services, src.data, src.models, src.config, src.utils"
pytest tests/test_project_structure.py -v  # Run structure validation tests
```

## Development Environment

### Requirements Management
The project uses a structured requirements approach:

- **`requirements/base.txt`**: Core runtime dependencies (production)
- **`requirements/dev.txt`**: Development tools (black, flake8, mypy, etc.)
- **`requirements/test.txt`**: Testing-specific dependencies (pytest, responses, etc.)

### Project Configuration
Modern Python project configuration is managed through:

- **`pyproject.toml`**: Main project configuration with tool settings
- **`.env.example`**: Environment variables template
- **`.gitignore`**: Comprehensive exclusion patterns for Python projects

## Development Workflow Steps

### 1. Start Development
```bash
# Activate virtual environment
source venv/bin/activate

# Ensure all dependencies are current
pip install -r requirements/dev.txt
```

### 2. Code Quality Standards
```bash
# Format code (automated)
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/  # Type checking

# Combined quality check
make quality-check  # (when Makefile is implemented)
```

### 3. Testing Approach
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/test_project_structure.py -v # Structure validation
```

### 4. Git Workflow
```bash
# Create feature branch
git checkout -b feature/add-participant-command

# Make small, focused commits
git add src/services/participant_service.py
git commit -m "Add participant service with validation"

# Run full quality check before push
pytest tests/ -v
git push origin feature/add-participant-command
```

## Code Organization Guidelines

### File Structure Rules
- **One class per file** (except small related classes)
- **Group related functions** in the same module
- **Import organization**: Standard library → Third party → Local imports
- **No circular imports**: Use dependency injection patterns

### Naming Conventions
```python
# Good examples following implemented structure
from src.services.participant_service import ParticipantService
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.participant import Participant
from src.config.settings import BotSettings
```

## Testing Strategy (Implemented Framework)

### Test Organization
The testing framework is fully configured with:

```
tests/
├── unit/                   # Layer-specific unit tests
│   ├── test_services/      # Business logic tests
│   ├── test_data/          # Data layer tests  
│   └── test_models/        # Model validation tests
├── integration/            # End-to-end workflow tests
│   └── test_bot_handlers/  # Complete bot interaction tests
├── fixtures/               # Shared test data and mocks
└── test_project_structure.py  # Structural validation (7 tests)
```

### Test Execution
```bash
# Structure validation (foundation verification)
pytest tests/test_project_structure.py -v

# Example output from Phase 1:
# test_src_directory_structure ✅
# test_tests_directory_structure ✅  
# test_python_packages_have_init_files ✅
# test_python_imports_work ✅
# test_requirements_files_exist ✅
# test_project_config_files_exist ✅
# test_supporting_directories_exist ✅
```

## Implementation Status

### Phase 1: Foundation (COMPLETED)
- Project structure established and validated
- Development environment configured  
- Testing framework operational
- Quality tools integrated (pytest, black, mypy)
- Requirements management implemented
- Git workflow established

### Phase 2: Development Process
- Core feature implementation workflow
- Automated quality gates
- Continuous integration setup
- Code review guidelines

## Quality Gates

### Pre-commit Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code formatted: `black src/ tests/`
- [ ] No linting errors: `flake8 src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Structure validation passes: `pytest tests/test_project_structure.py -v`

### Commit Standards
- Small, focused commits
- Clear commit messages describing changes
- Test coverage for new functionality
- Documentation updates for user-facing changes