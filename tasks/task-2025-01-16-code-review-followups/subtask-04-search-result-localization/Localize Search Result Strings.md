# Localize Search Result Strings

## Summary
Search result formatting mixes English labels (`Floor`, `Room`, `Date of Birth`, `N/A`, `years`) into predominantly Russian responses. Align these labels and fallbacks with the bot's Russian UX language.

## References
- `src/services/search_service.py:135-208`
- `src/bot/messages.py`

## Goals
- Provide Russian translations for structural labels and fallback text in search result summaries.
- Escape Markdown characters properly after localization adjustments.
- Consider centralizing reusable labels in `bot/messages.py`.

## Acceptance Criteria
- Search results display consistent Russian messaging (including fallbacks like “Не указано”).
- Unit tests cover localization output to prevent reintroduction of English strings.
- No regressions in Markdown rendering or formatting.

## Change Log
- Added localized search result labels (этаж, комната, дата рождения, возраст, etc.) and age pluralization via `SearchResultLabels` in `bot/messages.py`.
- Updated `format_participant_result` to surface Russian fallbacks such as “Не указано” and formatted dates, with adjusted unit tests to cover the localized output.
