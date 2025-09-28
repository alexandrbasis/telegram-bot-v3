# Fix CI Issues Command

## PRIMARY OBJECTIVE
Fix all CI pipeline failures blocking the PR merge while maintaining code quality and test integrity.

## CONTEXT & CONSTRAINTS
- CI pipeline failed during merge attempt to main branch
- Must resolve all failures without compromising code quality
- Preserve existing test coverage and validation logic
- CI includes: pytest (with coverage ≥80%), mypy, flake8, black, isort, pip-audit, bandit, docker build

## ANALYSIS REQUIREMENTS
1. **Identify CI Failures:**
   - Run `gh run list --workflow=ci-pipeline --limit=3` to check recent CI status
   - Review failure logs to identify specific issues
   - Categorize failures by type (formatting, typing, tests, linting, security, docker)

2. **Execute Diagnostic Checks:**
   - `venv/bin/pytest -v --cov-fail-under=80` - Run test suite with coverage
   - `venv/bin/mypy src --no-error-summary` - Type checking
   - `venv/bin/flake8 src tests` - Linting
   - `venv/bin/black --check src tests` - Format checking
   - `venv/bin/isort --check-only src tests` - Import sorting

## RESOLUTION PROCESS
1. **Fix Formatting Issues First:**
   - Run `venv/bin/isort src tests` if import sorting fails
   - Run `venv/bin/black src tests` if formatting fails
   - These are automated fixes - apply immediately

2. **Address Type Errors:**
   - Fix mypy violations maintaining type safety
   - Add appropriate type hints, don't use `# type: ignore` unless justified

3. **Resolve Test Failures:**
   - Fix failing tests by correcting implementation bugs
   - DO NOT simplify tests or reduce assertions
   - Maintain or improve test coverage (≥80% target)

4. **Fix Linting Issues:**
   - Address flake8 violations (E501 line length, etc.)
   - Refactor code properly, don't just suppress warnings

5. **Security Issues:**
   - Fix pip-audit vulnerabilities by updating dependencies
   - Address bandit security warnings in `src/` directory

6. **Docker Build Issues:**
   - Ensure Docker build succeeds and smoke test passes
   - Fix any import or runtime errors in containerized environment

## VERIFICATION REQUIREMENTS
Before completion, execute ALL checks and confirm passing:
```bash
# Run full CI validation suite (matches .github/workflows/ci-pipeline.yml)
venv/bin/black --check src tests && \
venv/bin/isort --check-only src tests && \
venv/bin/flake8 src tests && \
venv/bin/mypy src --no-error-summary && \
venv/bin/pytest -v --cov-fail-under=80
```

Optional additional checks (if security/docker jobs are failing):
```bash
# Security checks
pip-audit -r requirements/base.txt && pip-audit -r requirements/dev.txt && pip-audit -r requirements/test.txt
bandit -r src -ll

# Docker build test
docker build -t app:ci .
```

## DEFINITION OF DONE
- [ ] All CI checks pass (lint, typing, format, tests, security, docker)
- [ ] Test coverage maintained at ≥80%
- [ ] No test logic simplified or removed
- [ ] Security vulnerabilities resolved (pip-audit, bandit)
- [ ] Docker build and smoke test pass
- [ ] GitHub CI status shows green checkmark
- [ ] Ready for clean merge to main branch