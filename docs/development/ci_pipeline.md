CI Pipeline Overview
====================

This repository uses GitHub Actions to enforce code quality and provide quick feedback on every change.

Triggers
--------
- pull_request → target: `main`
- push → branch: `main`
- paths ignored: `docs/**`, `*.md`, `CHANGELOG.md`
- concurrency: cancels in‑progress runs on the same ref to reduce queue time

Jobs
----
- Lint (flake8)
  - Installs `requirements/dev.txt`
  - Runs `flake8 src tests`

- Type Check (mypy)
  - Uses `mypy.ini` for consistent settings
  - Runs `mypy src --no-error-summary`

- Format Check (black, isort)
  - `black --check src tests`
  - `isort --check-only src tests`

- Tests + Coverage (pytest)
  - Configured via `pytest.ini`
  - Default args: `--cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=80`
  - Uploads `coverage.xml` artifact

- Security (pip-audit)
  - Runs `pip-audit` against `requirements/base.txt`, `requirements/dev.txt`, and `requirements/test.txt`
  - Current policy: fail on any known vulnerability (can be tuned later for severity thresholds)

- Docker Build + Smoke Test
  - Builds the app image using the repository `Dockerfile`
  - Smoke test: runs a short Python command inside the container to import and instantiate the app
    without starting polling:
    `docker run --rm --entrypoint python -e TELEGRAM_BOT_TOKEN=dummy -e AIRTABLE_API_KEY=dummy app:ci -c "from src.main import create_application; create_application(); print('ok')"`

Local Parity
------------
- Lint: `flake8 src tests`
- Types: `mypy src --no-error-summary`
- Format: `black src tests && isort src tests`
- Tests: `pytest` (uses `pytest.ini` config)

Branch Protection
-----------------
Enable required status checks for `main`:
- Settings → Branches → Add rule → Branch name pattern: `main`
- Require status checks to pass before merging → select:
  - Lint (flake8)
  - Type Check (mypy)
  - Format Check (black, isort)
  - Tests + Coverage (pytest)
  - Security (pip-audit)
  - Docker Build + Smoke Test
- Optional: Require PR approvals, dismiss stale approvals, and require conversation resolution

Notes
-----
- Python 3.11 is the CI target (matches production). Expand matrix if broader support is desired.
- Caching leverages `actions/setup-python` pip cache, keyed by requirements files.
- Security policy is initially conservative (fail on any). If this causes friction, adopt a severity filter policy in a future iteration.

