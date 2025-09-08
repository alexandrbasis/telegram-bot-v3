"""
Tests for field mapping completeness validation.

This test suite validates that all field references used in the repository
have corresponding centralized field mappings, detecting any missing mappings.
"""

import inspect
import re
from typing import Dict, List, Set

import pytest

from src.config.field_mappings import AirtableFieldMapping
from src.data.airtable.airtable_participant_repo import \
    AirtableParticipantRepository


class TestFieldMappingsCompleteness:
    """Test suite for field mapping completeness validation."""

    def test_all_repository_field_references_have_mappings(self):
        """Test that all field references in repository methods have corresponding mappings."""
        # Get all methods from the repository
        repository_methods = [
            method
            for method in dir(AirtableParticipantRepository)
            if not method.startswith("_")
            and callable(getattr(AirtableParticipantRepository, method))
        ]

        # Extract field references from repository source code
        missing_mappings = []
        found_field_references = set()

        for method_name in repository_methods:
            method = getattr(AirtableParticipantRepository, method_name)
            try:
                source = inspect.getsource(method)

                # Look for search_by_field calls with string literals
                field_calls = re.findall(
                    r'search_by_field\(\s*["\']([^"\']+)["\']', source
                )

                for field_name in field_calls:
                    found_field_references.add(field_name)
                    # Check if this field has a corresponding mapping
                    field_id = AirtableFieldMapping.get_field_id(field_name)
                    if field_id is None:
                        missing_mappings.append(
                            {
                                "method": method_name,
                                "field_name": field_name,
                                "type": "search_by_field_call",
                            }
                        )

            except (OSError, TypeError):
                # Skip if we can't get source (built-in methods, etc.)
                continue

        # Report findings for any string-literal usages found
        if missing_mappings:
            error_msg = "Found field references without mappings:\n"
            for missing in missing_mappings:
                error_msg += f"  - Method '{missing['method']}': field '{missing['field_name']}' (type: {missing['type']})\n"
            pytest.fail(error_msg)
        # Note: Repository is expected to use centralized mapping helpers and avoid
        # string-literal field references entirely. Therefore we intentionally do
        # NOT require finding any literals here.

    def test_no_hardcoded_field_references_in_repository(self):
        """Test that repository methods don't use hardcoded field references."""
        # Get repository source code
        repository_source = inspect.getsource(AirtableParticipantRepository)

        # Define patterns that indicate hardcoded field references
        hardcoded_patterns = [
            r'search_by_field\(\s*["\'][^"\']+["\']',  # search_by_field("FieldName")
            r"\.search_by_formula\([^)]*{[^}]*}[^)]*\)",  # formula with {FieldName}
        ]

        violations = []

        for pattern in hardcoded_patterns:
            matches = re.finditer(pattern, repository_source, re.MULTILINE)
            for match in matches:
                # Skip if this is using field mapping methods
                context = repository_source[
                    max(0, match.start() - 100) : match.end() + 100
                ]
                if (
                    "get_airtable_field_name" in context
                    or "build_formula_field" in context
                    or "AirtableFieldMapping" in context
                ):
                    continue

                # This is a potential hardcoded reference
                line_num = repository_source[: match.start()].count("\n") + 1
                violations.append(
                    {
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group(),
                        "context": context.strip(),
                    }
                )

        if violations:
            error_msg = (
                "Found hardcoded field references (should use centralized mappings):\n"
            )
            for violation in violations:
                error_msg += f"  - Line {violation['line']}: {violation['match']}\n"
            pytest.fail(error_msg)

    def test_centralized_field_mapping_coverage(self):
        """Test that centralized field mappings cover all expected fields."""
        # Get all Python field names that should have mappings
        expected_python_fields = {
            "full_name_ru",
            "full_name_en",
            "church",
            "country_and_city",
            "submitted_by",
            "contact_information",
            "telegram_id",
            "gender",
            "size",
            "role",
            "department",
            "payment_status",
            "payment_amount",
            "payment_date",
            "floor",
            "room_number",
            "record_id",
        }

        # Get actual mapped fields
        actual_python_fields = set(AirtableFieldMapping.get_all_python_fields())

        # Check for missing mappings
        missing_fields = expected_python_fields - actual_python_fields
        extra_fields = actual_python_fields - expected_python_fields

        if missing_fields:
            pytest.fail(f"Missing field mappings for: {sorted(missing_fields)}")

        # Extra fields are okay, but let's log them for awareness
        if extra_fields:
            print(
                f"Note: Extra field mappings found (not an error): {sorted(extra_fields)}"
            )

    def test_formula_field_references_coverage(self):
        """Test that formula field references cover commonly used fields."""
        # Fields that should have formula references (used in search methods)
        expected_formula_fields = {"full_name_ru", "full_name_en"}

        actual_formula_fields = set(
            AirtableFieldMapping.FORMULA_FIELD_REFERENCES.keys()
        )

        missing_formula_fields = expected_formula_fields - actual_formula_fields

        if missing_formula_fields:
            pytest.fail(
                f"Missing formula field references for: {sorted(missing_formula_fields)}"
            )

        # Verify formula references produce correct format
        for field in actual_formula_fields:
            formula_ref = AirtableFieldMapping.build_formula_field(field)
            assert (
                formula_ref is not None
            ), f"Formula field reference for '{field}' should not be None"
            assert formula_ref.startswith("{") and formula_ref.endswith(
                "}"
            ), f"Formula reference '{formula_ref}' should be wrapped in curly braces"

    def test_field_mapping_bidirectional_completeness(self):
        """Test that all field mappings are bidirectionally consistent."""
        python_fields = AirtableFieldMapping.get_all_python_fields()
        airtable_fields = AirtableFieldMapping.get_all_airtable_fields()

        # Test forward mapping completeness
        for python_field in python_fields:
            airtable_field = AirtableFieldMapping.get_airtable_field_name(python_field)
            assert (
                airtable_field is not None
            ), f"Python field '{python_field}' should map to Airtable field"
            assert (
                airtable_field in airtable_fields
            ), f"Mapped Airtable field '{airtable_field}' not in field list"

        # Test reverse mapping completeness
        for airtable_field in airtable_fields:
            python_field = AirtableFieldMapping.get_python_field_name(airtable_field)
            assert (
                python_field is not None
            ), f"Airtable field '{airtable_field}' should map to Python field"
            assert (
                python_field in python_fields
            ), f"Mapped Python field '{python_field}' not in field list"

    def test_field_id_mapping_completeness(self):
        """Test that all Airtable fields have corresponding Field IDs."""
        airtable_fields = AirtableFieldMapping.get_all_airtable_fields()

        missing_field_ids = []
        invalid_field_ids = []

        for field_name in airtable_fields:
            field_id = AirtableFieldMapping.get_field_id(field_name)

            if field_id is None:
                missing_field_ids.append(field_name)
            elif not (field_id.startswith("fld") and len(field_id) == 17):
                # Airtable field IDs should start with 'fld' and be 17 characters
                invalid_field_ids.append((field_name, field_id))

        errors = []
        if missing_field_ids:
            errors.append(f"Fields missing Field IDs: {missing_field_ids}")
        if invalid_field_ids:
            errors.append(f"Fields with invalid Field IDs: {invalid_field_ids}")

        if errors:
            pytest.fail("\n".join(errors))

    def test_repository_uses_centralized_mappings_consistently(self):
        """Test that repository methods consistently use centralized field mappings."""
        # Get repository source
        repository_source = inspect.getsource(AirtableParticipantRepository)

        # Count usage of centralized mapping methods
        mapping_usage = {
            "get_airtable_field_name": len(
                re.findall(r"get_airtable_field_name\(", repository_source)
            ),
            "build_formula_field": len(
                re.findall(r"build_formula_field\(", repository_source)
            ),
            "AirtableFieldMapping_import": "AirtableFieldMapping" in repository_source,
        }

        # Verify import exists
        assert mapping_usage[
            "AirtableFieldMapping_import"
        ], "Repository should import AirtableFieldMapping for centralized field access"

        # Verify actual usage (should have multiple uses after centralization)
        total_usage = (
            mapping_usage["get_airtable_field_name"]
            + mapping_usage["build_formula_field"]
        )
        assert (
            total_usage >= 3
        ), f"Repository should use centralized mapping methods (found {total_usage} usages)"

        print(f"Centralized mapping usage: {mapping_usage}")  # For visibility
