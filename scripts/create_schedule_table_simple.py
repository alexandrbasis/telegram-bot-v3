#!/usr/bin/env python3
"""
Simplified script to create Schedule table fields manually in existing Airtable base.
Since Airtable API has limitations for creating tables via metadata API,
we'll create a simpler version that adds fields to an existing table.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appRp7Vby2JMzN0mC")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def check_existing_tables() -> Optional[str]:
    """
    Check if Schedule table already exists and return its ID.
    """
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"

    print("Checking existing tables...")
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        for table in data.get('tables', []):
            if table['name'] == 'Schedule':
                print(f"✅ Found existing Schedule table: {table['id']}")
                return table['id']
        print("ℹ️ Schedule table not found. Please create it manually in Airtable UI first.")
        return None
    else:
        print(f"❌ Failed to fetch tables: {response.status_code}")
        return None

def add_sample_events_basic(table_name: str = "Schedule") -> None:
    """
    Add sample events to the Schedule table using basic API.
    We'll use a simplified field structure that we know works.
    """
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"

    # Simplified sample events
    sample_events = [
        {
            "fields": {
                "EventTitle": "Регистрация участников",
                "EventDate": "2025-11-13",
                "StartTime": "17:00",
                "EndTime": "19:00",
                "Description": "Регистрация и размещение кандидатов",
                "Location": "Главный холл",
                "Audience": "Candidates",
                "EventType": "Activity",
                "DayTag": "Day 0 - Thursday",
                "Order": 1,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Ужин",
                "EventDate": "2025-11-13",
                "StartTime": "19:00",
                "EndTime": "20:00",
                "Description": "Приветственный ужин для всех участников",
                "Location": "Столовая",
                "Audience": "All",
                "EventType": "Meal",
                "DayTag": "Day 0 - Thursday",
                "Order": 2,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Вечерняя молитва",
                "EventDate": "2025-11-13",
                "StartTime": "20:30",
                "EndTime": "21:00",
                "Description": "Открывающая молитва ретрита",
                "Location": "Часовня",
                "Audience": "All",
                "EventType": "Chapel",
                "DayTag": "Day 0 - Thursday",
                "Order": 3,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Завтрак",
                "EventDate": "2025-11-14",
                "StartTime": "07:00",
                "EndTime": "08:00",
                "Description": "Завтрак для всех участников",
                "Location": "Столовая",
                "Audience": "All",
                "EventType": "Meal",
                "DayTag": "Day 1 - Friday",
                "Order": 1,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Утренняя молитва",
                "EventDate": "2025-11-14",
                "StartTime": "08:30",
                "EndTime": "09:00",
                "Description": "Утренняя молитва и размышления",
                "Location": "Часовня",
                "Audience": "All",
                "EventType": "Chapel",
                "DayTag": "Day 1 - Friday",
                "Order": 2,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Talk 1: Ideal",
                "EventDate": "2025-11-14",
                "StartTime": "09:15",
                "EndTime": "10:15",
                "Description": "First talk about the ideal Christian life",
                "Location": "Конференц-зал",
                "Audience": "Candidates",
                "EventType": "Talk",
                "DayTag": "Day 1 - Friday",
                "Order": 3,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Перерыв на кофе",
                "EventDate": "2025-11-14",
                "StartTime": "10:15",
                "EndTime": "10:30",
                "Description": "Кофе-брейк",
                "Location": "Холл",
                "Audience": "All",
                "EventType": "Break",
                "DayTag": "Day 1 - Friday",
                "Order": 4,
                "IsActive": True,
                "IsMandatory": False
            }
        },
        {
            "fields": {
                "EventTitle": "Talk 2: Grace",
                "EventDate": "2025-11-14",
                "StartTime": "10:30",
                "EndTime": "11:30",
                "Description": "Talk about God's grace",
                "Location": "Конференц-зал",
                "Audience": "Candidates",
                "EventType": "Talk",
                "DayTag": "Day 1 - Friday",
                "Order": 5,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Обед",
                "EventDate": "2025-11-14",
                "StartTime": "12:00",
                "EndTime": "13:30",
                "Description": "Обеденный перерыв",
                "Location": "Столовая",
                "Audience": "All",
                "EventType": "Meal",
                "DayTag": "Day 1 - Friday",
                "Order": 6,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "ROE Session 1",
                "EventDate": "2025-11-14",
                "StartTime": "14:00",
                "EndTime": "15:00",
                "Description": "First ROE sharing session",
                "Location": "Конференц-зал",
                "Audience": "Candidates",
                "EventType": "ROE",
                "DayTag": "Day 1 - Friday",
                "Order": 7,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "De Colores",
                "EventDate": "2025-11-16",
                "StartTime": "16:00",
                "EndTime": "17:00",
                "Description": "Праздничное закрытие ретрита «De Colores»",
                "Location": "Главный зал",
                "Audience": "All",
                "EventType": "Celebration",
                "DayTag": "Day 3 - Sunday",
                "Order": 10,
                "IsActive": True,
                "IsMandatory": True
            }
        }
    ]

    print(f"\n📝 Adding sample events to Schedule table...")

    success_count = 0
    for event in sample_events:
        response = requests.post(url, headers=HEADERS, json=event)
        if response.status_code == 200:
            record = response.json()
            print(f"   ✅ Added: {event['fields']['EventTitle']}")
            success_count += 1
        else:
            print(f"   ❌ Failed to add {event['fields']['EventTitle']}: {response.text}")
        time.sleep(0.2)  # Rate limiting

    print(f"\n📊 Summary: {success_count}/{len(sample_events)} events added successfully")

def generate_field_mappings() -> Dict[str, Any]:
    """
    Generate field mappings structure for documentation.
    """
    # Since we can't get actual field IDs without creating the table via API,
    # we'll create a template that can be filled in after manual creation
    field_mappings = {
        "table_name": "Schedule",
        "table_id": "tbl[TO_BE_FILLED]",
        "primary_field": "EventTitle",
        "fields": {
            "EventTitle": {
                "type": "singleLineText",
                "id": "fld[TO_BE_FILLED]",
                "description": "Title of the event (primary field)"
            },
            "EventDate": {
                "type": "date",
                "id": "fld[TO_BE_FILLED]",
                "description": "Date of the event",
                "format": "D/M/YYYY"
            },
            "StartTime": {
                "type": "singleLineText",
                "id": "fld[TO_BE_FILLED]",
                "description": "Start time in 24-hour format (HH:MM)"
            },
            "EndTime": {
                "type": "singleLineText",
                "id": "fld[TO_BE_FILLED]",
                "description": "End time in 24-hour format (HH:MM)"
            },
            "Description": {
                "type": "multilineText",
                "id": "fld[TO_BE_FILLED]",
                "description": "Detailed description of the event"
            },
            "Location": {
                "type": "singleLineText",
                "id": "fld[TO_BE_FILLED]",
                "description": "Location or room where the event takes place"
            },
            "Audience": {
                "type": "singleSelect",
                "id": "fld[TO_BE_FILLED]",
                "description": "Target audience for the event",
                "options": ["All", "Candidates", "Team", "Clergy", "Leadership"]
            },
            "EventType": {
                "type": "singleSelect",
                "id": "fld[TO_BE_FILLED]",
                "description": "Type of event",
                "options": ["Talk", "Meal", "Chapel", "ROE", "Activity", "Break", "Prayer", "Celebration"]
            },
            "DayTag": {
                "type": "singleSelect",
                "id": "fld[TO_BE_FILLED]",
                "description": "Day identifier for the retreat",
                "options": ["Day 0 - Thursday", "Day 1 - Friday", "Day 2 - Saturday", "Day 3 - Sunday"]
            },
            "Order": {
                "type": "number",
                "id": "fld[TO_BE_FILLED]",
                "description": "Order of events within the day (for sorting)"
            },
            "Duration": {
                "type": "duration",
                "id": "fld[TO_BE_FILLED]",
                "description": "Duration of the event"
            },
            "IsActive": {
                "type": "checkbox",
                "id": "fld[TO_BE_FILLED]",
                "description": "Whether this event is active and should be displayed"
            },
            "IsMandatory": {
                "type": "checkbox",
                "id": "fld[TO_BE_FILLED]",
                "description": "Whether this event is mandatory for participants"
            },
            "ResponsibleDepartment": {
                "type": "singleSelect",
                "id": "fld[TO_BE_FILLED]",
                "description": "Department responsible for the event",
                "options": ["ROE", "Chapel", "Setup", "Palanka", "Administration", "Kitchen",
                           "Decoration", "Bell", "Refreshment", "Worship", "Media", "Clergy", "Rectorate"]
            },
            "ResponsiblePerson": {
                "type": "multipleRecordLinks",
                "id": "fld[TO_BE_FILLED]",
                "description": "Person(s) responsible for this event",
                "linkedTableId": "tbl8ivwOdAUvMi3Jy"
            },
            "Notes": {
                "type": "multilineText",
                "id": "fld[TO_BE_FILLED]",
                "description": "Additional notes or special instructions"
            }
        },
        "views": {
            "All Events": "viw[TO_BE_FILLED]",
            "Active Events": "viw[TO_BE_FILLED]",
            "By Day": "viw[TO_BE_FILLED]",
            "November 13": "viw[TO_BE_FILLED]",
            "November 14": "viw[TO_BE_FILLED]",
            "November 15": "viw[TO_BE_FILLED]",
            "November 16": "viw[TO_BE_FILLED]"
        }
    }
    return field_mappings

def save_documentation_template():
    """
    Save documentation template for manual update.
    """
    mappings = generate_field_mappings()

    output_file = "/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3/scripts/schedule_field_mappings_template.json"
    with open(output_file, 'w') as f:
        json.dump(mappings, f, indent=2)

    print(f"💾 Field mappings template saved to: {output_file}")
    print("   ⚠️ Note: Field IDs need to be filled in after manual table creation")

def print_manual_instructions():
    """
    Print instructions for manual table creation.
    """
    print("\n" + "=" * 60)
    print("📋 MANUAL SETUP INSTRUCTIONS")
    print("=" * 60)
    print("\n1️⃣ Create the Schedule table in Airtable UI:")
    print("   - Go to: https://airtable.com/appRp7Vby2JMzN0mC")
    print("   - Click '+ Add a table' or 'Create' → 'Table'")
    print("   - Name it: 'Schedule'")
    print("   - Keep the default Grid view")
    print("\n2️⃣ Add the following fields (keep this order):")
    print("   1. EventTitle (Single line text) - Primary field")
    print("   2. EventDate (Date, European format)")
    print("   3. StartTime (Single line text)")
    print("   4. EndTime (Single line text)")
    print("   5. Description (Long text)")
    print("   6. Location (Single line text)")
    print("   7. Audience (Single select: All, Candidates, Team, Clergy, Leadership)")
    print("   8. EventType (Single select: Talk, Meal, Chapel, ROE, Activity, Break, Prayer, Celebration)")
    print("   9. DayTag (Single select: Day 0 - Thursday, Day 1 - Friday, Day 2 - Saturday, Day 3 - Sunday)")
    print("   10. Order (Number)")
    print("   11. Duration (Duration)")
    print("   12. IsActive (Checkbox)")
    print("   13. IsMandatory (Checkbox)")
    print("   14. ResponsibleDepartment (Single select - copy from Participants table)")
    print("   15. ResponsiblePerson (Link to Participants table)")
    print("   16. Notes (Long text)")
    print("\n3️⃣ Create these views:")
    print("   - Active Events (Filter: IsActive = checked)")
    print("   - By Day (Group by: DayTag, Sort by: Order)")
    print("   - November 13 (Filter: EventDate = 13/11/2025)")
    print("   - November 14 (Filter: EventDate = 14/11/2025)")
    print("   - November 15 (Filter: EventDate = 15/11/2025)")
    print("   - November 16 (Filter: EventDate = 16/11/2025)")
    print("\n4️⃣ After creating the table:")
    print("   - Note the table ID from the URL")
    print("   - Run this script again with the table name to add sample data")
    print("   - Update the field IDs in the documentation")

def main():
    """
    Main execution function.
    """
    print("🚀 Airtable Schedule Table Setup Helper")
    print("=" * 50)

    if not API_KEY:
        print("❌ Error: AIRTABLE_API_KEY not found in environment")
        sys.exit(1)

    if not BASE_ID:
        print("❌ Error: AIRTABLE_BASE_ID not found in environment")
        sys.exit(1)

    print(f"📊 Base ID: {BASE_ID}")
    print()

    # Check if table exists
    table_id = check_existing_tables()

    if table_id:
        # Table exists, ask if user wants to add sample data
        response = input("\n❓ Schedule table exists. Add sample events? (y/n): ")
        if response.lower() == 'y':
            add_sample_events_basic()
    else:
        # Table doesn't exist, show manual instructions
        print_manual_instructions()
        save_documentation_template()

        print("\n" + "=" * 60)
        print("✅ Next steps:")
        print("1. Create the table manually following the instructions above")
        print("2. Run this script again to add sample data")
        print("3. Update documentation with actual field IDs")

if __name__ == "__main__":
    main()