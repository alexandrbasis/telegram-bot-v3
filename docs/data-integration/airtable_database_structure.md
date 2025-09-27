# Airtable Database Structure Documentation

## Last Updated
- **Date**: September 27, 2025
- **Version**: 3.2.0
- **Changes**: Added Schedule table schema for retreat event management (November 13-16, 2025)

## Database Information
- **Base ID**: `appRp7Vby2JMzN0mC`
- **Base Type**: Airtable
- **Environment**: Development

## Configuration (Environment Variables)

### Base Configuration
- `AIRTABLE_API_KEY`: Your Airtable personal access token
- `AIRTABLE_BASE_ID`: appRp7Vby2JMzN0mC

### Table-Specific Configuration
```bash
# Participants table (default/primary)
AIRTABLE_TABLE_NAME=Participants
AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy

# BibleReaders table
AIRTABLE_BIBLE_READERS_TABLE_NAME=BibleReaders
AIRTABLE_BIBLE_READERS_TABLE_ID=tblGEnSfpPOuPLXcm

# ROE table
AIRTABLE_ROE_TABLE_NAME=ROE
AIRTABLE_ROE_TABLE_ID=tbl0j8bcgkV3lVAdc

# Bot Access Requests table
AIRTABLE_ACCESS_REQUESTS_TABLE_NAME=BotAccessRequests
AIRTABLE_ACCESS_REQUESTS_TABLE_ID=tblQWWEcHx9sfhsgN

# AuthorizedUsers table
AIRTABLE_AUTHORIZED_USERS_TABLE_NAME=AuthorizedUsers
AIRTABLE_AUTHORIZED_USERS_TABLE_ID=tblQ5i7EwSZrVYwT6A

# Schedule table
AIRTABLE_SCHEDULE_TABLE_NAME=Schedule
AIRTABLE_SCHEDULE_TABLE_ID=tblsxihPaZebzyBS2
```

## Tables Overview

### 1. Participants Table
**Table ID**: `tbl8ivwOdAUvMi3Jy`
**Primary Field**: `FullNameRU` (fldOcpA3JW5MRmR6R)

### 2. ROE Table
**Table ID**: `tbl0j8bcgkV3lVAdc`
**Primary Field**: `RoeTopic` (fldSniGvfWpmkpc1r)

### 3. BibleReaders Table
**Table ID**: `tblGEnSfpPOuPLXcm`
**Primary Field**: `Where` (fldsSNHSXJBhewCxq)

### 4. BotAccessRequests Table
**Table ID**: `tblQWWEcHx9sfhsgN`
**Primary Field**: `TelegramUserId` (fldeiF3gxg4fZMirc)

### 5. AuthorizedUsers Table
**Table ID**: `tblQ5i7EwSZrVYwT6A`
**Primary Field**: `TelegramUserId` (fldMwpp0K6deDnZwQ)

### 6. Schedule Table
**Table ID**: `tblsxihPaZebzyBS2`
**Primary Field**: `EventTitle` (fldwJzYx5l5NMnBET)

#### Purpose
- Serves as the source of truth for Telegram bot authorization assignments
- Enables dynamic authorization updates without restarting the bot
- Provides audit context for access control changes

#### Core Fields (current schema)
- `TelegramUserId` (Number, primary, required) – Unique Telegram user identifier
- `Status` (Single select) – Operational status for the user (e.g., `Active`, `Suspended`, `Revoked`)
- `AccessLevel` (Single select) – Role granted to the user (`VIEWER`, `COORDINATOR`, `ADMIN`)

#### Recommended Views
- **Active Users** – Filters `Status = Active`; consumed by authorization sync job
- **Suspended Users** – Tracks suspended/blocked accounts for review

## Field Specifications

### Text Fields

#### FullNameRU
- **Field ID**: `fldOcpA3JW5MRmR6R`
- **Type**: `singleLineText`
- **Purpose**: Primary field - Full name in Russian
- **Required**: Yes (Primary field)
- **Example**: "Александр Басис"

#### FullNameEN
- **Field ID**: `fldrFVukSmk0i9sqj`
- **Type**: `singleLineText`
- **Purpose**: Full name in English
- **Required**: No
- **Example**: Not provided in sample data

