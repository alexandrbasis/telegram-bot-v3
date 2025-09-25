"""
Tests for user interaction logging integration in edit participant handlers.

This test module verifies that all callback_query handlers in the edit participant
flow properly log user interactions, bot responses, and error scenarios.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import CallbackQuery, InlineKeyboardMarkup, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.edit_participant_handlers import (
    EditStates,
    cancel_editing,
    get_user_interaction_logger,
    handle_button_field_selection,
    handle_field_edit_selection,
    retry_save,
    save_changes,
    show_save_confirmation,
)
from src.models.participant import Gender, Participant, Size


@pytest.fixture
def mock_update():
    """Create a mock Telegram update with callback query."""
    update = MagicMock(spec=Update)
    update.callback_query = MagicMock(spec=CallbackQuery)
    update.callback_query.answer = AsyncMock()
    update.callback_query.from_user = MagicMock(spec=User)
    update.callback_query.from_user.id = 12345
    update.callback_query.from_user.username = "testuser"
    update.callback_query.message = MagicMock(spec=Message)
    update.callback_query.message.edit_text = AsyncMock()
    update.callback_query.data = "test_data"
    return update


@pytest.fixture
def mock_context():
    """Create a mock bot context with user data."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {
        "current_participant": MagicMock(spec=Participant),
        "editing_changes": {"gender": Gender.MALE},
        "editing_field": "gender",
    }
    return context


@pytest.fixture
def mock_user_logger():
    """Create a mock user interaction logger."""
    logger = MagicMock()
    logger.log_button_click = MagicMock()
    logger.log_bot_response = MagicMock()
    logger.log_missing_response = MagicMock()
    return logger


