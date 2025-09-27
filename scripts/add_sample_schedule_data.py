#!/usr/bin/env python3
"""
Add sample schedule data to the Schedule table.
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appRp7Vby2JMzN0mC")
TABLE_ID = os.getenv("AIRTABLE_SCHEDULE_TABLE_ID", "tblsxihPaZebzyBS2")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def add_sample_events():
    """Add sample events to the Schedule table."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

    # Sample events with actual field names and option values
    sample_events = [
        {
            "fields": {
                "EventTitle": "Регистрация участников",
                "EventDate": "2025-11-13",
                "StartTime": "17:00",
                "EndTime": "19:00",
                "Description": "Регистрация и размещение кандидатов в комнатах",
                "Location": "Главный холл",
                "Audience": "Candidates",
                "EventType": "Activity",
                "DayTag": "Day 0",
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
                "DayTag": "Day 0",
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
                "DayTag": "Day 0",
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
                "DayTag": "Day 1",
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
                "DayTag": "Day 1",
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
                "DayTag": "Day 1",
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
                "DayTag": "Day 1",
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
                "DayTag": "Day 1",
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
                "DayTag": "Day 1",
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
                "DayTag": "Day 1",
                "Order": 7,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Talk 3: Piety",
                "EventDate": "2025-11-15",
                "StartTime": "09:00",
                "EndTime": "10:00",
                "Description": "Talk about piety and devotion",
                "Location": "Конференц-зал",
                "Audience": "Candidates",
                "EventType": "Talk",
                "DayTag": "Day 2",
                "Order": 1,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "ROE Session 2",
                "EventDate": "2025-11-15",
                "StartTime": "11:00",
                "EndTime": "12:00",
                "Description": "Second ROE sharing session",
                "Location": "Конференц-зал",
                "Audience": "Candidates",
                "EventType": "ROE",
                "DayTag": "Day 2",
                "Order": 2,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Праздничный ужин",
                "EventDate": "2025-11-15",
                "StartTime": "18:00",
                "EndTime": "20:00",
                "Description": "Праздничный ужин с развлечениями",
                "Location": "Главный зал",
                "Audience": "All",
                "EventType": "Celebration",
                "DayTag": "Day 2",
                "Order": 3,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Утренняя молитва",
                "EventDate": "2025-11-16",
                "StartTime": "08:00",
                "EndTime": "08:30",
                "Description": "Заключительная утренняя молитва",
                "Location": "Часовня",
                "Audience": "All",
                "EventType": "Chapel",
                "DayTag": "Day 3",
                "Order": 1,
                "IsActive": True,
                "IsMandatory": True
            }
        },
        {
            "fields": {
                "EventTitle": "Talk 4: Study",
                "EventDate": "2025-11-16",
                "StartTime": "09:00",
                "EndTime": "10:00",
                "Description": "Final talk about continuous study",
                "Location": "Конференц-зал",
                "Audience": "Candidates",
                "EventType": "Talk",
                "DayTag": "Day 3",
                "Order": 2,
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
                "DayTag": "Day 3",
                "Order": 10,
                "IsActive": True,
                "IsMandatory": True
            }
        }
    ]

    print(f"📝 Adding {len(sample_events)} sample events to Schedule table...")

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
    return success_count

def main():
    print("🚀 Adding Sample Schedule Data")
    print("=" * 50)
    print(f"Base ID: {BASE_ID}")
    print(f"Table ID: {TABLE_ID}")
    print()

    if not API_KEY:
        print("❌ Error: AIRTABLE_API_KEY not found in environment")
        return

    success_count = add_sample_events()

    if success_count > 0:
        print(f"\n✨ Successfully added {success_count} sample events!")
        print("\n📌 Next Steps:")
        print("   1. Check the Schedule table in Airtable to verify the data")
        print("   2. Create additional views if needed (By Day, November 13-16, etc.)")
        print("   3. Test the bot integration with the schedule data")
    else:
        print("\n❌ No events were added. Check the error messages above.")

if __name__ == "__main__":
    main()