#### Church
- **Field ID**: `fld4CXL9InW0ogAQh`
- **Type**: `singleLineText`
- **Purpose**: Church affiliation
- **Required**: No
- **Example**: "Грейс"

#### CountryAndCity
- **Field ID**: `fldJ7dFRzx7bR9U6g`
- **Type**: `singleLineText`
- **Purpose**: Location information
- **Required**: No
- **Example**: "21"

#### SubmittedBy
- **Field ID**: `flduADiTl7jpiy8OH`
- **Type**: `singleLineText`
- **Purpose**: Person who submitted the record
- **Required**: No
- **Example**: "12"

#### ContactInformation
- **Field ID**: `fldSy0Hbwl49VtZvf`
- **Type**: `singleLineText`
- **Purpose**: Contact details
- **Required**: No
- **Example**: Not provided in sample data

#### ChurchLeader
- **Field ID**: `fldbQr0R6nEtg1nXM`
- **Type**: `singleLineText`
- **Purpose**: Church leader name or reference
- **Required**: No
- **Example**: Not provided in sample data

#### TableName
- **Field ID**: `fldwIopXniSHk94v9`
- **Type**: `singleLineText`
- **Purpose**: Table assignment for events
- **Required**: No
- **Example**: Not provided in sample data

### Multi-line Text Fields

#### Notes
- **Field ID**: `fldL4wmlV9de1kKa1`
- **Type**: `multilineText`
- **Purpose**: Additional notes or comments about the participant
- **Required**: No
- **Example**: Not provided in sample data

### Single Select Fields

#### Status (BotAccessRequests)
- **Field ID**: `fldcuRa8qeUDKY3hN`
- **Type**: `singleSelect`
- **Purpose**: Tracks request state
- **Required**: Yes
- **Options**:
  - `Pending` - Color: `yellowLight2` - ID: `sel2z5NxHBR4zPIbY`
  - `Approved` - Color: `greenLight2` - ID: `selw76sykZ8WNV5nP`
  - `Denied` - Color: `redLight2` - ID: `selterUXC4cXAuyWI`

#### AccessLevel (BotAccessRequests)
- **Field ID**: `fldRBCoHwrJ87hdjr`
- **Type**: `singleSelect`
- **Purpose**: Defines access tier granted after approval
- **Required**: Yes
- **Options**:
  - `VIEWER` - Color: `tealLight2` - ID: `seldUb45waf3xvSOH`
  - `COORDINATOR` - Color: `cyanLight2` - ID: `selhBl3PB3h6NQ9TQ`
  - `ADMIN` - Color: `blueLight2` - ID: `selUPw7UMErtc7O9n`


#### Gender
- **Field ID**: `fldOAGXoU0DqqFRmB`
- **Type**: `singleSelect`
- **Required**: No
- **Options**:
  - `M` (Male) - Color: `cyanLight2` - ID: `selZClW1ZQ0574g1o`
  - `F` (Female) - Color: `redLight2` - ID: `sellCtTlpLKDRs7Uw`

#### Size
- **Field ID**: `fldZyNgaaa1snp6s7`
- **Type**: `singleSelect`
- **Purpose**: Clothing size
- **Required**: No
- **Options**:
  - `XS` - Color: `blueLight2` - ID: `selNuViDUBjuth8lP`
  - `S` - Color: `cyanLight2` - ID: `selKoQLAR5xH9jQvg`
  - `M` - Color: `tealLight2` - ID: `sel0Ci7MTtsPBtPi0`
  - `L` - Color: `greenLight2` - ID: `sel5Zd5JF5WD8Y5ab`
  - `XL` - Color: `yellowLight2` - ID: `selmHioiHTrhhmpOO`
  - `XXL` - Color: `orangeLight2` - ID: `selPsyMnT0h7wyOly`
  - `3XL` - Color: `redLight2` - ID: `sel1NSFzQbfWVUEuS`

#### Role
- **Field ID**: `fldetbIGOkKFK0hYq`
- **Type**: `singleSelect`
- **Purpose**: Participant role/status
- **Required**: No
- **Options**:
  - `CANDIDATE` - Color: `yellowLight2` - ID: `seleMsONuukNzmB2M`
  - `TEAM` - Color: `redLight2` - ID: `selycaljF0Qnq0tdD`