class TestEditHandlerLoggingIntegration:
    """Test user interaction logging integration in edit handlers."""

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.edit_participant_handlers.show_field_button_selection")
    async def test_handle_field_edit_selection_button_field_logging(
        self,
        mock_show_button,
        mock_get_logger,
        mock_update,
        mock_context,
        mock_user_logger,
    ):
        """Test logging in handle_field_edit_selection for button fields."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_show_button.return_value = EditStates.BUTTON_SELECTION
        mock_update.callback_query.data = "edit_field:gender"

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await handle_field_edit_selection(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="edit_field:gender", username="testuser"
        )

        # Verify bot response logging
        mock_user_logger.log_bot_response.assert_called_once_with(
            user_id=12345,
            response_type="edit_message",
            content="Field button selection for gender",
            keyboard_info="Button options for field: gender",
        )

        # Verify state transition
        assert result == EditStates.BUTTON_SELECTION

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.edit_participant_handlers.show_field_text_prompt")
    async def test_handle_field_edit_selection_text_field_logging(
        self,
        mock_show_text,
        mock_get_logger,
        mock_update,
        mock_context,
        mock_user_logger,
    ):
        """Test logging in handle_field_edit_selection for text fields."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_show_text.return_value = EditStates.TEXT_INPUT
        mock_update.callback_query.data = "edit_field:full_name_ru"

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await handle_field_edit_selection(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="edit_field:full_name_ru", username="testuser"
        )

        # Verify bot response logging
        mock_user_logger.log_bot_response.assert_called_once_with(
            user_id=12345,
            response_type="edit_message",
            content="Text input prompt for full_name_ru",
            keyboard_info="Cancel button",
        )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    async def test_handle_field_edit_selection_unknown_field_logging(
        self, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test logging for unknown field error scenario."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.data = "edit_field:unknown_field"

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await handle_field_edit_selection(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="edit_field:unknown_field", username="testuser"
        )

        # Verify missing response logging
        mock_user_logger.log_missing_response.assert_called_once_with(
            user_id=12345,
            expected_action="field_edit_selection",
            error_context="Unknown field type: unknown_field",
        )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.edit_participant_handlers.ParticipantUpdateService")
    @patch(
        "src.bot.handlers.edit_participant_handlers.create_participant_edit_keyboard"
    )
    async def test_handle_button_field_selection_success_logging(
        self,
        mock_keyboard,
        mock_service,
        mock_get_logger,
        mock_update,
        mock_context,
        mock_user_logger,
    ):
        """Test logging in handle_button_field_selection for successful selection."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.data = "select_value:male"
        mock_context.user_data["editing_field"] = "gender"

        service_instance = MagicMock()
        service_instance.convert_button_value.return_value = Gender.MALE
        service_instance.get_russian_display_value.return_value = "Мужской"
        mock_service.return_value = service_instance

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await handle_button_field_selection(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="select_value:male", username="testuser"
        )

        # Verify bot response logging
        mock_user_logger.log_bot_response.assert_called_once_with(
            user_id=12345,
            response_type="edit_message",
            content="Field gender updated to Мужской",
            keyboard_info="Participant edit menu",
        )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    async def test_handle_button_field_selection_no_field_logging(
        self, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test logging when no editing field is set."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_context.user_data["editing_field"] = None

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await handle_button_field_selection(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="test_data", username="testuser"
        )

        # Verify missing response logging
        mock_user_logger.log_missing_response.assert_called_once_with(
            user_id=12345,
            expected_action="button_field_selection",
            error_context="No editing field set in context",
        )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.search_handlers.get_results_navigation_keyboard")
    async def test_cancel_editing_logging(
        self,
        mock_keyboard,
        mock_get_logger,
        mock_update,
        mock_context,
        mock_user_logger,
    ):
        """Test logging in cancel_editing handler."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.data = "cancel_edit"

        # Execute
        from src.bot.handlers.search_handlers import SearchStates

        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await cancel_editing(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="cancel_edit", username="testuser"
        )

        # Verify bot response logging
        mock_user_logger.log_bot_response.assert_called_once_with(
            user_id=12345,
            response_type="edit_message",
            content="Editing cancelled",
            keyboard_info="Search results keyboard",
        )

        # Verify state transition
        assert result == SearchStates.SHOWING_RESULTS

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    async def test_show_save_confirmation_with_changes_logging(
        self, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test logging in show_save_confirmation with pending changes."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.data = "save_confirmation"
        mock_context.user_data["editing_changes"] = {
            "gender": Gender.MALE,
            "size": Size.M,
        }

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await show_save_confirmation(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="save_confirmation", username="testuser"
        )

        # Verify bot response logging
        mock_user_logger.log_bot_response.assert_called_once_with(
            user_id=12345,
            response_type="edit_message",
            content="Save confirmation for 2 changes",
            keyboard_info="Save/Cancel confirmation buttons",
        )

        # Verify state transition
        assert result == EditStates.CONFIRMATION

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.edit_participant_handlers.get_participant_repository")
    async def test_save_changes_success_logging(
        self, mock_repo, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test logging in save_changes for successful save."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.data = "confirm_save"
        mock_context.user_data["editing_changes"] = {"gender": Gender.MALE}
        mock_context.user_data["current_participant"] = MagicMock()
        mock_context.user_data["current_participant"].record_id = "rec123"

        repo_instance = MagicMock()
        repo_instance.update_by_id = AsyncMock(return_value=True)
        mock_repo.return_value = repo_instance

        # Execute
        from src.bot.handlers.search_handlers import SearchStates

        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await save_changes(mock_update, mock_context)

        # Verify button click logging
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="confirm_save", username="testuser"
        )

        # Verify successful save response logging
        mock_user_logger.log_bot_response.assert_called_once_with(
            user_id=12345,
            response_type="edit_message",
            content="Changes saved successfully: 1 fields updated",
            keyboard_info="Main menu button",
        )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.edit_participant_handlers.get_participant_repository")
    async def test_save_changes_failure_logging(
        self, mock_repo, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test logging in save_changes for failed save."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_context.user_data["editing_changes"] = {"gender": Gender.MALE}
        mock_context.user_data["current_participant"] = MagicMock()
        mock_context.user_data["current_participant"].record_id = "rec123"

        repo_instance = MagicMock()
        repo_instance.update_by_id = AsyncMock(return_value=False)
        mock_repo.return_value = repo_instance

        # Execute
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "coordinator"
            result = await save_changes(mock_update, mock_context)

        # Verify missing response logging for failed save
        mock_user_logger.log_missing_response.assert_called_once_with(
            user_id=12345,
            expected_action="save_changes",
            error_context="Save operation failed",
        )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    async def test_retry_save_logging(
        self, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test logging in retry_save handler."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.data = "retry_save"

        # Mock save_changes to avoid full execution
        with patch(
            "src.bot.handlers.edit_participant_handlers.save_changes"
        ) as mock_save:
            mock_save.return_value = MagicMock()

            # Execute
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "coordinator"
                result = await retry_save(mock_update, mock_context)

            # Verify button click logging
            mock_user_logger.log_button_click.assert_called_once_with(
                user_id=12345, button_data="retry_save", username="testuser"
            )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    async def test_logging_disabled_no_calls(
        self, mock_get_logger, mock_update, mock_context
    ):
        """Test that no logging calls are made when logging is disabled."""
        # Setup - logging disabled
        mock_get_logger.return_value = None
        mock_update.callback_query.data = "cancel_edit"

        # Execute
        with patch("src.bot.handlers.search_handlers.get_results_navigation_keyboard"):
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "coordinator"
                result = await cancel_editing(mock_update, mock_context)

        # Verify no logging calls were made since logger is None
        # This test passes if no AttributeError is raised

    @pytest.mark.asyncio
    @patch("src.bot.handlers.edit_participant_handlers.get_user_interaction_logger")
    async def test_username_none_handling(
        self, mock_get_logger, mock_update, mock_context, mock_user_logger
    ):
        """Test handling of users without username."""
        # Setup
        mock_get_logger.return_value = mock_user_logger
        mock_update.callback_query.from_user.username = None
        mock_update.callback_query.data = "cancel_edit"

        # Execute
        with patch("src.bot.handlers.search_handlers.get_results_navigation_keyboard"):
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "coordinator"
                result = await cancel_editing(mock_update, mock_context)

        # Verify button click logging with None username
        mock_user_logger.log_button_click.assert_called_once_with(
            user_id=12345, button_data="cancel_edit", username=None
        )
