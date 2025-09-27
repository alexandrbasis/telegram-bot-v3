#!/usr/bin/env python3
"""
Fetch Schedule table metadata from Airtable to get actual field IDs and view IDs.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appRp7Vby2JMzN0mC")

def fetch_table_metadata():
    """Fetch metadata for all tables in the base."""
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching metadata: {response.status_code}")
        print(response.text)
        return None

def extract_schedule_info(data):
    """Extract Schedule table information."""
    for table in data.get('tables', []):
        if table['name'] == 'Schedule':
            print(f"✅ Found Schedule table!")
            print(f"Table ID: {table['id']}")
            print(f"Primary Field ID: {table.get('primaryFieldId', 'N/A')}")
            print("\n📋 Fields:")

            field_info = {}
            for field in table.get('fields', []):
                field_info[field['name']] = {
                    'id': field['id'],
                    'type': field['type'],
                    'options': field.get('options', {})
                }
                print(f"  {field['name']}: {field['id']} ({field['type']})")

                # Print select options if available
                if field['type'] == 'singleSelect' and 'choices' in field.get('options', {}):
                    print(f"    Options:")
                    for choice in field['options']['choices']:
                        print(f"      - {choice['name']}: {choice['id']}")

            print("\n👁️ Views:")
            for view in table.get('views', []):
                print(f"  {view['name']}: {view['id']} ({view['type']})")

            # Save to file
            output_file = "schedule_metadata.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'table_id': table['id'],
                    'table_name': table['name'],
                    'primary_field_id': table.get('primaryFieldId'),
                    'fields': field_info,
                    'views': {v['name']: v['id'] for v in table.get('views', [])}
                }, f, indent=2)

            print(f"\n💾 Metadata saved to {output_file}")
            return table

    print("❌ Schedule table not found")
    return None

def main():
    print("🔍 Fetching Airtable metadata...")
    print(f"Base ID: {BASE_ID}\n")

    data = fetch_table_metadata()
    if data:
        schedule_table = extract_schedule_info(data)
        if schedule_table:
            print("\n✨ Successfully retrieved Schedule table metadata!")
    else:
        print("❌ Failed to fetch metadata")

if __name__ == "__main__":
    main()