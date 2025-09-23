# Israel Missions 2025 CSV → Airtable Mapping

This document defines how columns from the Google Form export `Israel Missions 2025_ Team Members - Form Responses 1.csv` map to the production Airtable **Participants** table. It should be treated as the canonical reference for import tooling and manual verification.

> **CSV sample header**: `FullNameRU, DateOfBirth, Gender, Size, ContactInformation, CountryAndCity, Role`

## Column-Level Mapping

| CSV Column | Airtable Field | Field ID | Type | Transformation | Required | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `FullNameRU` | `FullNameRU` | `fldOcpA3JW5MRmR6R` | Text | `strip()` whitespace | ✅ | Primary field in Airtable; must be non-empty and unique enough for human review. |
| `DateOfBirth` | `DateOfBirth` | `fld1rN2cffxKuZh4i` | Date | Parse with `%m/%d/%Y` → serialize as `%d/%m/%Y` | ⚠️ | Source data uses U.S. style (e.g. `7/2/1992` → 2 July 1992). Invalid/blank values should be logged and left unset. |
| `Gender` | `Gender` | `fldOAGXoU0DqqFRmB` | Single select | Map `{ "Female": "F", "Male": "M" }` (case-insensitive) | ⚠️ | Unknown values should log warning and remain unset to avoid Airtable option mismatch. |
| `Size` | `Size` | `fldZyNgaaa1snp6s7` | Single select | Uppercase and validate against `{XS,S,M,L,XL,XXL,3XL}` | ⚠️ | Reject/flag any size outside known list; do not coerce. |
| `ContactInformation` | `ContactInformation` | `fldSy0Hbwl49VtZvf` | Text | `strip()` | ✅ (for duplicate detection) | Used for duplicate detection; if blank, fallback to `FullNameRU`. Never write partial phone fragments to logs. |
| `CountryAndCity` | `CountryAndCity` | `fldJ7dFRzx7bR9U6g` | Text | `strip()` | ➖ | Optional context for operators. |
| `Role` | `Role` | `fldetbIGOkKFK0hYq` | Single select | Uppercase then validate against `{TEAM, CANDIDATE}` | ⚠️ | Default to `TEAM` if blank (per mission requirements) but note fallback in run log. |

## Derived / Defaulted Airtable Fields

| Airtable Field | Value Strategy | Rationale |
| --- | --- | --- |
| `SubmittedBy` | Static `"Israel Missions 2025 Form"` | Traceability of import source. |
| `Notes` | Append `"Imported on {ISO date} via Israel Missions importer."` | Operational audit trail. |
| `EnvironmentTag` *(if present)* | `"missions-2025"` | Allows downstream filters; omit if field not defined in base. |

## Duplicate Detection Policy

1. Primary key: normalized `ContactInformation` (digits only, strip `+`, `-`, spaces).  
2. Secondary key: case-folded `FullNameRU` **and** `DateOfBirth`.  
3. If both keys fail (e.g., missing DOB), mark record for manual review; do **not** auto-create.

Importer should log duplicates at `INFO` level with redaction: `+7********01`.

## Validation Rules

- **Required field failures** (`FullNameRU`, `ContactInformation`) must raise a validation error and skip the record.
- **Enum mismatches** (`Gender`, `Size`, `Role`) should produce warning + skip assignment (leave field empty) but still allow record creation.
- **Date parsing** errors leave DOB empty and log a warning; do not abort entire run.
- **Whitespace-only entries** should be treated as missing values.

## Dry-Run Expectations

Dry-run output must include a tabular summary:

- Total rows scanned
- Rows ready for import
- Rows skipped (duplicates)
- Rows with validation errors
- Rows requiring manual review

For each row, include a structured JSON payload (without secrets) so stakeholders can sign off before live import.

## Outstanding Questions

- Confirm with business owner whether `TEAM` should remain the default `Role` when CSV is blank.
- Determine if additional Airtable fields (e.g., `Department`, `PaymentStatus`) require mission-specific defaults.
- Verify Airtable currently stores DOB in European format (`DD/MM/YYYY`)—last confirmed 2025-09-10.

---

_Last updated: 2025-09-23. Contact @data-eng for schema changes._
