# Tres Dias Telegram Bot v3

Telegram assistant that gives Tres Dias retreat leaders live access to participant data, streamlined editing, and rich reporting — all through a secure chat interface backed by Airtable.

---

## Business Use
- **Single source of truth**: Coordinators browse, search, and edit retreat participant records without leaving Telegram.
- **Bilingual experience**: Supports Russian and English lookups so mixed-language teams stay productive.
- **Operational readiness**: Floor, room, and department views keep logistics, dining, and prayer teams aligned.
- **Rapid exports**: Generates CSV snapshots (participants, ROE, Bible readers) that mirror Airtable views for off-platform sharing.
- **Leadership controls**: Role-based permissions (viewer, coordinator, admin) protect sensitive information while keeping teams informed.

## Technical Solution
- **Clean 3-layer architecture** (`src/bot`, `src/services`, `src/data`) isolates Telegram UX, business rules, and Airtable I/O.
- **Airtable integration** with throttled client, field mapping, and repository abstraction for testability.
- **Stateful conversations** driven by `python-telegram-bot` create guided flows for search, editing, exports, and schedule browsing.
- **Inline editing engine** validates 13+ fields, tracks diffs, and confirms saves/cancels before writing back to Airtable.
- **Observability baseline**: Structured logging, hashed IDs for privacy, and optional daily statistics reports.

## Key Challenges & Responses
- **Fuzzy multilingual search** → Transliteration helpers, similarity scoring, and nickname support deliver reliable matches.
- **Rate-limited API** → Built-in throttling (5 req/s), batching, and retry-safe workflows keep Airtable happy.
- **Telegram UX limits** → Paginated keyboards, chunked messages, and progress indicators avoid 4 KB payload limits.
- **Granular access control** → Authorization decorators and cached role checks stay under 50 ms while respecting hierarchy.
- **Resilient editing** → Save/cancel checkpoints, retry prompts, and change previews prevent accidental data loss.

## Feature Highlights
- **Search & Discovery**: Name, room, floor, and department searches with interactive keyboards.
- **Participant Management**: Inline profile editing with validation, confirmation screens, and audit-friendly logs.
- **Bulk & Exports**: Department and role lists plus CSV exports aligned to Airtable schemas.
- **Schedule & Notifications**: Feature-flagged four-day schedule browser and optional daily stats push.
- **Security & Compliance**: Role filtering, sanitized inputs, temporary-file hygiene, and Docker non-root runtime.

## Telegram Commands
| Audience | Command | Purpose |
|----------|---------|---------|
| All users | `/start`, `/help` | Welcome flow and full guidance |
| Viewer+ | `/search <query>` | Bilingual fuzzy participant search |
| Viewer+ | `/search_room <room>` / `/search_floor <floor>` | Room or floor rollups |
| Admin | `/export` | Guided CSV export wizard |
| Admin | `/auth_refresh`, `/notifications`, `/set_notification_time`, `/test_stats`, `/logging` | Operational controls |
| Viewer+ (flagged) | `/schedule` | Four-day retreat timeline |

Quick-access buttons include **Поиск участников**, **Получить список**, and **Главное меню** for non-command navigation.

## Architecture at a Glance
```
┌──────────────────────────┐
│ Bot Layer (src/bot)      │ Telegram handlers, keyboards, conversation state
└──────────────┬───────────┘
               │
┌──────────────▼───────────┐
│ Service Layer             │ Business rules, validation, formatting
└──────────────┬───────────┘
               │
┌──────────────▼───────────┐
│ Data Layer                │ Airtable client, repositories, caching helpers
└──────────────────────────┘
```
Pydantic models (`src/models`) enforce schemas, while utilities (`src/utils`) handle transliteration, similarity scoring, and formatting.

## Getting Started
```bash
# 1. Environment
python -m venv venv
source venv/bin/activate

# 2. Dependencies
pip install -r requirements/dev.txt

# 3. Environment variables
cp .env.example .env  # fill in Airtable + Telegram secrets

# 4a. Run the bot (script)
./start_bot.sh

# 4b. Or run manually
python -m src.main
```

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=...              # required
AIRTABLE_API_KEY=...                # required
AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC  # default base
AIRTABLE_TABLE_NAME=Participants    # optional override
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy # optional override
TELEGRAM_ADMIN_IDS=1,2,3
TELEGRAM_COORDINATOR_IDS=...
TELEGRAM_VIEWER_IDS=...
DAILY_STATS_ENABLED=false
NOTIFICATION_TIME=09:00
NOTIFICATION_TIMEZONE=UTC
NOTIFICATION_ADMIN_USER_ID=...
LOG_LEVEL=INFO
ENVIRONMENT=development
TELEGRAM_CONVERSATION_TIMEOUT_MINUTES=30
```

## Validation & Quality Checks
All automated tests succeed on macOS (Python 3.11):
```bash
./venv/bin/pytest tests -q
# 1680 passed, 9 skipped (9.13s)
```
Run `./venv/bin/mypy`, `./venv/bin/flake8`, `./venv/bin/black`, and `./venv/bin/isort` for full pre-flight checks.


## Acknowledgments
Built for the Tres Dias community to keep retreat participant management reliable, secure, and effortless.
