# Field Mappings

This document describes the field mappings between the Participant model and Airtable fields, including validation rules and data transformation logic.

## Airtable Field Mappings

The following table shows the mapping between Python model fields and their corresponding Airtable fields:

### Core Fields
| Python Field | Airtable Field Name | Field Type | Required | Validation |
|-------------|-------------------|------------|----------|------------|
| full_name_ru | FullNameRU | singleLineText | Yes | Min length 1 |
| full_name_en | FullNameEN | singleLineText | No | - |
| church | Church | singleLineText | No | - |
| country_and_city | CountryAndCity | singleLineText | No | - |
| contact_information | ContactInformation | singleLineText | No | - |
| submitted_by | SubmittedBy | singleLineText | No | - |

### Enum Fields
| Python Field | Airtable Field Name | Field Type | Options |
|-------------|-------------------|------------|----------|
| gender | Gender | singleSelect | M, F |
| size | Size | singleSelect | XS, S, M, L, XL, XXL, 3XL |
| role | Role | singleSelect | CANDIDATE, TEAM |
| department | Department | singleSelect | ROE, Chapel, Setup, Palanka, Administration, Kitchen, Decoration, Bell, Refreshment, Worship, Media, Clergy, Rectorate |
| payment_status | PaymentStatus | singleSelect | Paid, Partial, Unpaid |

### Numeric and Date Fields
| Python Field | Airtable Field Name | Field Type | Validation |
|-------------|-------------------|------------|------------|
| payment_amount | PaymentAmount | number | Integer ≥ 0 |
| payment_date | PaymentDate | date | YYYY-MM-DD format |

### Accommodation Fields (New)
| Python Field | Airtable Field Name | Field Type | Validation | Description |
|-------------|-------------------|------------|------------|-------------|
| floor | Floor | singleLineText | Integer or string | Supports numeric floors (1, 2, 3) and descriptive names ("Ground", "Basement") |
| room_number | RoomNumber | singleLineText | Alphanumeric | Accepts room numbers like "101", "A12B", "Suite 100" |

## Field Validation Rules

### Text Field Validation
- **Required fields**: Only `full_name_ru` is required
- **Empty string handling**: Empty strings are converted to `None` for optional fields
- **Whitespace**: Leading and trailing whitespace is trimmed

### Accommodation Field Validation
- **Floor field**: Accepts both integer values (1, 2, 3) and descriptive strings ("Ground", "Basement", "Mezzanine")
- **Room Number field**: Accepts alphanumeric values with support for various formats:
  - Numeric: "101", "205", "1001"
  - Alphanumeric: "A12B", "C204", "Room-301"
  - Descriptive: "Suite 100", "Conference Room A"
- **Empty value handling**: Both fields convert empty strings to `None` for proper null handling in display

### Enum Field Validation
- **Validation**: Only predefined enum values are accepted
- **Case sensitivity**: Exact match required for enum values
- **Russian display**: Enum values are displayed with Russian translations in the UI

### Special Field Validation
- **Payment Amount**: Must be a non-negative integer
- **Payment Date**: Must follow YYYY-MM-DD format (ISO 8601)

## Data Transformation

### Model to Airtable (Serialization)
```python
def to_airtable_fields(self) -> dict:
    """Convert participant to Airtable field format"""
    return {
        "FullNameRU": self.full_name_ru,
        "FullNameEN": self.full_name_en,
        "Church": self.church,
        "CountryAndCity": self.country_and_city,
        "Gender": self.gender,
        "Size": self.size,
        "Role": self.role,
        "Department": self.department,
        "ContactInformation": self.contact_information,
        "PaymentStatus": self.payment_status,
        "PaymentAmount": self.payment_amount,
        "PaymentDate": self.payment_date,
        "SubmittedBy": self.submitted_by,
        "Floor": self.floor,  # New accommodation field
        "RoomNumber": self.room_number,  # New accommodation field
    }
```

### Airtable to Model (Deserialization)
```python
@classmethod
def from_airtable_record(cls, record: dict) -> 'Participant':
    """Create participant from Airtable record"""
    fields = record.get('fields', {})
    return cls(
        # ... other fields ...
        floor=fields.get('Floor'),  # New accommodation field
        room_number=fields.get('RoomNumber'),  # New accommodation field
    )
```

## Russian Field Labels

For user interface display, the following Russian translations are used:

| Field | Russian Label |
|-------|---------------|
| floor | Этаж |
| room_number | Номер комнаты |
| full_name_ru | Имя русское |
| full_name_en | Имя английское |
| church | Церковь |
| country_and_city | Местоположение |
| gender | Пол |
| size | Размер |
| role | Роль |
| department | Департамент |
| contact_information | Контакты |
| payment_status | Статус платежа |
| payment_amount | Сумма платежа |
| payment_date | Дата платежа |
| submitted_by | Кто подал |

## Implementation Notes

1. **Field ID Discovery**: Field IDs are automatically discovered using the `get_schema()` method in `airtable_client.py`
2. **Backward Compatibility**: All existing participants continue to work without accommodation fields
3. **Error Handling**: Field mapping errors are handled gracefully with appropriate fallbacks
4. **Rate Limiting**: Airtable API rate limits (5 requests/second) are respected during field operations