#### Department
- **Field ID**: `fldIh0eyPspgr1TWk`
- **Type**: `singleSelect`
- **Purpose**: Department assignment
- **Required**: No
- **Options**:
  - `ROE` - Color: `blueLight2` - ID: `selfaZRN9JukJMcZ5`
  - `Chapel` - Color: `cyanLight2` - ID: `sel6IPXCbLoWR5Ugd`
  - `Setup` - Color: `tealLight2` - ID: `selAtROQz5C6CMZMk`
  - `Palanka` - Color: `greenLight2` - ID: `sel1E7vNA7wgVDFLl`
  - `Administration` - Color: `yellowLight2` - ID: `selJBiWzoJiFmMlL6`
  - `Kitchen` - Color: `orangeLight2` - ID: `selBmfVPB1Jr6jTtQ`
  - `Decoration` - Color: `redLight2` - ID: `selrCvE3jP1Lxg5z5`
  - `Bell` - Color: `pinkLight2` - ID: `selX89NOZuBVjYD07`
  - `Refreshment` - Color: `purpleLight2` - ID: `selanq3i2UJWrsmkj`
  - `Worship` - Color: `grayLight2` - ID: `selCKwn2YGIYqQRs8`
  - `Media` - Color: `blueLight2` - ID: `selq5zRZtZ6LXMhN2`
  - `Clergy` - Color: `cyanLight2` - ID: `selksIu0oBzHq9Blm`
  - `Rectorate` - Color: `tealLight2` - ID: `seliF8wxKVKpY2za3`

#### PaymentStatus
- **Field ID**: `fldQzc7m7eO0JzRZf`
- **Type**: `singleSelect`
- **Purpose**: Payment tracking
- **Required**: No
- **Options**:
  - `Paid` - Color: `greenLight2` - ID: `sel4ZcXLVs973Gizi`
  - `Partial` - Color: `yellowLight2` - ID: `sel1WOFITijjZqaPQ`
  - `Unpaid` - Color: `redLight2` - ID: `selFWmvtAQC7EEB72`

### Number Fields

#### TelegramUserId
- **Field ID**: `fldeiF3gxg4fZMirc`
- **Type**: `number` (precision 0)
- **Purpose**: Stores Telegram user ID for lookup and uniqueness
- **Required**: Yes (primary field in BotAccessRequests table)
- **Example**: `5212991086`

#### PaymentAmount
- **Field ID**: `fldyP24ZbeGD8nnaZ`
- **Type**: `number`
- **Purpose**: Amount paid
- **Required**: No
- **Precision**: 0 (integers only)
- **Example**: 0

#### Age
- **Field ID**: `fldZPh65PIekEbgvs`
- **Type**: `number`
- **Purpose**: Participant's age in years
- **Required**: No
- **Precision**: 1 (supports one decimal place)
- **Constraints**: Must be >= 0 and <= 120
- **Example**: 35

#### Floor
- **Field ID**: `fldlzG1sVg01hsy2g`
- **Type**: `number`
- **Purpose**: Floor number for accommodation assignment
- **Required**: No
- **Precision**: 0 (integers only)
- **Example**: Not provided in sample data

#### RoomNumber
- **Field ID**: `fldJTPjo8AHQaADVu`
- **Type**: `number`
- **Purpose**: Room number for accommodation assignment
- **Required**: No
- **Precision**: 0 (integers only)
- **Example**: Not provided in sample data

### Checkbox Fields

#### IsDepartmentChief
- **Field ID**: `fldWAay3tQiXN9888`
- **Type**: `checkbox`
- **Purpose**: Indicates if the participant is a department chief/leader
- **Required**: No
- **Values**: `true` (checked) or `false` (unchecked)
- **Default**: `false`
- **Example**: `true` for department heads

### Relationship Fields

#### BibleReaders
- **Field ID**: `fldaiLErSw51C4pFN`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links participant to Bible reading sessions they're involved in
- **Required**: No
- **Links To**: BibleReaders table (tblGEnSfpPOuPLXcm)
- **Example**: Array of record IDs from BibleReaders table

#### Roe
- **Field ID**: `fldl5TjaTqhdzbdLu`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links participant as a primary presenter for ROE sessions
- **Required**: No
- **Links To**: ROE table (tbl0j8bcgkV3lVAdc)
- **Example**: Array of record IDs from ROE table where participant serves as the main presenter

