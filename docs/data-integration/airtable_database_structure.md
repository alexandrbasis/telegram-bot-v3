# Airtable Database Structure Documentation

## Last Updated
- **Date**: January 19, 2025
- **Version**: 3.0.0
- **Changes**: Added IsDepartmentChief field, new ROE and BibleReaders tables, and relationship fields

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
- **Format**: Localized Airtable date (`format = l`)
- **Example**: Locale-specific (e.g., "15.05.1990")

## Views Available

### Participants Table Views
1. **All Data** (`viwxzBkV6XPSOlaY6`) - Grid view showing all records
2. **Тимы** (`viwhPNd0BbAxw9lr2`) - Grid view filtered for team members
3. **Кандидаты** (`viwIJSnpWr61efCYB`) - Grid view filtered for candidates
4. **По этажам** (`viwvKvD2hDiAHmEK9`) - Grid view grouped by accommodation floor
5. **По комнатам** (`viwOFJJ8vmhwCsiJZ`) - Grid view grouped by accommodation room

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

#### RoistaChurch
- **Field ID**: `flday5BYiQsP8njau`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing church of the main Roista
- **Source**: Church field from linked Roista record
- **Read-only**: Yes (computed field)

#### RoistaDepartment
- **Field ID**: `fldomNR0M0AHolSmj`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing department of the main Roista
- **Source**: Department field from linked Roista record
- **Read-only**: Yes (computed field)

#### RoistaRoom
- **Field ID**: `fldNlkZv2bktVqFDl`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing room number of the main Roista
- **Source**: RoomNumber field from linked Roista record
- **Read-only**: Yes (computed field)

#### RoistaNotes
- **Field ID**: `fldHa1gyW60Dz9wfC`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing notes about the main Roista
- **Source**: Notes field from linked Roista record
- **Read-only**: Yes (computed field)

#### Assistant
- **Field ID**: `fldtTUTsJy6oCg1sE`
- **Type**: `multipleRecordLinks`
- **Purpose**: Links to assistant Roista from Participants table
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

#### AssistantChuch
- **Field ID**: `fldsDcqcSfilntPws`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing church of the assistant Roista
- **Source**: Church field from linked Assistant record
- **Read-only**: Yes (computed field)

#### AssistantDepartment
- **Field ID**: `fldgDVWQNFeooDRo7`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing department of the assistant Roista
- **Source**: Department field from linked Assistant record
- **Read-only**: Yes (computed field)

#### AssistantRoom
- **Field ID**: `fldBlcyDcW0NcUVcX`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing room number of the assistant Roista
- **Source**: RoomNumber field from linked Assistant record
- **Read-only**: Yes (computed field)

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
- **Purpose**: Links to participants who will be Bible readers
- **Required**: No
- **Links To**: Participants table (tbl8ivwOdAUvMi3Jy)

#### Church (from Participants)
- **Field ID**: `fldadEnWickpmcDCE`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing churches of the Bible readers
- **Source**: Church field from linked Participants records
- **Read-only**: Yes (computed field)

#### RoomNumber (from Participants)
- **Field ID**: `fldOGZxVkpFycVs38`
- **Type**: `multipleLookupValues`
- **Purpose**: Lookup field showing room numbers of the Bible readers
- **Source**: RoomNumber field from linked Participants records
- **Read-only**: Yes (computed field)

#### When
- **Field ID**: `fld6WfIcctT2WZnNO`
- **Type**: `date`
- **Purpose**: Date and time of the Bible reading session
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
    "RoeAssistant": ["recZZZZZZZZZZZZZZ"]
  }
}
```

#### ROE Table Record
```json
{
  "fields": {
    "RoeTopic": "string (required)",
    "Roista": ["recParticipantID1"],
    "Assistant": ["recParticipantID2"]
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
    - Links Roista presenters and assistants to specific topics
    - Lookup fields automatically show participant details for planning
    - Supports multiple Roistas per topic through relationship fields
13. **Bible Reading Coordination**: BibleReaders table manages reading assignments
    - Tracks multiple readers per session with location and timing
    - Enables scheduling and conflict detection through date fields
    - Can generate reading schedules and participant notifications
14. **Cross-Table Relationships**: Multiple relationship fields enable complex queries
    - Roe and RoeAssistant fields in Participants show ROE involvement
    - BibleReaders field shows reading assignments per participant
    - Enables comprehensive participant activity tracking across events
15. **Lookup Field Optimization**: Multiple lookup fields reduce API calls
    - Computed fields automatically update when source records change
    - Read-only fields prevent accidental data corruption
    - Useful for displaying related data without additional queries
