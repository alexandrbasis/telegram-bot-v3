"""
Tests to verify that contact information search already uses proper field mapping.

This test validates that the find_by_contact_information method correctly uses 
centralized field mapping constants instead of hardcoded field name strings.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.models.participant import Participant
from src.config.field_mappings import AirtableFieldMapping


class TestContactInfoMappingVerification:
    """Test suite to verify contact information mapping usage."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AirtableClient for testing."""
        client = MagicMock()
        client.search_by_field = AsyncMock()
        return client

    @pytest.fixture
    def repository(self, mock_client):
        """Create AirtableParticipantRepository with mock client."""
        return AirtableParticipantRepository(mock_client)

    @pytest.fixture
    def mock_participant_record(self):
        """Create a mock participant record for testing."""
        return {
            "id": "recTestRecord123",
            "fields": {
                "FullNameRU": "Тестовый Участник",
                "FullNameEN": "Test Participant",
                "ContactInformation": "test@example.com",
                "Role": "CANDIDATE",
            }
        }

    @pytest.mark.asyncio
    async def test_find_by_contact_information_uses_field_mapping(self, repository, mock_client, mock_participant_record):
        """Test that find_by_contact_information uses centralized field mapping."""
        # This test should PASS if contact info already uses proper mapping
        # or FAIL if it still uses hardcoded strings
        
        # Setup: Mock the client to return a participant record
        mock_client.search_by_field.return_value = [mock_participant_record]
        
        # Patch Participant.from_airtable_record to avoid complex object creation
        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant
            
            # Act: Call find_by_contact_information
            contact_info = "test@example.com"
            result = await repository.find_by_contact_information(contact_info)
            
            # Assert: Should use the centralized field mapping
            expected_field_name = AirtableFieldMapping.get_airtable_field_name("contact_information")
            actual_field_name = mock_client.search_by_field.call_args[0][0]
            
            # Check if it uses the correct field mapping
            if actual_field_name == expected_field_name:
                # PASS: Already using centralized mapping
                assert True, "Contact information search correctly uses centralized field mapping"
            else:
                # FAIL: Still using hardcoded string - this indicates current implementation issue
                assert False, f"Expected field mapping '{expected_field_name}', but got hardcoded '{actual_field_name}'. Contact info search needs centralization."

    @pytest.mark.asyncio
    async def test_contact_info_field_mapping_consistency(self, repository):
        """Test that contact information field mapping is consistent and correct."""
        # Verify the field mapping exists and is correct
        python_field = "contact_information"
        airtable_field = AirtableFieldMapping.get_airtable_field_name(python_field)
        
        assert airtable_field is not None, "Contact information field mapping should exist"
        assert airtable_field == "ContactInformation", f"Expected 'ContactInformation', got: {airtable_field}"
        
        # Test reverse mapping
        reverse_field = AirtableFieldMapping.get_python_field_name(airtable_field)
        assert reverse_field == python_field, "Reverse mapping should be consistent"

    @pytest.mark.asyncio
    async def test_contact_info_functionality_preserved(self, repository, mock_client, mock_participant_record):
        """Test that find_by_contact_information functionality is preserved."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [mock_participant_record]
        
        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant
            
            # Act
            result = await repository.find_by_contact_information("test@example.com")
            
            # Assert: Should return the participant (functionality preserved)
            assert result is not None
            assert result == mock_participant
            
            # Should call from_airtable_record with the correct record
            mock_from_record.assert_called_once_with(mock_participant_record)

    @pytest.mark.asyncio
    async def test_contact_info_not_found(self, repository, mock_client):
        """Test find_by_contact_information when no participant is found."""
        # Setup: Mock empty search result
        mock_client.search_by_field.return_value = []
        
        # Act
        result = await repository.find_by_contact_information("nonexistent@example.com")
        
        # Assert: Should return None
        assert result is None
        
        # Should still use proper field mapping (regardless of result)
        mock_client.search_by_field.assert_called_once()
        actual_field_name = mock_client.search_by_field.call_args[0][0]
        expected_field_name = AirtableFieldMapping.get_airtable_field_name("contact_information")
        
        # This assertion will help us understand current implementation
        if actual_field_name != expected_field_name:
            pytest.fail(f"Contact info search uses hardcoded '{actual_field_name}' instead of mapped '{expected_field_name}'")

    def test_current_implementation_status(self):
        """Test to document current implementation status of contact information search."""
        # This test documents whether the contact info method needs updating
        
        # Read the current repository implementation to check what it uses
        import inspect
        from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
        
        # Get the source code of find_by_contact_information method
        method = getattr(AirtableParticipantRepository, 'find_by_contact_information')
        source = inspect.getsource(method)
        
        # Check if it uses the proper field mapping pattern
        uses_mapping = "get_airtable_field_name" in source and "contact_information" in source
        uses_hardcoded_call = '"Contact Information"' in source and 'search_by_field(' in source
        
        if uses_mapping and not uses_hardcoded_call:
            # This is the desired state - uses field mapping, no hardcoded calls
            assert True, "Contact information search correctly uses centralized field mapping"
        elif uses_hardcoded_call and not uses_mapping:
            pytest.fail("Contact information search uses hardcoded 'Contact Information' string - needs centralization")
        elif uses_mapping and uses_hardcoded_call:
            # This shouldn't happen with proper implementation
            pytest.fail("Contact information method contains both mapping and hardcoded calls - check implementation")
        else:
            pytest.fail("Contact information implementation not found or unclear")