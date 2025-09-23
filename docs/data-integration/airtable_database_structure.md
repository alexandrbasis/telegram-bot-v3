# Airtable Database Structure Documentation

## Last Updated
- **Date**: September 22, 2025
- **Version**: 3.1.0
- **Changes**: Synchronized ROE and BibleReaders schemas with new scheduling fields, refreshed participant view catalog, documented ROE prayer support links

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
1. **All Data** (`viwxzBkV6XPSOlaY6`) - Grid view showing the full participant roster
2. **Тимы** (`viwhPNd0BbAxw9lr2`) - Grid view filtered for active team members
   - **Visible fields (export order)**: `FullNameRU`, `FullNameEN`, `Gender`, `Size`, `Church`, `Role`, `Department`, `CountryAndCity`, `PaymentStatus`, `Floor`, `DateOfBirth`, `ChurchLeader`, `IsDepartmentChief`, `SubmittedBy`, `ContactInformation`, `Age`, `RoeAssistant`, `Notes`, `Roe`, `BibleReaders`, `ROE 2`
3. **Тимы по департаментам** (`viwsTX6z1SKc0fc9c`) - Grid view grouping team members by department assignments (shares the same column layout as **Тимы**)
4. **Кандидаты** (`viwIJSnpWr61efCYB`) - Grid view filtered for candidate applications
   - **Visible fields (export order)**: `FullNameRU`, `FullNameEN`, `Gender`, `Size`, `Church`, `Role`, `CountryAndCity`, `SubmittedBy`, `PaymentStatus`, `Floor`, `RoomNumber`, `DateOfBirth`, `ChurchLeader`, `ContactInformation`, `Age`, `Notes`
5. **По этажам** (`viwvKvD2hDiAHmEK9`) - Grid view grouped by lodging floor assignments
6. **По комнатам** (`viwOFJJ8vmhwCsiJZ`) - Grid view grouped by room assignments
7. **Размеры** (`viwcH4YV8e0bOsXDn`) - Grid view grouping by clothing size selections

---

## ROE Table Structure

### Table Information
- **Table ID**: `tbl0j8bcgkV3lVAdc`
- **Primary Field**: `RoeTopic` (fldSniGvfWpmkpc1r)
- **Purpose**: Manages ROE (Rollo of Encouragement) sessions and assignments

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
