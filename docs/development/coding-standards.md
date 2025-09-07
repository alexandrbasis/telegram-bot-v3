# Coding Standards

## Asynchronous Programming Standards

### Modern Asyncio Patterns
The project consistently uses modern asyncio patterns for optimal performance and maintainability:

- **Use `asyncio.to_thread()` for blocking operations**: All blocking I/O operations, particularly Airtable API calls, use `asyncio.to_thread()` instead of the legacy `run_in_executor(None, ...)` pattern
- **Thread offloading**: Blocking SDK calls are properly offloaded to threads to prevent event loop blocking
- **Cancellation semantics**: `asyncio.to_thread()` provides identical cancellation behavior to `run_in_executor` but with cleaner syntax

### Implementation Example
```python
# Preferred: Modern asyncio.to_thread pattern
async def get_participant(self, record_id: str) -> Optional[Dict[str, Any]]:
    try:
        record = await asyncio.to_thread(self.table.get, record_id)
        return record['fields'] if record else None
    except Exception as e:
        logger.error(f"Failed to get participant {record_id}: {e}")
        raise AirtableAPIError(f"Failed to retrieve participant: {e}")

# Avoid: Legacy run_in_executor pattern
# await asyncio.get_running_loop().run_in_executor(None, self.table.get, record_id)
```

### Benefits
- **Improved readability**: Cleaner syntax without lambda expressions or partial functions
- **Better maintainability**: Direct function calls with clear parameter passing
- **Modern compatibility**: Aligns with Python 3.9+ best practices
- **Future-proofing**: Reduces reliance on direct event loop access patterns

*Additional code style and development standards will be documented here.*