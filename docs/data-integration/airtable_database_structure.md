# Airtable Database Structure Documentation

## Database Information
- **Base ID**: `appRp7Vby2JMzN0mC`
- **Base Type**: Airtable
- **Environment**: Development

## Tables Overview

### 1. Participants Table
**Table ID**: `tbl8ivwOdAUvMi3Jy`
**Primary Field**: `FullNameRU` (fldOcpA3JW5MRmR6R)

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
- **Precision**: 0 (integers only)
- **Constraints**: Must be >= 0 and <= 120
- **Example**: 35

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
- **Format**: ISO format (YYYY-MM-DD)
- **Example**: "1990-05-15"

## Views Available

1. **All Data** (`viwxzBkV6XPSOlaY6`) - Grid view showing all records
2. **Team Members** (`viwhPNd0BbAxw9lr2`) - Grid view filtered for team members
3. **Candidates** (`viwIJSnpWr61efCYB`) - Grid view filtered for candidates

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

### Sample Record Structure:
```json
{
  "fields": {
    "FullNameRU": "string (required)",
    "FullNameEN": "string (optional)",
    "Gender": "M|F",
    "Size": "XS|S|M|L|XL|XXL|3XL",
    "Church": "string (optional)",
    "Role": "CANDIDATE|TEAM",
    "Department": "ROE|Chapel|Setup|...",
    "CountryAndCity": "string (optional)",
    "SubmittedBy": "string (optional)",
    "ContactInformation": "string (optional)",
    "PaymentStatus": "Paid|Partial|Unpaid",
    "PaymentAmount": "number (integer)",
    "PaymentDate": "YYYY-MM-DD",
    "DateOfBirth": "YYYY-MM-DD (optional)",
    "Age": "number (integer, optional, 0-120)"
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