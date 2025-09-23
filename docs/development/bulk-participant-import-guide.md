# Bulk Participant Import Guide

**Version**: 1.0
**Last Updated**: 2025-09-23
**Author**: Development Team

## Overview

This guide explains how to safely import large batches of participant data from CSV files into the Airtable database using our automated import system.

## Quick Start

For experienced developers who just need the commands:

```bash
# 1. Prepare your CSV file with the required format
# 2. Run dry-run validation
python scripts/import_israel_missions_participants.py "your_file.csv"

# 3. Run live import (requires confirmation)
python scripts/import_israel_missions_participants.py "your_file.csv" --confirm-live
```

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [CSV File Format](#csv-file-format)
3. [Import Process](#import-process)
4. [Command Options](#command-options)
5. [Safety Features](#safety-features)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Prerequisites

### Environment Setup

1. **Virtual Environment**: Ensure the Python virtual environment is activated
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Environment Variables**: Required variables must be set
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export AIRTABLE_API_KEY="your_airtable_key"
   export AIRTABLE_BASE_ID="appRp7Vby2JMzN0mC"  # Default
   ```

3. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements/dev.txt
   ```

## CSV File Format

### Required Columns

Your CSV file **must** contain these exact column headers:

| Column | Description | Example |
|--------|-------------|---------|
| `FullNameRU` | Full name in Russian/Latin | "Hannah Chin" |
| `DateOfBirth` | US format date | "7/2/1992" |
| `Gender` | Gender (flexible format) | "Female", "F", "Male", "M" |
| `Size` | Clothing size | "L", "XL", "S", etc. |
| `ContactInformation` | Phone/contact info | "7147426601" |
| `CountryAndCity` | Location info | "USA", "United States" |
| `Role` | Participant role | "TEAM", "CANDIDATE" |

### Example CSV Format

```csv
FullNameRU,DateOfBirth,Gender,Size,ContactInformation,CountryAndCity,Role
Hannah Chin,7/2/1992,Female,L,7147426601,USA,TEAM
Jimmy Kim,6/24/1995,Male,XL,7147436722,USA,TEAM
Samuel An,9/7/2003,Male,XL,5626776844,United States of America,TEAM
```

### Data Transformations

The system automatically handles:

- **Date Format**: US format (M/D/YYYY) → ISO format (YYYY-MM-DD)
- **Gender Normalization**: "Female"/"Male" → "F"/"M"
- **Contact Info**: Cleaned and normalized
- **Additional Fields**: Auto-generated submission metadata

## Import Process

### Step 1: Dry-Run Validation (Always Run First!)

```bash
python scripts/import_israel_missions_participants.py "your_file.csv"
```

**What this does:**
- ✅ Validates CSV structure and data
- ✅ Shows transformation preview
- ✅ Identifies potential issues
- ❌ **Does NOT** write to database

**Expected Output:**
```
ISRAEL MISSIONS 2025 IMPORT SUMMARY
============================================================
Duration: 0.0 seconds
Total rows processed: 42

RESULTS:
  ✅ Successful: 42
  🔄 Duplicates skipped: 0
  ❌ Validation errors: 0
  🚫 API errors: 0
  ⚠️ Transformation errors: 0

Success rate: 100.0%
Overall status: ✅ SUCCESS
```

### Step 2: Live Import (Production Write)

```bash
python scripts/import_israel_missions_participants.py "your_file.csv" --confirm-live
```

**Safety Prompts:**
1. Script shows dry-run results first
2. Warns about production database writes
3. Requires typing "CONFIRM" to proceed

## Command Options

### Basic Usage
```bash
python scripts/import_israel_missions_participants.py <csv_file> [options]
```

### Available Options

| Option | Description | Example |
|--------|-------------|---------|
| `--confirm-live` | Enable live import mode | Required for actual imports |
| `--max-records N` | Limit import to N records | `--max-records 10` |
| `--rate-limit X` | Requests per second | `--rate-limit 3.0` |
| `--verbose` | Enable debug logging | `--verbose` |
| `--preview-samples N` | Show N preview samples | `--preview-samples 5` |

### Example Commands

```bash
# Test with first 5 records only
python scripts/import_israel_missions_participants.py "test.csv" --max-records 5

# Live import with slower rate limiting
python scripts/import_israel_missions_participants.py "data.csv" --confirm-live --rate-limit 2.0

# Verbose logging for debugging
python scripts/import_israel_missions_participants.py "data.csv" --verbose
```

## Safety Features

### Built-in Safeguards

1. **Dry-Run Default**: Script defaults to validation mode
2. **Explicit Confirmation**: Live mode requires `--confirm-live` flag
3. **Interactive Prompt**: Must type "CONFIRM" to proceed
4. **Duplicate Detection**: Automatically skips existing participants
5. **Rate Limiting**: Respects Airtable API limits (5 req/sec default)
6. **Data Validation**: Ensures all required fields are present
7. **Error Handling**: Graceful failure with detailed error messages

### Logging and Audit Trail

- **Contact Info Redaction**: Phone numbers masked in logs (71******01)
- **Record IDs**: Each successful import gets unique Airtable record ID
- **Timestamps**: All operations timestamped in ISO format
- **Status Tracking**: Per-record success/failure status

## Troubleshooting

### Common Issues and Solutions

#### 1. Date Format Errors
```
❌ Cannot parse date value "24/06/1995" for field DateOfBirth
```
**Solution**: Ensure dates are in US format (M/D/YYYY), not European (DD/MM/YYYY)

#### 2. Missing Required Fields
```
❌ Missing required fields: ['FullNameRU', 'ContactInformation']
```
**Solution**: Check CSV has all required columns with exact spelling

#### 3. Environment Variables Not Set
```
❌ Environment validation failed: AIRTABLE_API_KEY not found
```
**Solution**: Set required environment variables
```bash
export AIRTABLE_API_KEY="your_key_here"
```

#### 4. CSV File Not Found
```
❌ FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'
```
**Solution**: Use absolute path or ensure file is in current directory
```bash
python scripts/import_israel_missions_participants.py "/full/path/to/data.csv"
```

#### 5. Permission Errors
```
❌ 403 Client Error: Forbidden
```
**Solution**: Verify Airtable API key has write permissions to the base

### Debugging Steps

1. **Run with verbose logging**:
   ```bash
   python scripts/import_israel_missions_participants.py "data.csv" --verbose
   ```

2. **Test with small batch**:
   ```bash
   python scripts/import_israel_missions_participants.py "data.csv" --max-records 3
   ```

3. **Check environment**:
   ```bash
   echo $AIRTABLE_API_KEY
   echo $AIRTABLE_BASE_ID
   ```

## Best Practices

### Before Import

1. **✅ Always run dry-run first**: Never skip validation
2. **✅ Review sample data**: Check the preview output carefully
3. **✅ Start small**: Test with `--max-records 5` for new datasets
4. **✅ Backup consideration**: Consider Airtable backup if importing large datasets
5. **✅ Coordinate timing**: Avoid imports during peak usage times

### During Import

1. **✅ Monitor progress**: Watch the console output for errors
2. **✅ Don't interrupt**: Let the process complete naturally
3. **✅ Rate limiting**: Use default 5 req/sec unless system is slow

### After Import

1. **✅ Verify in Airtable**: Spot-check imported records
2. **✅ Archive CSV**: Keep original file for audit trail
3. **✅ Document**: Note any issues or special handling required

### File Management

```bash
# Good file naming convention
participants_israel_missions_2025_corrected_20250923.csv

# Organize in dated folders
imports/
  2025-09-23/
    israel_missions_original.csv
    israel_missions_corrected.csv
    import_log_20250923.txt
```

## Advanced Usage

### Batch Processing Multiple Files

```bash
#!/bin/bash
# Process multiple CSV files
for file in imports/*.csv; do
    echo "Processing $file..."
    python scripts/import_israel_missions_participants.py "$file" --confirm-live
done
```

### Custom Rate Limiting for Large Imports

```bash
# For very large imports, slow down to avoid hitting limits
python scripts/import_israel_missions_participants.py "large_file.csv" \
    --confirm-live --rate-limit 2.0
```

## Script Architecture

### How It Works

The import system follows this architecture:

1. **CSV Parser** → Reads and validates CSV structure
2. **Data Transformer** → Normalizes data (dates, gender, etc.)
3. **Duplicate Detector** → Checks against existing records
4. **Airtable Client** → Handles API communication with rate limiting
5. **Result Aggregator** → Tracks success/failure statistics

### Key Components

- `scripts/import_israel_missions_participants.py` - Main CLI script
- `src/services/israel_missions_import_service.py` - Business logic
- `src/data/importers/israel_missions_mapping.py` - Data transformation
- `src/data/airtable/airtable_client.py` - API client with rate limiting

## Support

### Getting Help

1. **Check logs**: Look for detailed error messages in console output
2. **Review this guide**: Most issues are covered in troubleshooting
3. **Test environment**: Try with a small test file first
4. **Contact team**: Reach out with specific error messages and context

### Reporting Issues

When reporting problems, include:
- Full command used
- Error message (copy/paste)
- Sample of CSV data (anonymized)
- Environment details (OS, Python version)

---

## Summary

The bulk import system provides a safe, reliable way to import participant data with built-in validation, duplicate detection, and error handling. Always start with dry-run validation, review the results carefully, and use the safety features to ensure successful imports.

**Remember**: The system is designed to be safe and forgiving. When in doubt, run another dry-run or test with a small subset of data first.