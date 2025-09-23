"""
Integration tests for Israel Missions 2025 participant import CLI script.

Tests cover CLI argument parsing, environment validation, workflow orchestration,
and end-to-end import scenarios using mocked components.
"""

import argparse
import tempfile
import csv
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import sys
import os

import pytest

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from import_israel_missions_participants import (
    setup_argument_parser,
    validate_arguments,
    validate_environment,
    run_dry_run,
    run_live_import,
    main,
    DEFAULT_RATE_LIMIT,
    MIN_RATE_LIMIT,
    MAX_RATE_LIMIT,
)


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample data."""
    data = [
        {
            "FullNameRU": "Тест Пользователь",
            "DateOfBirth": "1/1/1990",
            "Gender": "Male",
            "Size": "M",
            "ContactInformation": "+7-495-123-4567",
            "CountryAndCity": "Москва",
            "Role": "TEAM"
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestArgumentParsing:
    """Test CLI argument parsing functionality."""

    def test_setup_argument_parser(self):
        """Test argument parser setup."""
        parser = setup_argument_parser()

        assert isinstance(parser, argparse.ArgumentParser)
        assert "Import Israel Missions 2025 participants" in parser.description

    def test_required_csv_file_argument(self, sample_csv_file):
        """Test CSV file argument parsing."""
        parser = setup_argument_parser()
        args = parser.parse_args([str(sample_csv_file)])

        assert args.csv_file == sample_csv_file
        assert args.confirm_live is False  # Default
        assert args.rate_limit == DEFAULT_RATE_LIMIT
        assert args.max_records is None
        assert args.verbose is False

    def test_all_optional_arguments(self, sample_csv_file):
        """Test all optional arguments."""
        parser = setup_argument_parser()
        args = parser.parse_args([
            str(sample_csv_file),
            '--confirm-live',
            '--rate-limit', '0.5',
            '--max-records', '100',
            '--verbose',
            '--preview-samples', '5'
        ])

        assert args.csv_file == sample_csv_file
        assert args.confirm_live is True
        assert args.rate_limit == 0.5
        assert args.max_records == 100
        assert args.verbose is True
        assert args.preview_samples == 5

    def test_missing_csv_file_argument(self):
        """Test parser requires CSV file argument."""
        parser = setup_argument_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestArgumentValidation:
    """Test CLI argument validation."""

    def test_validate_arguments_valid_file(self, sample_csv_file):
        """Test validation passes with valid CSV file."""
        args = Mock()
        args.csv_file = sample_csv_file
        args.rate_limit = DEFAULT_RATE_LIMIT
        args.max_records = None
        args.preview_samples = 3

        result = validate_arguments(args)
        assert result is True

    def test_validate_arguments_nonexistent_file(self):
        """Test validation fails with nonexistent file."""
        args = Mock()
        args.csv_file = Path("nonexistent.csv")
        args.rate_limit = DEFAULT_RATE_LIMIT
        args.max_records = None
        args.preview_samples = 3

        result = validate_arguments(args)
        assert result is False

    def test_validate_arguments_directory_path(self, tmp_path):
        """Test validation fails when CSV path is directory."""
        args = Mock()
        args.csv_file = tmp_path  # Directory, not file
        args.rate_limit = DEFAULT_RATE_LIMIT
        args.max_records = None
        args.preview_samples = 3

        result = validate_arguments(args)
        assert result is False

    def test_validate_arguments_wrong_extension(self, tmp_path):
        """Test validation fails with wrong file extension."""
        txt_file = tmp_path / "test.txt"
        txt_file.touch()

        args = Mock()
        args.csv_file = txt_file
        args.rate_limit = DEFAULT_RATE_LIMIT
        args.max_records = None
        args.preview_samples = 3

        result = validate_arguments(args)
        assert result is False

    def test_validate_arguments_invalid_rate_limit(self, sample_csv_file):
        """Test validation fails with invalid rate limit."""
        args = Mock()
        args.csv_file = sample_csv_file
        args.rate_limit = 5.0  # Too high
        args.max_records = None
        args.preview_samples = 3

        result = validate_arguments(args)
        assert result is False

    def test_validate_arguments_invalid_max_records(self, sample_csv_file):
        """Test validation fails with invalid max records."""
        args = Mock()
        args.csv_file = sample_csv_file
        args.rate_limit = DEFAULT_RATE_LIMIT
        args.max_records = 0  # Invalid
        args.preview_samples = 3

        result = validate_arguments(args)
        assert result is False

    def test_validate_arguments_negative_preview_samples(self, sample_csv_file):
        """Test validation fails with negative preview samples."""
        args = Mock()
        args.csv_file = sample_csv_file
        args.rate_limit = DEFAULT_RATE_LIMIT
        args.max_records = None
        args.preview_samples = -1  # Invalid

        result = validate_arguments(args)
        assert result is False


class TestEnvironmentValidation:
    """Test environment validation functionality."""

    @patch('import_israel_missions_participants.get_settings')
    def test_validate_environment_success(self, mock_get_settings):
        """Test successful environment validation."""
        mock_settings = Mock()
        mock_settings.telegram.bot_token = "test_token"
        mock_settings.database.api_key = "test_key"
        mock_settings.database.base_id = "test_base"
        mock_settings.database.table_name = "test_table"
        mock_settings.application.environment = "test"
        mock_get_settings.return_value = mock_settings

        result = validate_environment()
        assert result is True

    @patch('import_israel_missions_participants.get_settings')
    def test_validate_environment_missing_bot_token(self, mock_get_settings):
        """Test environment validation fails with missing bot token."""
        mock_settings = Mock()
        mock_settings.telegram.bot_token = ""  # Missing
        mock_settings.database.api_key = "test_key"
        mock_settings.database.base_id = "test_base"
        mock_get_settings.return_value = mock_settings

        result = validate_environment()
        assert result is False

    @patch('import_israel_missions_participants.get_settings')
    def test_validate_environment_missing_api_key(self, mock_get_settings):
        """Test environment validation fails with missing API key."""
        mock_settings = Mock()
        mock_settings.telegram.bot_token = "test_token"
        mock_settings.database.api_key = None  # Missing
        mock_settings.database.base_id = "test_base"
        mock_get_settings.return_value = mock_settings

        result = validate_environment()
        assert result is False

    @patch('import_israel_missions_participants.get_settings')
    def test_validate_environment_exception_handling(self, mock_get_settings):
        """Test environment validation handles exceptions."""
        mock_get_settings.side_effect = Exception("Configuration error")

        result = validate_environment()
        assert result is False


class TestWorkflowFunctions:
    """Test workflow orchestration functions."""

    @pytest.mark.asyncio
    async def test_run_dry_run_success(self, sample_csv_file):
        """Test dry-run workflow execution."""
        # Mock import service
        mock_service = AsyncMock()
        mock_summary = Mock()
        mock_summary.successful = 1
        mock_service.import_from_csv.return_value = mock_summary
        mock_service.format_summary_report.return_value = "Test report"
        mock_service.get_dry_run_preview.return_value = "Test preview"

        result = await run_dry_run(mock_service, sample_csv_file, None, 3)

        assert result == mock_summary
        mock_service.import_from_csv.assert_called_once()
        mock_service.format_summary_report.assert_called_once_with(mock_summary)
        mock_service.get_dry_run_preview.assert_called_once_with(mock_summary, max_samples=3)

    @pytest.mark.asyncio
    async def test_run_live_import_cancelled(self, sample_csv_file):
        """Test live import cancelled by user."""
        mock_service = AsyncMock()

        with patch('builtins.input', return_value='CANCEL'):  # User cancels
            result = await run_live_import(mock_service, sample_csv_file, None)

        # Should return empty summary without calling service
        assert result.total_rows == 0
        mock_service.import_from_csv.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_live_import_confirmed(self, sample_csv_file):
        """Test live import with user confirmation."""
        mock_service = AsyncMock()
        mock_summary = Mock()
        mock_service.import_from_csv.return_value = mock_summary
        mock_service.format_summary_report.return_value = "Test report"

        with patch('builtins.input', return_value='CONFIRM'):  # User confirms
            result = await run_live_import(mock_service, sample_csv_file, 10)

        assert result == mock_summary
        mock_service.import_from_csv.assert_called_once()


class TestMainWorkflow:
    """Test main CLI workflow integration."""

    @pytest.mark.asyncio
    async def test_main_dry_run_only(self, sample_csv_file):
        """Test main workflow with dry-run only."""
        test_args = ['script_name', str(sample_csv_file)]

        with patch('sys.argv', test_args), \
             patch('import_israel_missions_participants.validate_environment', return_value=True), \
             patch('import_israel_missions_participants.get_settings') as mock_get_settings, \
             patch('import_israel_missions_participants.AirtableClient') as mock_client_class, \
             patch('import_israel_missions_participants.AirtableParticipantRepository') as mock_repo_class, \
             patch('import_israel_missions_participants.IsraelMissionsImportService') as mock_service_class, \
             patch('import_israel_missions_participants.run_dry_run') as mock_run_dry_run, \
             patch('import_israel_missions_participants.print_next_steps'):

            # Mock settings
            mock_settings = Mock()
            mock_settings.database.api_key = "test_key"
            mock_settings.database.base_id = "test_base"
            mock_settings.database.table_name = "test_table"
            mock_settings.database.table_id = "test_id"
            mock_get_settings.return_value = mock_settings

            # Mock successful dry-run
            mock_summary = Mock()
            mock_summary.is_successful.return_value = True
            mock_run_dry_run.return_value = mock_summary

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 0  # Success exit code
            mock_run_dry_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_live_import_workflow(self, sample_csv_file):
        """Test main workflow with live import."""
        test_args = ['script_name', str(sample_csv_file), '--confirm-live']

        with patch('sys.argv', test_args), \
             patch('import_israel_missions_participants.validate_environment', return_value=True), \
             patch('import_israel_missions_participants.get_settings') as mock_get_settings, \
             patch('import_israel_missions_participants.AirtableClient'), \
             patch('import_israel_missions_participants.AirtableParticipantRepository'), \
             patch('import_israel_missions_participants.IsraelMissionsImportService'), \
             patch('import_israel_missions_participants.run_dry_run') as mock_run_dry_run, \
             patch('import_israel_missions_participants.run_live_import') as mock_run_live_import, \
             patch('import_israel_missions_participants.print_next_steps'):

            # Mock settings
            mock_settings = Mock()
            mock_settings.database.api_key = "test_key"
            mock_settings.database.base_id = "test_base"
            mock_settings.database.table_name = "test_table"
            mock_settings.database.table_id = "test_id"
            mock_get_settings.return_value = mock_settings

            # Mock successful dry-run and live import
            mock_dry_summary = Mock()
            mock_dry_summary.is_successful.return_value = True
            mock_run_dry_run.return_value = mock_dry_summary

            mock_live_summary = Mock()
            mock_live_summary.is_successful.return_value = True
            mock_run_live_import.return_value = mock_live_summary

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 0  # Success exit code
            mock_run_dry_run.assert_called_once()
            mock_run_live_import.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_environment_validation_failure(self, sample_csv_file):
        """Test main workflow fails with environment validation error."""
        test_args = ['script_name', str(sample_csv_file)]

        with patch('sys.argv', test_args), \
             patch('import_israel_missions_participants.validate_environment', return_value=False):

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 1  # Error exit code

    @pytest.mark.asyncio
    async def test_main_keyboard_interrupt(self, sample_csv_file):
        """Test main workflow handles keyboard interrupt."""
        test_args = ['script_name', str(sample_csv_file)]

        with patch('sys.argv', test_args), \
             patch('import_israel_missions_participants.validate_environment', return_value=True), \
             patch('import_israel_missions_participants.get_settings', side_effect=KeyboardInterrupt()):

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 130  # Keyboard interrupt exit code

    @pytest.mark.asyncio
    async def test_main_unexpected_exception(self, sample_csv_file):
        """Test main workflow handles unexpected exceptions."""
        test_args = ['script_name', str(sample_csv_file)]

        with patch('sys.argv', test_args), \
             patch('import_israel_missions_participants.validate_environment', return_value=True), \
             patch('import_israel_missions_participants.get_settings', side_effect=Exception("Unexpected error")):

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 1  # Error exit code


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_validate_arguments_comprehensive_error_reporting(self, tmp_path):
        """Test that argument validation reports all errors together."""
        # Create non-CSV file
        txt_file = tmp_path / "test.txt"
        txt_file.touch()

        args = Mock()
        args.csv_file = txt_file  # Wrong extension
        args.rate_limit = 10.0  # Invalid rate limit
        args.max_records = -5  # Invalid max records
        args.preview_samples = -1  # Invalid preview samples

        result = validate_arguments(args)
        assert result is False
        # Multiple validation errors should all be caught

    def test_rate_limit_boundary_values(self, sample_csv_file):
        """Test rate limit validation at boundary values."""
        args = Mock()
        args.csv_file = sample_csv_file
        args.max_records = None
        args.preview_samples = 3

        # Test minimum boundary
        args.rate_limit = MIN_RATE_LIMIT
        assert validate_arguments(args) is True

        # Test maximum boundary
        args.rate_limit = MAX_RATE_LIMIT
        assert validate_arguments(args) is True

        # Test just below minimum
        args.rate_limit = MIN_RATE_LIMIT - 0.01
        assert validate_arguments(args) is False

        # Test just above maximum
        args.rate_limit = MAX_RATE_LIMIT + 0.01
        assert validate_arguments(args) is False


class TestCLIIntegration:
    """Integration tests simulating real CLI usage."""

    def test_help_output(self):
        """Test that help output is generated properly."""
        parser = setup_argument_parser()

        # This should not raise an exception
        help_text = parser.format_help()
        assert "Israel Missions 2025" in help_text
        assert "--confirm-live" in help_text
        assert "--rate-limit" in help_text

    @pytest.mark.asyncio
    async def test_verbose_logging_enabled(self, sample_csv_file):
        """Test that verbose flag enables debug logging."""
        test_args = ['script_name', str(sample_csv_file), '--verbose']

        with patch('sys.argv', test_args), \
             patch('logging.getLogger') as mock_get_logger, \
             patch('import_israel_missions_participants.validate_environment', return_value=False):

            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            with pytest.raises(SystemExit):
                await main()

            # Should have set debug level
            mock_logger.setLevel.assert_called()

    def test_argument_types_and_defaults(self, sample_csv_file):
        """Test argument types and default values."""
        parser = setup_argument_parser()

        # Test with minimal arguments
        args = parser.parse_args([str(sample_csv_file)])

        assert isinstance(args.csv_file, Path)
        assert isinstance(args.confirm_live, bool)
        assert isinstance(args.rate_limit, float)
        assert args.max_records is None or isinstance(args.max_records, int)
        assert isinstance(args.verbose, bool)
        assert isinstance(args.preview_samples, int)

        # Test defaults
        assert args.confirm_live is False
        assert args.rate_limit == DEFAULT_RATE_LIMIT
        assert args.verbose is False
        assert args.preview_samples == 3