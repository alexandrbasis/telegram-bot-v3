# Refactor `export_to_csv` for Async Contexts

## Summary
`ParticipantExportService.export_to_csv` invokes `loop.run_until_complete` even if an event loop is already running, which breaks under PTB's async runtime. Provide a safe synchronous entry point without risking `RuntimeError`.

## References
- `src/services/participant_export_service.py:110-134`
- `src/bot/handlers/export_handlers.py`

## Goals
- Avoid calling `run_until_complete` when inside an active loop.
- Expose a coroutine-friendly API that the export handler can await.
- Cover the behavior with tests (including async contexts) to prevent regression.

## Acceptance Criteria
- Export command works under the async PTB application without raising `RuntimeError`.
- Unit/integration tests demonstrate both sync and async invocation paths succeed.
- Documentation/comments updated to clarify usage expectations.

