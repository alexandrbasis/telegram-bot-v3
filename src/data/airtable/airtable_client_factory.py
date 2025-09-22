"""
Factory for creating table-specific Airtable clients.

This factory provides a centralized way to create AirtableClient instances
configured for different tables while maintaining consistency and
supporting dependency injection.
"""

from typing import Optional

from src.data.airtable.airtable_client import AirtableClient
from src.config.settings import DatabaseSettings


class AirtableClientFactory:
    """
    Factory for creating table-specific Airtable clients.

    This factory uses the DatabaseSettings to get table-specific configurations
    and creates appropriately configured AirtableClient instances.
    """

    def __init__(self, database_settings: Optional[DatabaseSettings] = None):
        """
        Initialize the factory.

        Args:
            database_settings: DatabaseSettings instance. If None, creates a new one.
        """
        self.database_settings = database_settings or DatabaseSettings()

    def create_client(self, table_type: str) -> AirtableClient:
        """
        Create an AirtableClient for the specified table type.

        Args:
            table_type: The type of table ('participants', 'bible_readers', 'roe')

        Returns:
            Configured AirtableClient instance

        Raises:
            ValueError: If table_type is not supported
        """
        supported_types = ["participants", "bible_readers", "roe"]
        if table_type not in supported_types:
            raise ValueError(
                f"Unsupported table type: {table_type}. "
                f"Supported types: {supported_types}"
            )

        # Get table-specific configuration
        airtable_config = self.database_settings.to_airtable_config(table_type)

        # Create and return the client
        return AirtableClient(airtable_config)
