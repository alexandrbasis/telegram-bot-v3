# Optimize Enhanced Search Data Access

## Summary
`find_by_name_enhanced` currently calls `list_all()` for every query, pulling the entire participant dataset from Airtable and risking rate-limit pressure. Explore strategies to cut unnecessary reads.

## References
- `src/data/airtable/airtable_participant_repo.py:1093-1120`
- Airtable rate limit documentation

## Goals
- Evaluate caching, pagination, or Airtable-side filtering to minimize full-table scans.
- Measure the impact of proposed changes on API usage and response latency.
- Document trade-offs for chosen approach.

## Acceptance Criteria
- Search workflow no longer fetches the entire dataset on every query.
- Performance characteristics and rate-limit adherence are validated (via tests or instrumentation).
- Added tests confirm search results remain correct after optimization.

## Change Log
- Introduced a short-lived participant cache in `AirtableParticipantRepository` with automatic invalidation on create/update/delete/bulk operations.
- Updated fuzzy and enhanced name search methods to reuse cached participant lists and added tests covering cache reuse, expiry, and invalidation triggers.