#### RoeAssistant
- **Field ID**: `fldYCDajNakfOhdZ8`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links participant as an assistant presenter for ROE sessions
- **Required**: No
- **Links To**: ROE table (tbl0j8bcgkV3lVAdc)
- **Example**: Array of record IDs from ROE table where participant serves as an assistant

#### ROE 2
- **Field ID**: `fld7h2Zk7pHP4E5V8`
- **Type**: `multipleRecordLinks`
- **Purpose**: Tracks ROE prayer support assignments associated with the participant
- **Required**: No
- **Links To**: ROE table (tbl0j8bcgkV3lVAdc)
- **Example**: Array of record IDs from ROE records where participant is assigned to prayer support roles

### Date Fields

#### PaymentDate
- **Field ID**: `fldylOQLqcBwkmzlh`
- **Type**: `date`
- **Purpose**: Date of payment
- **Required**: No
- **Format**: European format (D/M/YYYY)
- **Example**: Not provided in sample data

#### DateOfBirth
- **Field ID**: `fld1rN2cffxKuZh4i`
- **Type**: `date`
- **Purpose**: Participant's date of birth
- **Required**: No
- **Format**: European format (`DD/MM/YYYY`)
- **Example**: `22/09/2025`

## Views Available

### Participants Table Views

#### Export-Aligned Views (Updated 2025-09-23)
The following views have been precisely documented to support view-driven export functionality that maintains Airtable column ordering:

1. **All Data** (`viwxzBkV6XPSOlaY6`) - Grid view showing the full participant roster
2. **Тимы** (`viwhPNd0BbAxw9lr2`) - Grid view filtered for active team members
   - **Exact Export Column Order**: `FullNameRU`, `Gender`, `DateOfBirth`, `Size`, `Department`, `CountryAndCity`, `Church`, `SubmittedBy`, `FullNameEN`, `ContactInformation`
   - **Export Integration**: Used by `ParticipantExportService` for Team role and department-based exports with preserved view structure
   - **Column Order Preservation**: Export service maintains exact Airtable view ordering for participant essentials
3. **Тимы по департаментам** (`viwsTX6z1SKc0fc9c`) - Grid view grouping team members by department assignments (shares the same column layout as **Тимы**)
4. **Кандидаты** (`viwIJSnpWr61efCYB`) - Grid view filtered for candidate applications
   - **Exact Export Column Order**: `FullNameRU`, `Gender`, `DateOfBirth`, `Size`, `CountryAndCity`, `Church`, `SubmittedBy`, `FullNameEN`, `ContactInformation`
   - **Export Integration**: Used by `ParticipantExportService` for Candidate role filtering with preserved view structure
   - **Column Order Preservation**: Export service maintains concise candidate-focused column ordering
5. **По этажам** (`viwvKvD2hDiAHmEK9`) - Grid view grouped by lodging floor assignments
6. **По комнатам** (`viwOFJJ8vmhwCsiJZ`) - Grid view grouped by room assignments
7. **Размеры** (`viwcH4YV8e0bOsXDn`) - Grid view grouping by clothing size selections

#### View-Based Export Implementation (2025-09-23)
- **Repository Support**: Added `list_view_records(view: str)` method to retrieve raw Airtable view data
- **Column Order Preservation**: Export services maintain exact view column ordering including linked relationship fields
- **Header Reconstruction**: Enhanced header detection includes linked fields and preserves complete view structure
- **Filter Application**: Optional filters applied while maintaining complete view column layout
- **Export Alignment**: Ensures export output matches live Airtable base structure for direct comparability

---

## ROE Table Structure

### Table Information
- **Table ID**: `tbl0j8bcgkV3lVAdc`
- **Primary Field**: `RoeTopic` (fldSniGvfWpmkpc1r)
- **Purpose**: Manages ROE (Rollo of Encouragement) sessions and assignments

### Export Column Order
- `RoeTopic`, `Roista`, `RoeDate`, `RoeTiming`, `RoeDuration`, `Assistant`, `Prayer`

### ROE Table Fields

#### RoeTopic
- **Field ID**: `fldSniGvfWpmkpc1r`
- **Type**: `singleLineText`
- **Purpose**: Primary field - The topic or name of the ROE session
- **Required**: Yes (Primary field)
- **Example**: "Faith Journey", "Grace and Forgiveness"

