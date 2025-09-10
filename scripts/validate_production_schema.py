#!/usr/bin/env python3
"""
Production Schema Validation Script

This script validates that all field IDs defined in field_mappings.py
actually exist in the production Airtable base and have the correct types.

Usage:
    python scripts/validate_production_schema.py

    Or as part of CI/CD:
    python scripts/validate_production_schema.py --ci
"""

import json
import os
import sys
from typing import Any, Dict, List, Tuple

import requests

# Add the project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config.field_mappings import AirtableFieldMapping  # noqa: E402


def fetch_airtable_schema(api_key: str, base_id: str, table_id: str) -> Dict[str, Any]:
    """Fetch table schema directly from Airtable API."""
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Find the target table
        for table in data.get("tables", []):
            if table.get("id") == table_id:
                return table

        raise ValueError(f"Table {table_id} not found in base {base_id}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Airtable API: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from Airtable API: {e}")


def validate_field_mappings(
    airtable_schema: Dict[str, Any],
) -> Tuple[List[str], List[str], List[str]]:
    """
    Validate field mappings against live Airtable schema.

    Returns:
        Tuple of (valid_fields, missing_fields, type_mismatches)
    """
    valid_fields = []
    missing_fields = []
    type_mismatches = []

    # Create a map of field IDs to field data from Airtable
    airtable_fields = {
        field["id"]: field for field in airtable_schema.get("fields", [])
    }

    # Validate each field mapping
    for python_name, airtable_id in AirtableFieldMapping.AIRTABLE_FIELD_IDS.items():
        if airtable_id in airtable_fields:
            airtable_field = airtable_fields[airtable_id]
            expected_type = AirtableFieldMapping.FIELD_TYPES.get(python_name)
            actual_type = airtable_field.get("type", "").upper()

            # Map Airtable types to our internal types
            type_mapping = {
                "SINGLELINETEXT": "TEXT",
                "MULTILINETEXT": "TEXT",
                "EMAIL": "TEXT",
                "PHONENUMBER": "TEXT",
                "URL": "TEXT",
                "NUMBER": "NUMBER",
                "PERCENT": "NUMBER",
                "CURRENCY": "NUMBER",
                "RATING": "NUMBER",
                "DATE": "DATE",
                "DATETIME": "DATE",
                "SINGLESELECT": "SELECT",
                "MULTIPLESELECTS": "MULTISELECT",
                "MULTIPLELOOKUPVALUES": "LOOKUP",
                "CHECKBOX": "CHECKBOX",
                "BARCODE": "TEXT",
                "BUTTON": "BUTTON",
                "COLLABORATOR": "COLLABORATOR",
                "CREATEDBY": "COLLABORATOR",
                "CREATEDTIME": "DATE",
                "LASTMODIFIEDBY": "COLLABORATOR",
                "LASTMODIFIEDTIME": "DATE",
            }

            normalized_type = type_mapping.get(actual_type, actual_type)

            if expected_type and normalized_type != expected_type:
                type_mismatches.append(
                    f"{python_name}: expected {expected_type}, got {actual_type}"
                )
            else:
                valid_fields.append(python_name)
        else:
            missing_fields.append(f"{python_name} (ID: {airtable_id})")

    return valid_fields, missing_fields, type_mismatches


def validate_production_schema(ci_mode: bool = False) -> bool:
    """
    Validate production schema and return success status.

    Args:
        ci_mode: If True, suppress interactive output for CI/CD

    Returns:
        True if validation passes, False otherwise
    """
    if not ci_mode:
        print("🔍 Production Schema Validation")
        print("=" * 50)

    # Load credentials from environment
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID", "appRp7Vby2JMzN0mC")
    table_id = os.getenv("AIRTABLE_TABLE_ID", "tbl8ivwOdAUvMi3Jy")

    if not api_key:
        if ci_mode:
            print("ERROR: AIRTABLE_API_KEY not set")
        else:
            print("❌ AIRTABLE_API_KEY environment variable not found")
            print()
            print("💡 Please set the environment variable:")
            print("   export AIRTABLE_API_KEY='your_api_key_here'")
        return False

    try:
        if not ci_mode:
            print(f"📊 Validating against base: {base_id}")
            print(f"📋 Table ID: {table_id}")
            print()
            print("📡 Fetching production schema...")

        # Fetch live schema
        schema = fetch_airtable_schema(api_key, base_id, table_id)

        if not ci_mode:
            field_count = len(schema.get("fields", []))
            print(f"✅ Connected to Airtable (found {field_count} fields)")
            print()

        # Validate field mappings
        valid, missing, mismatches = validate_field_mappings(schema)

        # Report results
        total_fields = len(AirtableFieldMapping.AIRTABLE_FIELD_IDS)
        validation_passed = len(missing) == 0 and len(mismatches) == 0

        if not ci_mode:
            print("📋 Validation Results:")
            print("-" * 40)
            print(f"Total fields configured: {total_fields}")
            print(f"✅ Valid fields: {len(valid)}")

            if missing:
                print(f"❌ Missing fields: {len(missing)}")
                for field in missing:
                    print(f"   - {field}")

            if mismatches:
                print(f"⚠️  Type mismatches: {len(mismatches)}")
                for mismatch in mismatches:
                    print(f"   - {mismatch}")

            print()

            # Special check for DateOfBirth and Age fields
            target_fields = ["date_of_birth", "age"]
            print("🎯 Target Fields Validation (DateOfBirth and Age):")
            print("-" * 40)

            for field in target_fields:
                if field in valid:
                    field_id = AirtableFieldMapping.AIRTABLE_FIELD_IDS[field]
                    print(f"✅ {field}: Valid (ID: {field_id})")
                elif field in [f.split()[0] for f in missing]:
                    print(f"❌ {field}: Missing from production")
                else:
                    print(f"⚠️  {field}: Type mismatch")

            print()

            if validation_passed:
                print("✅ Schema validation PASSED!")
                print(
                    "   All configured fields exist in production with correct types."
                )
            else:
                print("❌ Schema validation FAILED!")
                print("   Please update field_mappings.py to match production schema.")

        else:
            # CI mode - concise output
            if validation_passed:
                print(f"PASS: All {total_fields} fields validated successfully")
            else:
                print(
                    f"FAIL: {len(missing)} missing, {len(mismatches)} type mismatches"
                )
                if missing:
                    print(f"Missing: {', '.join(f.split()[0] for f in missing)}")
                if mismatches:
                    print(
                        f"Mismatches: {', '.join(m.split(':')[0] for m in mismatches)}"
                    )

        return validation_passed

    except ConnectionError as e:
        error_msg = f"Connection error: {e}"
        if ci_mode:
            print(f"ERROR: {error_msg}")
        else:
            print(f"❌ {error_msg}")
            print()
            print("💡 Troubleshooting tips:")
            print("   1. Check your internet connection")
            print("   2. Verify the API key is valid")
            print("   3. Ensure the base and table IDs are correct")
        return False

    except ValueError as e:
        error_msg = f"Validation error: {e}"
        if ci_mode:
            print(f"ERROR: {error_msg}")
        else:
            print(f"❌ {error_msg}")
        return False

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        if ci_mode:
            print(f"ERROR: {error_msg}")
        else:
            print(f"❌ {error_msg}")
        return False


def main():
    """Main entry point for the validation script."""
    # Check for CI mode
    ci_mode = "--ci" in sys.argv or os.getenv("CI") == "true"

    # Run validation
    success = validate_production_schema(ci_mode)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
