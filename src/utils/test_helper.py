"""
Test helper utility for demonstrating indexer hook functionality.

This file was created to test the automatic index updating system.
It will trigger the PostToolUse hook which should update project_index.json.
"""


def test_function() -> str:
    """Simple test function to demonstrate indexer functionality."""
    return "Index hook test successful"


def debug_hook_test() -> str:
    """Debug function to test automatic hook triggering."""
    return "Hook debugging in progress..."


def test_hook_trigger() -> str:
    """Test function to trigger PostToolUse hook."""
    return "Testing hook trigger mechanism"


def another_test() -> str:
    """Another test to verify hook."""
    return "Hook test #2"


def final_hook_test() -> str:
    """Final test with bash -c wrapper."""
    return "Testing bash -c wrapper approach"


def wrapper_test() -> str:
    """Test with wrapper script approach."""
    return "Testing wrapper.sh script"


def hook_should_work_now() -> str:
    """Hook should trigger automatically now."""
    return "Hook testing final attempt"


class TestHelper:
    """Test helper class for indexer demonstration."""

    def __init__(self) -> None:
        self.message: str = "Indexer hook is working!"
        self.test_counter: int = 0

    def get_message(self) -> str:
        """Return the test message."""
        return self.message

    def increment_counter(self) -> int:
        """Increment test counter to verify hook functionality."""
        self.test_counter += 1
        return self.test_counter
