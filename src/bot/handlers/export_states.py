"""
Export conversation states and callback data patterns.

Defines enumeration-based states for export selection workflow and
callback data structures for inline keyboard interactions.
"""

from typing import Optional


class ExportStates:
    """Export conversation states for state management."""

    SELECTING_EXPORT_TYPE = "selecting_export_type"
    SELECTING_DEPARTMENT = "selecting_department"
    PROCESSING_EXPORT = "processing_export"


class ExportCallbackData:
    """Export callback data patterns for inline keyboards."""

    # Export type selections
    EXPORT_ALL = "export:all"
    EXPORT_TEAM = "export:team"
    EXPORT_CANDIDATES = "export:candidates"
    EXPORT_BY_DEPARTMENT = "export:by_department"
    EXPORT_BIBLE_READERS = "export:bible_readers"
    EXPORT_ROE = "export:roe"

    # Navigation
    CANCEL = "export:cancel"
    BACK_TO_EXPORT_SELECTION = "export:back"

    @staticmethod
    def department_callback(department: str) -> str:
        """
        Generate callback data for department selection.

        Args:
            department: Name of the department

        Returns:
            Formatted callback data string
        """
        return f"export:department:{department}"

    @staticmethod
    def parse_export_type(callback_data: str) -> Optional[str]:
        """
        Parse export type from callback data.

        Args:
            callback_data: Callback data string

        Returns:
            Export type or None if invalid pattern
        """
        if callback_data.startswith("export:") and ":" not in callback_data[7:]:
            return callback_data[7:]  # Remove "export:" prefix
        return None

    @staticmethod
    def parse_department(callback_data: str) -> Optional[str]:
        """
        Parse department from callback data.

        Args:
            callback_data: Callback data string

        Returns:
            Department name or None if invalid pattern
        """
        if callback_data.startswith("export:department:"):
            return callback_data[18:]  # Remove "export:department:" prefix
        return None