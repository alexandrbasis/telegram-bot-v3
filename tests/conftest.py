"""
Test configuration for pytest.

This file ensures that the src module can be imported during testing
without requiring PYTHONPATH setup or editable install.
"""

import sys
from pathlib import Path


def pytest_configure(config):
    """Add src directory to Python path for test imports."""
    # Get the project root directory (parent of tests directory)
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"

    # Add src to Python path if not already present
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
