"""
Integration tests for payment automation workflow.

Tests the complete payment automation flow:
1. User enters payment amount >= 1
2. System automatically sets payment_status=PAID and payment_date=today()
3. Changes are saved to repository with automated fields
"""

from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import CallbackQuery, Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.edit_participant_handlers import (
    handle_text_field_input, save_changes)
from src.data.repositories.participant_repository import RepositoryError
from src.models.participant import Participant, PaymentStatus


class TestPaymentAutomationWorkflow:
    """Integration tests for payment automation workflow."""

    @pytest.fixture
    def mock_user(self):
        """Mock Telegram user."""
        user = Mock(spec=User)
        user.id = 12345
        user.first_name = "Test"
        user.username = "testuser"
        return user

    @pytest.fixture
    def mock_chat(self):
        """Mock Telegram chat."""
        chat = Mock(spec=Chat)
        chat.id = 12345
        chat.type = "private"
        return chat

    @pytest.fixture
    def mock_message(self, mock_chat):
        """Mock Telegram message."""
        message = Mock(spec=Message)
        message.message_id = 1
        message.chat = mock_chat
        message.edit_text = AsyncMock()
        return message

    @pytest.fixture
    def mock_callback_query(self, mock_user, mock_message):
        """Mock callback query for button interactions."""
        query = Mock(spec=CallbackQuery)
        query.from_user = mock_user
        query.message = mock_message
        query.data = "save_changes"
        query.answer = AsyncMock()
        return query

    @pytest.fixture
    def mock_update(self, mock_callback_query):
        """Mock Telegram update."""
        update = Mock(spec=Update)
        update.callback_query = mock_callback_query
        return update

    @pytest.fixture
    def mock_context(self):
        """Mock bot context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.fixture
    def sample_participant(self):
        """Sample participant for testing."""
        return Participant(
            record_id="rec123test",
            full_name_ru="Тест Тестович",
            full_name_en="Test Testovich",
            payment_amount=0,
            payment_status=PaymentStatus.UNPAID,
            payment_date=None,
        )

    @pytest.mark.asyncio
    async def test_payment_automation_triggers_on_paid_amount(
        self, mock_update, mock_context, sample_participant
    ):
        """Test that payment automation triggers when payment_amount >= 1."""
        # Setup: participant with payment amount change
        mock_context.user_data["current_participant"] = sample_participant
        mock_context.user_data["editing_changes"] = {"payment_amount": 1500}

        with (
            patch(
                "src.bot.handlers.edit_participant_handlers.get_participant_repository"
            ) as mock_get_repo,
            patch(
                "src.bot.handlers.edit_participant_handlers.get_user_interaction_logger"
            ) as mock_logger,
        ):

            # Setup repository mock
            mock_repo = AsyncMock()
            mock_repo.update_by_id.return_value = True
            mock_get_repo.return_value = mock_repo
            mock_logger.return_value = None

            # Execute save_changes
            await save_changes(mock_update, mock_context)

            # Verify automated fields were added to the update
            expected_update = {
                "payment_amount": 1500,
                "payment_status": PaymentStatus.PAID,
                "payment_date": date.today(),
            }
            mock_repo.update_by_id.assert_called_once_with(
                sample_participant.record_id, expected_update
            )

    @pytest.mark.asyncio
    async def test_payment_automation_does_not_trigger_on_zero_amount(
        self, mock_update, mock_context, sample_participant
    ):
        """Test that payment automation does not trigger when payment_amount = 0."""
        # Setup: participant with zero payment amount
        mock_context.user_data["current_participant"] = sample_participant
        mock_context.user_data["editing_changes"] = {"payment_amount": 0}

        with (
            patch(
                "src.bot.handlers.edit_participant_handlers.get_participant_repository"
            ) as mock_get_repo,
            patch(
                "src.bot.handlers.edit_participant_handlers.get_user_interaction_logger"
            ) as mock_logger,
        ):

            # Setup repository mock
            mock_repo = AsyncMock()
            mock_repo.update_by_id.return_value = True
            mock_get_repo.return_value = mock_repo
            mock_logger.return_value = None

            # Execute save_changes
            await save_changes(mock_update, mock_context)

            # Verify only payment_amount is updated, no automation
            expected_update = {"payment_amount": 0}
            mock_repo.update_by_id.assert_called_once_with(
                sample_participant.record_id, expected_update
            )

    @pytest.mark.asyncio
    async def test_payment_automation_does_not_trigger_without_payment_field(
        self, mock_update, mock_context, sample_participant
    ):
        """Test that payment automation does not trigger when payment_amount is not being changed."""
        # Setup: participant with other field changes
        mock_context.user_data["current_participant"] = sample_participant
        mock_context.user_data["editing_changes"] = {"full_name_ru": "Новое Имя"}

        with (
            patch(
                "src.bot.handlers.edit_participant_handlers.get_participant_repository"
            ) as mock_get_repo,
            patch(
                "src.bot.handlers.edit_participant_handlers.get_user_interaction_logger"
            ) as mock_logger,
        ):

            # Setup repository mock
            mock_repo = AsyncMock()
            mock_repo.update_by_id.return_value = True
            mock_get_repo.return_value = mock_repo
            mock_logger.return_value = None

            # Execute save_changes
            await save_changes(mock_update, mock_context)

            # Verify only intended field is updated, no automation
            expected_update = {"full_name_ru": "Новое Имя"}
            mock_repo.update_by_id.assert_called_once_with(
                sample_participant.record_id, expected_update
            )

    @pytest.mark.asyncio
    async def test_payment_automation_with_multiple_fields(
        self, mock_update, mock_context, sample_participant
    ):
        """Test that payment automation works correctly with multiple field changes."""
        # Setup: participant with multiple changes including payment
        mock_context.user_data["current_participant"] = sample_participant
        mock_context.user_data["editing_changes"] = {
            "full_name_ru": "Обновленное Имя",
            "payment_amount": 2000,
            "contact_information": "новый@email.com",
        }

        with (
            patch(
                "src.bot.handlers.edit_participant_handlers.get_participant_repository"
            ) as mock_get_repo,
            patch(
                "src.bot.handlers.edit_participant_handlers.get_user_interaction_logger"
            ) as mock_logger,
        ):

            # Setup repository mock
            mock_repo = AsyncMock()
            mock_repo.update_by_id.return_value = True
            mock_get_repo.return_value = mock_repo
            mock_logger.return_value = None

            # Execute save_changes
            await save_changes(mock_update, mock_context)

            # Verify all fields plus automated fields are updated
            expected_update = {
                "full_name_ru": "Обновленное Имя",
                "payment_amount": 2000,
                "contact_information": "новый@email.com",
                "payment_status": PaymentStatus.PAID,
                "payment_date": date.today(),
            }
            mock_repo.update_by_id.assert_called_once_with(
                sample_participant.record_id, expected_update
            )

    @pytest.mark.asyncio
    async def test_payment_automation_edge_case_amount_equals_one(
        self, mock_update, mock_context, sample_participant
    ):
        """Test that payment automation triggers when payment_amount = 1 (edge case)."""
        # Setup: participant with minimum triggering amount
        mock_context.user_data["current_participant"] = sample_participant
        mock_context.user_data["editing_changes"] = {"payment_amount": 1}

        with (
            patch(
                "src.bot.handlers.edit_participant_handlers.get_participant_repository"
            ) as mock_get_repo,
            patch(
                "src.bot.handlers.edit_participant_handlers.get_user_interaction_logger"
            ) as mock_logger,
        ):

            # Setup repository mock
            mock_repo = AsyncMock()
            mock_repo.update_by_id.return_value = True
            mock_get_repo.return_value = mock_repo
            mock_logger.return_value = None

            # Execute save_changes
            await save_changes(mock_update, mock_context)

            # Verify automation triggers for amount = 1
            expected_update = {
                "payment_amount": 1,
                "payment_status": PaymentStatus.PAID,
                "payment_date": date.today(),
            }
            mock_repo.update_by_id.assert_called_once_with(
                sample_participant.record_id, expected_update
            )

    @pytest.mark.asyncio
    async def test_payment_automation_logging(
        self, mock_update, mock_context, sample_participant, caplog
    ):
        """Test that payment automation is properly logged."""
        # Setup: participant with payment amount change
        mock_context.user_data["current_participant"] = sample_participant
        mock_context.user_data["editing_changes"] = {"payment_amount": 1500}

        with (
            patch(
                "src.bot.handlers.edit_participant_handlers.get_participant_repository"
            ) as mock_get_repo,
            patch(
                "src.bot.handlers.edit_participant_handlers.get_user_interaction_logger"
            ) as mock_logger,
        ):

            # Setup repository mock
            mock_repo = AsyncMock()
            mock_repo.update_by_id.return_value = True
            mock_get_repo.return_value = mock_repo
            mock_logger.return_value = None

            # Capture logs at INFO level
            caplog.set_level("INFO")

            # Execute save_changes
            await save_changes(mock_update, mock_context)

            # Verify payment automation was logged
            assert "Payment automation triggered" in caplog.text
            assert "amount=1500" in caplog.text
            assert str(PaymentStatus.PAID) in caplog.text
