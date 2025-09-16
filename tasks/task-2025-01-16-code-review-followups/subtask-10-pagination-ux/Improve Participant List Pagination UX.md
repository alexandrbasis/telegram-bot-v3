# Improve Participant List Pagination UX

## Summary
Participant list pagination clamps offsets to the last item, producing single-entry pages when users jump past the end. Provide a smoother experience by snapping to the previous full page and communicating bounds clearly.

## References
- `src/services/participant_list_service.py:70-134`
- Pagination keyboard handlers (if any)

## Goals
- Adjust pagination logic to handle out-of-range offsets gracefully.
- Update bot messaging/keyboard state to reflect available navigation.
- Add tests covering boundary navigation cases.

## Acceptance Criteria
- Jumping beyond the last page moves users to the final full page instead of a single item.
- Pagination metadata (`has_prev`, `has_next`, offsets) stays consistent.
- Tests cover edge cases for offsets before 0 and beyond total count.