#### Roista
- **Field ID**: `fldLWsfnGvJ26GwMI`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links to main Roista (presenter) from Participants table
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

#### RoeDate
- **Field ID**: `fldQHFNv68aNjuQOk`
- **Type**: `date`
- **Purpose**: Scheduled date of the ROE talk
- **Required**: No
- **Format**: European format (`D/M/YYYY`)

#### RoeTiming
- **Field ID**: `fldlobIBO2k62FaoA`
- **Type**: `singleLineText`
- **Purpose**: Human-readable time slot or schedule marker for the ROE session
- **Required**: No

#### RoeDuration
- **Field ID**: `fldpTVshWBBvv2T8X`
- **Type**: `duration`
- **Purpose**: Allocated duration for the ROE talk
- **Required**: No
- **Format**: Airtable duration format (`h:mm`)

#### Assistant
- **Field ID**: `fldtTUTsJy6oCg1sE`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links to assistant presenters from the Participants table
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

#### Prayer
- **Field ID**: `fldRSXoqNE16Inb7E`
- **Type**: `multipleRecordLinks`
- **Purpose**: Connects participants assigned to prayer support for the ROE session
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

---

## BibleReaders Table Structure

### Table Information
- **Table ID**: `tblGEnSfpPOuPLXcm`
- **Primary Field**: `Where` (fldsSNHSXJBhewCxq)
- **Purpose**: Manages Bible reading sessions and reader assignments

### Export Column Order
- `Where`, `Participants`, `When`, `Bible`

### BibleReaders Table Fields

#### Where
- **Field ID**: `fldsSNHSXJBhewCxq`
- **Type**: `singleLineText`
- **Purpose**: Primary field - Location or context of the Bible reading
- **Required**: Yes (Primary field)
- **Example**: "Morning Chapel", "Evening Service", "Room 101"

#### Participants
- **Field ID**: `fldVBlRvv295QhBlX`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links to participants assigned to read
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

#### When
- **Field ID**: `fld6WfIcctT2WZnNO`
- **Type**: `date`
- **Purpose**: Date of the Bible reading session
- **Required**: No
- **Format**: Localized Airtable date (`format = l`)
- **Example**: Locale-specific (e.g., "15.02.2025")

#### Bible
- **Field ID**: `fldi18WKRAa7iUXBQ`
- **Type**: `singleLineText`
- **Purpose**: Bible passage or reference to be read
- **Required**: No
- **Example**: "John 3:16", "Psalm 23", "1 Corinthians 13"

## API Integration Notes

### Required for Connection:
- **Token**: Personal Access Token (PAT format)
- **Base ID**: Application identifier
- **Table Name**: "Participants"

### Field Mapping for Integration:
- Use Field IDs for programmatic access
- Use Field Names for human-readable operations
- Single select fields require option IDs for writes, but accept option names
- Primary field (FullNameRU) cannot be empty

### Sample Record Structures:

#### Participants Table Record
```json
{
  "fields": {
    "FullNameRU": "string (required)",
    "FullNameEN": "string (optional)",
    "Gender": "M|F",
    "Size": "XS|S|M|L|XL|XXL|3XL",
    "Church": "string (optional)",
    "ChurchLeader": "string (optional)",
    "Role": "CANDIDATE|TEAM",
    "Department": "ROE|Chapel|Setup|...",
    "IsDepartmentChief": "boolean (optional)",
    "CountryAndCity": "string (optional)",
    "SubmittedBy": "string (optional)",
    "ContactInformation": "string (optional)",
    "PaymentStatus": "Paid|Partial|Unpaid",
    "PaymentAmount": "number (integer)",
    "PaymentDate": "YYYY-MM-DD",
    "DateOfBirth": "YYYY-MM-DD (optional)",
    "Age": "number (integer, optional, 0-120)",
    "Floor": "number (integer, optional)",
    "RoomNumber": "number (integer, optional)",
    "TableName": "string (optional)",
    "Notes": "string (multiline, optional)",
    "BibleReaders": ["recXXXXXXXXXXXXXX"],
    "Roe": ["recYYYYYYYYYYYYYY"],
    "RoeAssistant": ["recZZZZZZZZZZZZZZ"],
    "ROE 2": ["recPrayerSupportId"]
  }
}
```

