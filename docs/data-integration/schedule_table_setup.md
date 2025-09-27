# Schedule Table Setup Guide

## Overview
This guide walks through the complete setup of the Schedule table in Airtable for the Tres Dias retreat scheduling system (November 13-16, 2025).

## Table of Contents
1. [Manual Table Creation](#manual-table-creation)
2. [Field Configuration](#field-configuration)
3. [View Creation](#view-creation)
4. [Sample Data Import](#sample-data-import)
5. [Configuration Updates](#configuration-updates)
6. [Validation Steps](#validation-steps)

## Manual Table Creation

### Step 1: Access Your Airtable Base
1. Navigate to: https://airtable.com/appRp7Vby2JMzN0mC
2. Click the "+" button or "Add a table" → "Start from scratch"
3. Name the table: **Schedule**
4. Keep the default Grid view

### Step 2: Note the Table ID
After creation, the URL will change to include the table ID:
```
https://airtable.com/appRp7Vby2JMzN0mC/tblXXXXXXXXXXXXXX
                                          ^^^^^^^^^^^^^^^^
                                          This is your table ID
```
Save this ID - you'll need it for configuration.

## Field Configuration

Create the following fields in **exact order** (the first field "EventTitle" will be the primary field):

### Core Event Fields

| # | Field Name | Field Type | Configuration | Required |
|---|------------|------------|---------------|----------|
| 1 | **EventTitle** | Single line text | Primary field | Yes |
| 2 | **EventDate** | Date | Format: European (D/M/YYYY) | Yes |
| 3 | **StartTime** | Single line text | Format: HH:MM | Yes |
| 4 | **EndTime** | Single line text | Format: HH:MM | No |
| 5 | **Description** | Long text | Rich text formatting: Off | No |
| 6 | **Location** | Single line text | - | No |

### Classification Fields

| # | Field Name | Field Type | Options | Required |
|---|------------|------------|---------|----------|
| 7 | **Audience** | Single select | All, Candidates, Team, Clergy, Leadership | Yes |
| 8 | **EventType** | Single select | Talk, Meal, Chapel, ROE, Activity, Break, Prayer, Celebration | Yes |
| 9 | **DayTag** | Single select | Day 0 - Thursday, Day 1 - Friday, Day 2 - Saturday, Day 3 - Sunday | Yes |

### Organization Fields

| # | Field Name | Field Type | Configuration | Required |
|---|------------|------------|---------------|----------|
| 10 | **Order** | Number | Integer, no decimals | Yes |
| 11 | **Duration** | Duration | Format: h:mm | No |
| 12 | **IsActive** | Checkbox | Default: checked | No |
| 13 | **IsMandatory** | Checkbox | Default: unchecked | No |

### Responsibility Fields

| # | Field Name | Field Type | Configuration | Required |
|---|------------|------------|---------------|----------|
| 14 | **ResponsibleDepartment** | Single select | Copy options from Participants.Department field | No |
| 15 | **ResponsiblePerson** | Link to another record | Link to: Participants table | No |
| 16 | **Notes** | Long text | Rich text formatting: Off | No |

## View Creation

Create the following views for easy schedule management:

### 1. Active Events View
- **Name**: Active Events
- **Type**: Grid
- **Filter**: Where `IsActive` is ✓ (checked)
- **Sort**:
  1. EventDate (ascending)
  2. Order (ascending)

### 2. By Day View
- **Name**: By Day
- **Type**: Grid
- **Group by**: DayTag
- **Sort within groups**: Order (ascending)
- **Filter**: Where `IsActive` is ✓ (checked)

### 3. Daily Views (November 13-16)
Create four views, one for each day:

#### November 13 View
- **Name**: November 13
- **Filter**: Where `EventDate` is `13/11/2025`
- **Sort**: Order (ascending)

#### November 14 View
- **Name**: November 14
- **Filter**: Where `EventDate` is `14/11/2025`
- **Sort**: Order (ascending)

#### November 15 View
- **Name**: November 15
- **Filter**: Where `EventDate` is `15/11/2025`
- **Sort**: Order (ascending)

#### November 16 View
- **Name**: November 16
- **Filter**: Where `EventDate` is `16/11/2025`
- **Sort**: Order (ascending)

### 4. Mandatory Events View
- **Name**: Mandatory Events
- **Filter**: Where `IsMandatory` is ✓ (checked)
- **Sort**:
  1. EventDate (ascending)
  2. Order (ascending)

## Sample Data Import

### Option 1: Using the Script
After creating the table, run the helper script to add sample data:

```bash
cd "/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3"
./venv/bin/python scripts/create_schedule_table_simple.py
```

When prompted, enter 'y' to add sample events.

### Option 2: Manual Entry
Add these sample events manually to test the setup:

| EventTitle | EventDate | StartTime | EndTime | DayTag | Order | Audience | EventType |
|------------|-----------|-----------|---------|--------|-------|----------|-----------|
| Регистрация участников | 13/11/2025 | 17:00 | 19:00 | Day 0 - Thursday | 1 | Candidates | Activity |
| Ужин | 13/11/2025 | 19:00 | 20:00 | Day 0 - Thursday | 2 | All | Meal |
| Вечерняя молитва | 13/11/2025 | 20:30 | 21:00 | Day 0 - Thursday | 3 | All | Chapel |
| Завтрак | 14/11/2025 | 07:00 | 08:00 | Day 1 - Friday | 1 | All | Meal |
| Talk 1: Ideal | 14/11/2025 | 09:15 | 10:15 | Day 1 - Friday | 3 | Candidates | Talk |

## Configuration Updates

### 1. Update Environment Variables
Add to your `.env` file:
```bash
# Schedule table configuration
AIRTABLE_SCHEDULE_TABLE_NAME=Schedule
AIRTABLE_SCHEDULE_TABLE_ID=tblXXXXXXXXXXXXXX  # Replace with actual ID
```

### 2. Get Field IDs
After creating all fields, you need to get their IDs. Use this API call:

```bash
curl -X GET "https://api.airtable.com/v0/meta/bases/appRp7Vby2JMzN0mC/tables" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.tables[] | select(.name=="Schedule")'
```

### 3. Update Field Mappings
Edit `/src/config/field_mappings/schedule.py` and replace all `fld[TO_BE_FILLED]` with actual field IDs from the API response.

### 4. Update Documentation
Update `/docs/data-integration/airtable_database_structure.md`:
- Replace `tbl[TO_BE_FILLED_AFTER_CREATION]` with actual table ID
- Replace all `fld[TO_BE_FILLED]` with actual field IDs
- Update view IDs once created

## Validation Steps

### 1. Test API Connection
Run this Python script to verify the setup:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_ID = os.getenv("AIRTABLE_SCHEDULE_TABLE_ID")
API_KEY = os.getenv("AIRTABLE_API_KEY")

url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("✅ Schedule table is accessible!")
    records = response.json().get('records', [])
    print(f"   Found {len(records)} records")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
```

### 2. Verify Views
Check that all views are working:
- Each daily view should show only events for that specific date
- Active Events view should hide any unchecked IsActive records
- By Day view should group events properly

### 3. Test Filtering
Create a test event with `IsActive` unchecked and verify it doesn't appear in Active Events view.

## Troubleshooting

### Common Issues

1. **"Invalid table ID" error**
   - Ensure you copied the full table ID from the URL
   - Check that the ID starts with "tbl"

2. **"Field not found" error**
   - Verify field names match exactly (case-sensitive)
   - Check that all fields were created in Airtable

3. **Date format issues**
   - Ensure dates are in D/M/YYYY format
   - Use forward slashes, not dashes

4. **Time format issues**
   - Use 24-hour format (00:00 to 23:59)
   - Include leading zeros (09:00, not 9:00)

### Getting Help

If you encounter issues:
1. Check the Airtable API documentation: https://airtable.com/developers/web/api/introduction
2. Review the error messages in bot logs
3. Verify all field IDs are correctly mapped

## Next Steps

After completing the setup:
1. ✅ Table created in Airtable
2. ✅ All fields configured
3. ✅ Views created
4. ✅ Sample data imported
5. ✅ Environment variables updated
6. ✅ Field mappings updated
7. ✅ Documentation updated

You're now ready to implement the Schedule feature in the bot! The table is configured to support:
- Date-based filtering (Nov 13-16, 2025)
- Active/inactive event management
- Day-based grouping
- Mandatory event highlighting
- Department and person responsibility tracking

## API Integration Notes

When implementing the bot integration:
- Cache responses for 10 minutes (business requirement)
- Filter by `IsActive = true` by default
- Sort by `EventDate` then `Order`
- Handle empty schedule days gracefully
- Support both Russian and English content
- Use 24-hour time format consistently