# Introduce Airtable Client Reuse Strategy

## Summary
Service factory helpers build a fresh `AirtableClient` each time, preventing connection reuse and per-process rate-limit coordination. Design a lightweight caching strategy for Airtable clients.

## References
- `src/services/service_factory.py:18-63`
- `src/data/airtable/airtable_client.py`

## Goals
- Provide shared `AirtableClient` instances across handlers while preserving configurability for tests.
- Ensure rate-limiter state survives across sequential operations.
- Document how to override the shared client during testing.

## Acceptance Criteria
- Services fetched via `service_factory` reuse clients/config where appropriate.
- Tests validate that repeated calls obtain the same client (unless explicitly reset).
- No regressions in dependency injection flexibility (tests still able to mock).

