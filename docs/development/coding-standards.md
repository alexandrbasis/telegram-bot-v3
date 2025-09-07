# Coding Standards

## Code Quality Requirements

### Static Analysis Standards
- **Zero tolerance for linting violations**: All code must pass `flake8` checks without warnings or errors
- **Complete type coverage**: All functions and methods must have proper type annotations
- **MyPy compliance**: Code must pass `mypy` static type checking without errors

### Code Quality Commands
```bash
# Required checks before code submission
./venv/bin/flake8 src tests          # Must return 0 violations
./venv/bin/mypy src --no-error-summary  # Must return 0 errors
./venv/bin/pytest tests/unit -q     # All tests must pass
```

### Type Annotation Standards
- All function return types must be explicitly annotated
- Use `Optional[Type]` for nullable values with proper None guards
- Dict and List types should be fully specified (e.g., `Dict[str, int]`)
- Avoid `Any` type - prefer specific type annotations

### Formatting Standards
- Remove trailing whitespace from all files
- Ensure proper blank line spacing (2 lines between top-level definitions)
- End all files with a single newline character
- Use consistent indentation (spaces, not tabs)

### File Organization
- Follow the established 3-layer architecture (Bot → Services → Data)
- Keep behavioral changes separate from formatting/typing improvements
- Make minimal, surgical code modifications when fixing quality issues