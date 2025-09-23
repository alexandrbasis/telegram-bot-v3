#!/usr/bin/env python3
"""
Israel Missions 2025 Participant Import CLI Script

This script provides a command-line interface for importing participant data
from CSV exports of Google Form responses into the production Airtable database.

Features:
- Mandatory dry-run validation before live operations
- Interactive confirmation prompts for safety
- Comprehensive logging and error reporting
- Rate limiting and retry logic
- Environment variable validation

Usage:
    # Dry run (validation only)
    python scripts/import_israel_missions_participants.py path/to/participants.csv

    # Live import (requires explicit confirmation)
    python scripts/import_israel_missions_participants.py path/to/participants.csv --confirm-live

    # Custom rate limit
    python scripts/import_israel_missions_participants.py path/to/participants.csv --rate-limit 0.5

    # Limit records for testing
    python scripts/import_israel_missions_participants.py path/to/participants.csv --max-records 10

Safety Features:
- Defaults to dry-run mode (no data changes)
- Requires explicit --confirm-live flag for production writes
- Validates environment configuration before starting
- Provides detailed preview of changes before confirmation
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.settings import get_settings
from src.data.airtable.airtable_client import AirtableClient, AirtableConfig
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.services.israel_missions_import_service import (
    IsraelMissionsImportService,
    ImportMode,
    ImportSummary,
)

logger = logging.getLogger(__name__)

# Constants
DEFAULT_RATE_LIMIT = 0.2  # 5 requests per second
MIN_RATE_LIMIT = 0.1      # 10 requests per second max
MAX_RATE_LIMIT = 2.0      # 0.5 requests per second min


def configure_logging(verbose: bool = False) -> None:
    """Configure application logging safely.

    - Creates logs directory if missing
    - Attaches stdout handler always
    - Attaches file handler when possible (non-fatal if it fails)
    - Sets root logger level so tests observing setLevel still pass
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    handlers = [logging.StreamHandler(sys.stdout)]

    logs_dir = Path("logs")
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(logs_dir / "israel_missions_import.log", mode="a")
        handlers.append(file_handler)
    except Exception:
        # Fall back to stdout-only logging if file handler cannot be created
        pass

    # Ensure root logger level is set explicitly (used by tests)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
    )


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Import Israel Missions 2025 participants from CSV to Airtable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'csv_file',
        type=Path,
        help='Path to CSV file containing participant data'
    )

    parser.add_argument(
        '--confirm-live',
        action='store_true',
        help='Enable live import mode (writes to production Airtable). '
             'Without this flag, script runs in dry-run mode only.'
    )

    parser.add_argument(
        '--rate-limit',
        type=float,
        default=DEFAULT_RATE_LIMIT,
        metavar='SECONDS',
        help=f'Delay between API requests in seconds (default: {DEFAULT_RATE_LIMIT}). '
             f'Range: {MIN_RATE_LIMIT} to {MAX_RATE_LIMIT} seconds.'
    )

    parser.add_argument(
        '--max-records',
        type=int,
        metavar='N',
        help='Maximum number of records to process (for testing purposes)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    parser.add_argument(
        '--preview-samples',
        type=int,
        default=3,
        metavar='N',
        help='Number of sample payloads to show in dry-run preview (default: 3)'
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """Validate command line arguments."""
    errors = []

    # Validate CSV file
    if not args.csv_file.exists():
        errors.append(f"CSV file not found: {args.csv_file}")
    elif not args.csv_file.is_file():
        errors.append(f"Path is not a file: {args.csv_file}")
    elif not args.csv_file.suffix.lower() == '.csv':
        errors.append(f"File must have .csv extension: {args.csv_file}")

    # Validate rate limit
    if not (MIN_RATE_LIMIT <= args.rate_limit <= MAX_RATE_LIMIT):
        errors.append(f"Rate limit must be between {MIN_RATE_LIMIT} and {MAX_RATE_LIMIT} seconds")

    # Validate max records
    if args.max_records is not None and args.max_records < 1:
        errors.append("Max records must be at least 1")

    # Validate preview samples
    if args.preview_samples < 0:
        errors.append("Preview samples must be non-negative")

    if errors:
        logger.error("Argument validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return False

    return True


def validate_environment() -> bool:
    """Validate required environment variables and configuration."""
    try:
        settings = get_settings()

        # Check required settings
        required_checks = [
            (settings.telegram.bot_token, "TELEGRAM_BOT_TOKEN"),
            (settings.database.airtable_api_key, "AIRTABLE_API_KEY"),
            (settings.database.airtable_base_id, "AIRTABLE_BASE_ID"),
        ]

        missing = []
        for value, name in required_checks:
            if not value:
                missing.append(name)

        if missing:
            logger.error("Missing required environment variables:")
            for var in missing:
                logger.error(f"  - {var}")
            return False

        logger.info(f"Environment validation passed:")
        logger.info(f"  - Airtable Base: {settings.database.airtable_base_id}")
        logger.info(f"  - Airtable Table: {settings.database.airtable_table_name}")
        logger.info(f"  - Environment: {settings.application.environment}")

        return True

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False


async def run_dry_run(
    import_service: IsraelMissionsImportService,
    csv_file: Path,
    max_records: Optional[int],
    preview_samples: int
) -> ImportSummary:
    """Run dry-run validation."""
    logger.info("=" * 60)
    logger.info("STARTING DRY-RUN VALIDATION")
    logger.info("=" * 60)
    logger.info(f"CSV File: {csv_file}")
    logger.info(f"Max Records: {max_records or 'unlimited'}")
    logger.info("")

    # Run dry-run import
    summary = await import_service.import_from_csv(
        csv_file,
        mode=ImportMode.DRY_RUN,
        max_records=max_records
    )

    # Display results
    report = import_service.format_summary_report(summary)
    logger.info(report)

    # Show payload preview if successful validations exist
    if summary.successful > 0:
        logger.info("")
        preview = import_service.get_dry_run_preview(summary, max_samples=preview_samples)
        logger.info(preview)

    return summary


async def run_live_import(
    import_service: IsraelMissionsImportService,
    csv_file: Path,
    max_records: Optional[int]
) -> ImportSummary:
    """Run live import with confirmation."""
    logger.info("=" * 60)
    logger.info("STARTING LIVE IMPORT")
    logger.info("=" * 60)
    logger.info("⚠️  WARNING: This will write data to production Airtable!")
    logger.info(f"CSV File: {csv_file}")
    logger.info(f"Max Records: {max_records or 'unlimited'}")
    logger.info("")

    # Final confirmation prompt
    confirmation = input("Type 'CONFIRM' to proceed with live import: ")
    if confirmation != 'CONFIRM':
        logger.info("Live import cancelled by user")
        return ImportSummary()  # Empty summary

    logger.info("✅ User confirmed - proceeding with live import")
    logger.info("")

    # Run live import
    summary = await import_service.import_from_csv(
        csv_file,
        mode=ImportMode.LIVE,
        max_records=max_records
    )

    # Display results
    report = import_service.format_summary_report(summary)
    logger.info(report)

    return summary


def print_next_steps(dry_run_summary: ImportSummary, live_mode_requested: bool):
    """Print next steps guidance for the operator."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("NEXT STEPS")
    logger.info("=" * 60)

    if not live_mode_requested:
        if dry_run_summary.is_successful():
            logger.info("✅ Dry-run validation completed successfully!")
            logger.info("")
            logger.info("To proceed with live import:")
            logger.info("1. Review the payload samples above")
            logger.info("2. Confirm with stakeholders if needed")
            logger.info("3. Re-run with --confirm-live flag:")
            logger.info(f"   python {sys.argv[0]} {sys.argv[1]} --confirm-live")
        else:
            logger.info("❌ Dry-run validation found issues.")
            logger.info("")
            logger.info("Before proceeding:")
            logger.info("1. Fix validation errors in the CSV file")
            logger.info("2. Re-run dry-run validation")
            logger.info("3. Only then proceed with --confirm-live")
    else:
        if dry_run_summary.is_successful():
            logger.info("✅ Live import completed successfully!")
            logger.info("")
            logger.info("Recommended follow-up:")
            logger.info("1. Verify records in Airtable dashboard")
            logger.info("2. Run spot-checks on imported data")
            logger.info("3. Archive the CSV file for audit trail")
        else:
            logger.info("⚠️  Live import completed with issues.")
            logger.info("")
            logger.info("Recommended actions:")
            logger.info("1. Review failed records in the summary above")
            logger.info("2. Check Airtable for partially imported data")
            logger.info("3. Consider re-running failed records only")


async def main():
    """Main CLI entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Configure logging (stdout + optional file handler)
    configure_logging(verbose=args.verbose)
    if args.verbose:
        logger.debug("Verbose logging enabled")

    logger.info("Israel Missions 2025 Participant Import Tool")
    logger.info("=" * 60)

    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)

    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Please check your .env file.")
        sys.exit(1)

    try:
        # Initialize services
        settings = get_settings()

        config = AirtableConfig(
            api_key=settings.database.airtable_api_key,
            base_id=settings.database.airtable_base_id,
            table_name=settings.database.airtable_table_name,
            table_id=settings.database.airtable_table_id
        )

        client = AirtableClient(config)

        repository = AirtableParticipantRepository(client)

        import_service = IsraelMissionsImportService(
            participant_repository=repository,
            rate_limit_delay=args.rate_limit
        )

        # Always run dry-run first
        dry_run_summary = await run_dry_run(
            import_service,
            args.csv_file,
            args.max_records,
            args.preview_samples
        )

        # If live mode requested and dry-run successful, proceed to live import
        live_summary = None
        if args.confirm_live:
            if dry_run_summary.is_successful():
                live_summary = await run_live_import(
                    import_service,
                    args.csv_file,
                    args.max_records
                )
            else:
                logger.error("")
                logger.error("❌ Cannot proceed to live import - dry-run validation failed")
                logger.error("Please fix validation errors before attempting live import")

        # Print guidance
        final_summary = live_summary if live_summary else dry_run_summary
        print_next_steps(final_summary, args.confirm_live)

        # Exit with appropriate code
        if final_summary.is_successful():
            logger.info("")
            logger.info("✅ Import process completed successfully")
            sys.exit(0)
        else:
            logger.info("")
            logger.info("⚠️  Import process completed with issues")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Import cancelled by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Import failed with unexpected error: {e}")
        logger.exception("Full error details:")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())