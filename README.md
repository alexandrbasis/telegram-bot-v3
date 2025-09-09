# Tres Dias Telegram Bot v3

A simple, well-structured Telegram bot for managing Tres Dias event participants.

## Features

- **Participant Search**: Enhanced Russian/English name search with fuzzy matching
- **Interactive Editing**: Complete participant profile editing with 13 editable fields
- **Save/Cancel Workflow**: Confirmation screens and error recovery for data safety
- **Payment Tracking**: Track payment status and generate reports  
- **Data Export**: Export participant data in various formats
- **Database Abstraction**: Easy migration between different database backends

## Architecture

3-layer architecture with database abstraction:
- **Bot Layer**: Telegram handlers and user interface
- **Service Layer**: Business logic and data processing
- **Data Layer**: Database abstraction with repository pattern

## Quick Setup

```bash
# 1. Clone and setup
git clone [repository]
cd telegram-bot-v3
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements/dev.txt

# 2. Configuration
cp .env.example .env
# Edit .env with your bot token and Airtable credentials

# 3. Run tests
pytest tests/ -v

# 4. Start bot
python src/main.py
```

## Development

See [docs/development/development-workflow.md](docs/development/development-workflow.md) for detailed development guidelines.

## Documentation

- [Architecture Overview](docs/architecture/architecture-overview.md)
- [Feature Specifications](docs/business/feature-specifications.md)
- [API Design](docs/architecture/api-design.md)
- [Testing Strategy](docs/development/testing-strategy.md)

## License

Private use - Alexandr Basis
npx claude-code-templates@latest --analytics