#### ROE Table Record
```json
{
  "fields": {
    "RoeTopic": "string (required)",
    "Roista": ["recParticipantID1"],
    "RoeDate": "YYYY-MM-DD",
    "RoeTiming": "string (optional)",
    "RoeDuration": "HH:MM",
    "Assistant": ["recParticipantID2"],
    "Prayer": ["recParticipantID3"]
  }
}
```

#### BibleReaders Table Record
```json
{
  "fields": {
    "Where": "string (required)",
    "Participants": ["recParticipantID1", "recParticipantID2"],
    "When": "YYYY-MM-DD",
    "Bible": "string (optional)"
  }
}
```

## Implementation Considerations

1. **Validation**: Implement client-side validation for single select fields
2. **Error Handling**: Handle API rate limits (5 requests per second)
3. **Data Types**: Ensure proper type conversion for number and date fields
4. **Internationalization**: Support both Russian (primary) and English names
5. **Payment Tracking**: Implement logic to sync PaymentAmount with PaymentStatus
6. **Demographics**: DateOfBirth and Age fields provide demographic data for reporting
   - Age field should be validated to be within reasonable range (0-120)
   - DateOfBirth field uses ISO format for consistency with API standards
   - Both fields are optional and support backward compatibility with existing records
7. **Accommodation Management**: Floor and RoomNumber fields enable room assignment tracking
   - Both fields are numeric (integer) for sorting and filtering
   - Can be used for generating accommodation reports and floor plans
8. **Event Organization**: TableName field supports event seating arrangements
   - Free-text field allowing flexible table naming conventions
   - Can be used alongside Department for event logistics
9. **Leadership Tracking**: ChurchLeader field links participants to church leadership
   - Useful for group organization and communication channels
   - Can be cross-referenced with Church field for hierarchical structure
10. **Extended Information**: Notes field provides flexible multiline text storage
    - Supports rich participant information that doesn't fit standard fields
    - Useful for special requirements, dietary restrictions, or administrative notes
    - Content should be sanitized for display in various formats
11. **Department Leadership**: IsDepartmentChief checkbox identifies department leaders
    - Critical for organizational hierarchy and delegation
    - Can be used for filtering authorized users for administrative actions
    - Should be synchronized with Department field for consistency
12. **ROE Session Management**: ROE table enables Rollo assignment tracking
    - Links Roista presenters, assistants, and prayer partners to specific topics
    - Dedicated scheduling fields capture date, timing, and duration for agenda planning
    - Supports multiple Roistas per topic through relationship fields
13. **Bible Reading Coordination**: BibleReaders table manages reading assignments
    - Tracks multiple readers per session with location and timing
    - Enables scheduling and conflict detection through date fields
    - Can generate reading schedules and participant notifications
14. **Cross-Table Relationships**: Multiple relationship fields enable complex queries
    - Roe, RoeAssistant, and ROE 2 fields in Participants capture speaking and prayer assignments
    - BibleReaders field shows reading assignments per participant
    - Enables comprehensive participant activity tracking across events
15. **Participant Context**: Repository layer must enrich ROE/BibleReaders exports with participant details
    - Tables now expose relationship IDs only; downstream services should hydrate names, churches, and rooms as needed
    - Maintain caching to avoid redundant participant lookups when resolving linked records
    - Continue to respect Airtable rate limits when expanding linked record details
16. **View-Based Export Integration** (2025-09-23): Export services now align with Airtable view structure
    - **list_view_records() Method**: New repository interface method fetches raw view records preserving column order
    - **Header Reconstruction**: Export services reconstruct headers from actual view data including linked fields
    - **View-Driven Column Order**: Exports maintain exact Airtable view ordering for direct comparison with live base
    - **Optional Filtering**: Filters applied while preserving complete view column structure for consistency
    - **Linked Field Support**: Relationship fields (Roe, BibleReaders, ROE 2) included in exports with proper formatting
    - **Fall-back Header Support**: VIEW_HEADER_HINTS provide column ordering when view returns sparse data

