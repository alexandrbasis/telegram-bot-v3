#!/usr/bin/env python3
"""
Simplified Airtable Schema Discovery Script

This script fetches the current field structure from the live Airtable base
to identify field IDs, types, and options for DateOfBirth and Age fields.
"""

import json
import os
import sys
import requests
from typing import Any, Dict, List

# Add the project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def fetch_airtable_schema(api_key: str, base_id: str, table_id: str) -> Dict[str, Any]:
    """Fetch table schema directly from Airtable API."""
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Airtable API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    # Find the target table
    for table in data.get("tables", []):
        if table.get("id") == table_id:
            return table
    
    raise Exception(f"Table {table_id} not found in base {base_id}")


def format_field_info(field: Dict[str, Any]) -> Dict[str, Any]:
    """Format field information for display."""
    info = {
        "name": field.get("name", "Unknown"),
        "id": field.get("id", "Unknown"),
        "type": field.get("type", "Unknown"),
        "description": field.get("description", ""),
    }
    
    # Add options for select fields
    if field.get("options"):
        options = field["options"]
        if "choices" in options:
            info["choices"] = [
                {
                    "name": choice.get("name", "Unknown"),
                    "id": choice.get("id", "Unknown")
                }
                for choice in options["choices"]
            ]
    
    return info


def discover_schema() -> None:
    """Discover and display current Airtable schema."""
    print("🔍 Airtable Schema Discovery (Real API)")
    print("=" * 50)
    
    # Check if .env file exists in parent directory
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        print(f"💡 Found .env file at: {os.path.abspath(env_path)}")
        print("   Note: Environment variables should be loaded before running this script")
        print()
    
    # Load credentials from environment
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID", "appRp7Vby2JMzN0mC")
    table_id = os.getenv("AIRTABLE_TABLE_ID", "tbl8ivwOdAUvMi3Jy")
    
    if not api_key:
        print("❌ AIRTABLE_API_KEY environment variable not found")
        print()
        print("💡 Please set the environment variable before running this script:")
        print("   export AIRTABLE_API_KEY='your_api_key_here'")
        print()
        print("   Or source your .env file:")
        print("   source .env")
        print()
        print("   For permanent setup, add to your shell profile (~/.bashrc or ~/.zshrc)")
        sys.exit(1)
    
    # Validate API key format
    if not api_key.startswith('pat'):
        print("⚠️  Warning: API key doesn't start with 'pat' - may be invalid")
        print("   Airtable personal access tokens typically start with 'pat'")
        print()
    
    print(f"📊 Base ID: {base_id}")
    print(f"📋 Table ID: {table_id}")
    print()
    
    try:
        # Fetch table schema
        print("📡 Fetching table schema from live Airtable...")
        schema = fetch_airtable_schema(api_key, base_id, table_id)
        
        fields = schema.get("fields", [])
        print(f"✅ Found {len(fields)} fields")
        print()
        
        # Display all fields
        print("📋 All Fields:")
        print("-" * 40)
        all_field_info = []
        
        for field in fields:
            field_info = format_field_info(field)
            all_field_info.append(field_info)
            
            print(f"Name: {field_info['name']}")
            print(f"ID: {field_info['id']}")
            print(f"Type: {field_info['type']}")
            if field_info.get("description"):
                print(f"Description: {field_info['description']}")
            if field_info.get("choices"):
                print("Choices:")
                for choice in field_info["choices"]:
                    print(f"  - {choice['name']} (ID: {choice['id']})")
            print()
        
        # Look for target fields (DateOfBirth and Age)
        target_fields = ["DateOfBirth", "Age"]
        found_targets = []
        
        for field in fields:
            if field.get("name") in target_fields:
                found_targets.append(field)
        
        print("🎯 Target Fields (DateOfBirth and Age):")
        print("-" * 40)
        if found_targets:
            print(f"✅ Found {len(found_targets)} target field(s):")
            for field in found_targets:
                field_info = format_field_info(field)
                print(f"  🎯 {field_info['name']}")
                print(f"     ID: {field_info['id']}")
                print(f"     Type: {field_info['type']}")
                if field_info.get("description"):
                    print(f"     Description: {field_info['description']}")
                print()
        else:
            print("❌ No target fields found. Available fields:")
            for field in fields:
                print(f"  - {field.get('name')} ({field.get('type')})")
        
        # Save full schema
        output_file = "discovered_real_schema.json"
        schema_data = {
            "base_id": base_id,
            "table_id": table_id,
            "discovered_at": None,  # Will be set by json serializer
            "fields": all_field_info,
            "target_fields": [format_field_info(f) for f in found_targets]
        }
        
        with open(output_file, 'w') as f:
            json.dump(schema_data, f, indent=2)
        
        print(f"💾 Full schema saved to: {output_file}")
        
        # Print field mapping format for easy copy-paste
        if found_targets:
            print("\n📋 Field Mappings for field_mappings.py:")
            print("-" * 40)
            for field in found_targets:
                print(f'"{field.get("name")}": "{field.get("id")}",  # {field.get("type")} field')
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error connecting to Airtable API: {e}")
        print()
        print("💡 Troubleshooting tips:")
        print("   1. Check your internet connection")
        print("   2. Verify the API key is valid")
        print("   3. Ensure the base ID and table ID are correct")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing API response: {e}")
        print("   The API returned invalid JSON data")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if "401" in str(e):
            print()
            print("💡 Authentication failed. Please check:")
            print("   1. Your API key is valid and not expired")
            print("   2. The API key has access to the specified base")
        elif "404" in str(e):
            print()
            print("💡 Resource not found. Please verify:")
            print(f"   1. Base ID '{base_id}' exists")
            print(f"   2. Table ID '{table_id}' exists in the base")
        sys.exit(1)


if __name__ == "__main__":
    discover_schema()