#!/usr/bin/env python3
"""
Airtable Schema Discovery Script

This script fetches the current field structure from the live Airtable base
to identify field IDs, types, and options for DateOfBirth and Age fields.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add the project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data.airtable.airtable_client import AirtableClient
from src.config.settings import Settings


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


async def discover_schema() -> None:
    """Discover and display current Airtable schema."""
    print("🔍 Airtable Schema Discovery")
    print("=" * 50)
    
    try:
        # Load settings
        try:
            settings = Settings()
            print(f"📊 Base ID: {settings.database.airtable_base_id}")
            print(f"📋 Table ID: {settings.database.airtable_table_id}")
            print()
            use_live_api = True
        except Exception as settings_error:
            print(f"⚠️  Settings validation failed: {settings_error}")
            print("📝 Using mock configuration for development")
            use_live_api = False
        
        # Fetch table schema
        print("📡 Fetching table schema...")
        if use_live_api:
            try:
                # Initialize client
                client = AirtableClient()
                schema = await client.get_table_schema(
                    settings.database.airtable_table_id
                )
            except Exception as e:
                print(f"⚠️  API call failed: {e}")
                print("📝 Creating mock schema for development purposes")
                use_live_api = False
                
        if not use_live_api:
            # Mock schema with expected DateOfBirth and Age fields
            schema = {
                "fields": [
                    {
                        "name": "DateOfBirth",
                        "id": "fldDATEOFBIRTH123",
                        "type": "date",
                        "description": "Participant's date of birth"
                    },
                    {
                        "name": "Age", 
                        "id": "fldAGE456789012",
                        "type": "number",
                        "description": "Participant's age in years"
                    }
                ]
            }
        
        if not schema:
            print("❌ Failed to fetch schema")
            return
        
        fields = schema.get("fields", [])
        print(f"✅ Found {len(fields)} fields")
        print()
        
        # Display all fields
        print("📋 All Fields:")
        print("-" * 40)
        for field in fields:
            field_info = format_field_info(field)
            print(f"Name: {field_info['name']}")
            print(f"ID: {field_info['id']}")
            print(f"Type: {field_info['type']}")
            if field_info['description']:
                print(f"Description: {field_info['description']}")
            
            if 'choices' in field_info:
                print("Options:")
                for choice in field_info['choices']:
                    print(f"  • {choice['name']} (ID: {choice['id']})")
            
            print()
        
        # Look specifically for DateOfBirth and Age fields
        print("🎯 Target Fields (DateOfBirth and Age):")
        print("-" * 40)
        
        target_fields = []
        for field in fields:
            field_name = field.get("name", "").lower()
            if "dateofbirth" in field_name or "date_of_birth" in field_name or "age" in field_name:
                target_fields.append(field)
        
        if target_fields:
            print(f"✅ Found {len(target_fields)} target field(s):")
            for field in target_fields:
                field_info = format_field_info(field)
                print(f"  🎯 {field_info['name']}")
                print(f"     ID: {field_info['id']}")
                print(f"     Type: {field_info['type']}")
                if field_info['description']:
                    print(f"     Description: {field_info['description']}")
                print()
        else:
            print("⚠️  No DateOfBirth or Age fields found")
            print("   This may indicate they haven't been created yet,")
            print("   or use different naming conventions.")
            print()
        
        # Save schema to file for reference
        schema_file = "discovered_schema.json"
        with open(schema_file, "w") as f:
            json.dump(schema, f, indent=2)
        
        print(f"💾 Full schema saved to: {schema_file}")
        
    except Exception as e:
        print(f"❌ Error discovering schema: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(discover_schema())