## Bot Access Requests Table Details
- **Table ID**: tblQWWEcHx9sfhsgN
- **Primary View**: `Grid view` (viwVDrguxKWbRS9Xz)
- **Key Fields**: TelegramUserId (primary), Status, AccessLevel
- **Usage Notes**: Pending requests filtered in application code; AccessLevel defaults to VIEWER upon creation.

## Authorized Users Table Details
- **Table ID**: tblQ5i7EwSZrVYwT6A
- **Primary View**: `Active Users` (viwL5vrKDM6C8CRJf)
- **Key Fields**: TelegramUserId, AccessLevel, Status, UpdatedAt, UpdatedBy
- **Usage Notes**: Bot downloads this view on a schedule to refresh the in-memory authorization cache. Only records with `Status = Active` are treated as authorized; suspended or revoked users are excluded but retained for auditing. UpdatedAt/UpdatedBy fields support audit log correlation.

---

## Schedule Table Structure

### Table Information
- **Table ID**: `tblsxihPaZebzyBS2`
- **Primary Field**: `EventTitle` (fldwJzYx5l5NMnBET)
- **Purpose**: Manages retreat schedule for November 13-16, 2025 (Thursday-Sunday)
- **Created**: September 27, 2025

### Key Features
- Supports Russian and English event titles and descriptions
- 24-hour time format for precise scheduling
- Day-based grouping for easy navigation
- Active/inactive filtering for event management
- Links to responsible departments and persons
- Mandatory/optional event flagging

### Schedule Table Fields

#### EventTitle
- **Field ID**: `fldwJzYx5l5NMnBET`
- **Type**: `singleLineText`
- **Purpose**: Primary field - Title of the event
- **Required**: Yes (Primary field)
- **Example**: "Регистрация участников", "Talk 1: Ideal", "De Colores"

#### EventDate
- **Field ID**: `fldywzhY2xGarPBjx`
- **Type**: `date`
- **Purpose**: Date of the event
- **Required**: Yes
- **Format**: European format (`D/M/YYYY`)
- **Valid Range**: 13/11/2025 - 16/11/2025

#### StartTime
- **Field ID**: `fldy8llzYObPwtLAS`
- **Type**: `singleLineText`
- **Purpose**: Start time in 24-hour format
- **Required**: Yes
- **Format**: `HH:MM` (e.g., "09:00", "14:30")

#### EndTime
- **Field ID**: `fldSVERRPEGrt01P1`
- **Type**: `singleLineText`
- **Purpose**: End time in 24-hour format
- **Required**: No
- **Format**: `HH:MM` (e.g., "10:00", "15:30")

#### Description
- **Field ID**: `fldJC039MoBABhjDB`
- **Type**: `multilineText`
- **Purpose**: Detailed description of the event
- **Required**: No
- **Example**: "Регистрация и размещение кандидатов в комнатах"

#### Location
- **Field ID**: `fldJv61i8wBKm85mV`
- **Type**: `singleLineText`
- **Purpose**: Location or room where the event takes place
- **Required**: No
- **Example**: "Главный холл", "Часовня", "Конференц-зал"

#### Audience
- **Field ID**: `fldJ2qrRz5eeJsvUQ`
- **Type**: `singleSelect`
- **Purpose**: Target audience for the event
- **Required**: Yes
- **Options**:
  - `All` - ID: `selw4mMpFAAX3MMHn`
  - `Candidates` - ID: `selHrokUYNB1LJq4k`
  - `Team` - ID: `selhyWR3HzMvJ0Eo8`
  - `Clergy` - ID: `selC2xn33KAlmPmrh`
  - `Leadership` - ID: `selIcB1agLkQK9XAI`

#### EventType
- **Field ID**: `fld2FkrFTM3ArtdhC`
- **Type**: `singleSelect`
- **Purpose**: Type of event
- **Required**: Yes
- **Options**:
  - `Talk` - ID: `selaJbEmuyyHNfbeh`
  - `Meal` - ID: `selzQiWxhxNN2f70N`
  - `Chapel` - ID: `selBqnB3s1b4AJFNC`
  - `ROE` - ID: `seltW5k8u0ydSoZUQ`
  - `Activity` - ID: `seleRnLrfLo6gjl7s`
  - `Break` - ID: `selGsfBHKnhrYl2Jm`
  - `Prayer` - ID: `selz3IpA3qFmdSV9g`
  - `Celebration` - ID: `seloBgHtrWI3oVh64`

#### DayTag
- **Field ID**: `fldaT1FRDW7p9zpvN`
- **Type**: `singleSelect`
- **Purpose**: Day identifier for the retreat
- **Required**: Yes
- **Options**:
  - `Day 0` - ID: `selVWqI7RSfGRObKh`
  - `Day 1` - ID: `seltyw13cDQHB7DBA`
  - `Day 2` - ID: `selxCdMA3cGKiWyOc`
  - `Day 3` - ID: `selarmFzvKP0Yjktm`

#### Order
- **Field ID**: `fldfehkMFGrZ8qV4Q`
- **Type**: `number`
- **Purpose**: Order of events within the day (for sorting)
- **Required**: Yes
- **Precision**: 0 (integers only)
- **Example**: 1, 2, 3 (determines display order within each day)

#### Duration
- **Field ID**: `fld[TO_BE_FILLED]`
- **Type**: `duration`
- **Purpose**: Duration of the event
- **Required**: No
- **Format**: Airtable duration format (`h:mm`)

#### IsActive
- **Field ID**: `fldS24f13v1STUFQ8`
- **Type**: `checkbox`
- **Purpose**: Whether this event is active and should be displayed
- **Required**: No
- **Default**: `true`
- **Usage**: Filter inactive events from bot display

#### IsMandatory
- **Field ID**: `fld3A4pa7OOpJ3Ydc`
- **Type**: `checkbox`
- **Purpose**: Whether this event is mandatory for participants
- **Required**: No
- **Default**: `false`
- **Usage**: Highlight important events in bot display

#### ResponsibleDepartment
- **Field ID**: `fld[TO_BE_FILLED]`
- **Type**: `singleSelect`
- **Purpose**: Department responsible for the event
- **Required**: No
- **Options**: Same as Department field in Participants table

#### ResponsiblePerson
- **Field ID**: `fld[TO_BE_FILLED]`
- **Type**: `multipleRecordLinks`
- **Purpose**: Person(s) responsible for this event
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

#### Notes
- **Field ID**: `fld[TO_BE_FILLED]`
- **Type**: `multilineText`
- **Purpose**: Additional notes or special instructions
- **Required**: No
- **Example**: "Bring your Bible", "Dress code: formal"

### Views Available (To Be Created)

#### Schedule Table Views

1. **All Events** (`viw[TO_BE_CREATED]`) - Grid view showing all schedule records (to be created)
2. **Active Events** (`viwVk6sDqiF4qQyHM`) - Grid view filtered for IsActive = true
3. **By Day** (`viw[TO_BE_FILLED]`) - Grid view grouped by DayTag, sorted by Order
4. **November 13** (`viw[TO_BE_FILLED]`) - Filtered for EventDate = 13/11/2025
5. **November 14** (`viw[TO_BE_FILLED]`) - Filtered for EventDate = 14/11/2025
6. **November 15** (`viw[TO_BE_FILLED]`) - Filtered for EventDate = 15/11/2025
7. **November 16** (`viw[TO_BE_FILLED]`) - Filtered for EventDate = 16/11/2025
8. **Mandatory Events** (`viw[TO_BE_FILLED]`) - Filtered for IsMandatory = true

### Sample Schedule Record Structure

```json
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
    "Duration": "2:00",
    "IsActive": true,
    "IsMandatory": true,
    "ResponsibleDepartment": "Administration",
    "ResponsiblePerson": ["recParticipantID"],
    "Notes": "Подготовить регистрационные формы"
  }
}
```

### Implementation Considerations for Schedule

1. **Caching Strategy**: Implement 10-minute cache TTL to meet business requirements
2. **Date Filtering**: Always filter for November 13-16, 2025 date range
3. **Time Format**: Maintain 24-hour format throughout the application
4. **Sorting**: Primary sort by EventDate, secondary by Order field
5. **Active Filter**: Default to showing only IsActive = true events
6. **Localization**: Support both Russian and English content
7. **Special Characters**: Handle special characters like «De Colores» properly
8. **Relationship Expansion**: Fetch participant names when displaying ResponsiblePerson
9. **Rate Limiting**: Respect Airtable's 5 requests/second limit
10. **Error Handling**: Graceful fallback for empty schedule days
