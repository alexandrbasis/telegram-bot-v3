"""
Integration tests for room search functionality.

Tests complete room search workflow from command to response,
including Airtable integration and error scenarios.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.room_search_handlers import (
    RoomSearchStates,
    handle_room_search_command,
    process_room_search,
    process_room_search_with_number,
)
from src.models.participant import Department, Participant, Role
from src.services.service_factory import get_search_service


class TestRoomSearchIntegration:
    """Integration tests for room search end-to-end workflows."""

    @pytest.fixture
    def mock_update_and_context(self):
        """Create mock Update and Context for testing."""
        # Create mock user
        user = Mock(spec=User)
        user.id = 12345
        user.first_name = "Test"

        # Create mock chat
        chat = Mock(spec=Chat)
        chat.id = 67890

        # Create mock message
        message = Mock(spec=Message)
        message.reply_text = AsyncMock()
        message.text = ""

        # Create mock update
        update = Mock(spec=Update)
        update.effective_user = user
        update.effective_chat = chat
        update.message = message

        # Create mock context
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}

        return update, context

    @pytest.fixture
    def sample_participants(self):
        """Create sample participant data for testing."""
        return [
            Participant(
                record_id="rec001",
                full_name_ru="Иван Петров",
                full_name_en="Ivan Petrov",
                nickname="Vanya",
                role=Role.TEAM,
                department=Department.ADMINISTRATION,
                floor=2,
                room_number="201",
            ),
            Participant(
                record_id="rec002",
                full_name_ru="Мария Сидорова",
                full_name_en="Maria Sidorova",
                nickname="Masha",
                role=Role.CANDIDATE,
                department=Department.WORSHIP,
                floor=2,
                room_number="201",
            ),
        ]

    @pytest.mark.asyncio
    async def test_room_search_command_with_valid_room_success(
        self, mock_update_and_context, sample_participants
    ):
        """Test successful room search with room number in command."""
        update, context = mock_update_and_context
        update.message.text = "/search_room 201"

        # Mock search service to return participants
        with patch(
            "src.bot.handlers.room_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_room = AsyncMock(return_value=sample_participants)
            mock_get_service.return_value = mock_service

            # Execute room search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                result_state = await handle_room_search_command(update, context)

            # Verify service calls
            mock_service.search_by_room.assert_called_once_with("201")

            # Verify response sent to user
            assert update.message.reply_text.call_count == 2  # Loading + results

            # Check loading message
            loading_call = update.message.reply_text.call_args_list[0]
            assert "🔍 Ищу участников в комнате 201" in loading_call[1]["text"]

            # Check results message and Russian details
            results_call = update.message.reply_text.call_args_list[1]
            text = results_call[1]["text"]
            assert "🏠 Найдено участников в комнате 201: 2" in text
            assert "Иван Петров" in text
            assert "Мария Сидорова" in text
            # Role and department in Russian
            assert "Роль: Команда" in text
            assert "Департамент: Администрация" in text
            assert "Роль: Кандидат" in text
            assert "Департамент: Прославление" in text
            # Floor present
            assert "Этаж: 2" in text

            # Verify context data stored
            assert context.user_data["room_search_results"] == sample_participants
            assert context.user_data["current_room"] == "201"

            # Verify correct state returned
            assert result_state == RoomSearchStates.SHOWING_ROOM_RESULTS

    @pytest.mark.asyncio
    async def test_room_search_command_without_room_prompts_input(
        self, mock_update_and_context
    ):
        """Test room search command without room number prompts for input."""
        update, context = mock_update_and_context
        update.message.text = "/search_room"

        # Execute room search with authorization mocking
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "viewer"
            result_state = await handle_room_search_command(update, context)

        # Verify prompt message sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "Введите номер комнаты для поиска:" in call_args[1]["text"]

        # Verify correct state returned
        assert result_state == RoomSearchStates.WAITING_FOR_ROOM

    @pytest.mark.asyncio
    async def test_room_search_with_invalid_room_number(self, mock_update_and_context):
        """Test room search with invalid room number (no digits)."""
        update, context = mock_update_and_context
        update.message.text = "ABC"

        # Execute room search processing with authorization mocking
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "viewer"
            result_state = await process_room_search(update, context)

        # Verify error message sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "❌ Пожалуйста, введите корректный номер комнаты" in call_args[1]["text"]

        # Verify state remains in waiting
        assert result_state == RoomSearchStates.WAITING_FOR_ROOM

    @pytest.mark.asyncio
    async def test_room_search_with_no_participants_found(
        self, mock_update_and_context
    ):
        """Test room search when no participants found."""
        update, context = mock_update_and_context
        update.message.text = "999"

        # Mock search service to return empty results
        with patch(
            "src.bot.handlers.room_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_room = AsyncMock(return_value=[])
            mock_get_service.return_value = mock_service

            # Execute room search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                result_state = await process_room_search(update, context)

            # Verify service calls
            mock_service.search_by_room.assert_called_once_with("999")

            # Verify no participants message sent
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args
            assert "❌ В комнате 999 участники не найдены." in call_args[1]["text"]

            # Verify correct state returned
            assert result_state == RoomSearchStates.SHOWING_ROOM_RESULTS

    @pytest.mark.asyncio
    async def test_room_search_with_api_error_handling(self, mock_update_and_context):
        """Test room search handles API errors gracefully."""
        update, context = mock_update_and_context
        update.message.text = "201"

        # Mock search service to raise exception
        with patch(
            "src.bot.handlers.room_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_room = AsyncMock(side_effect=Exception("API Error"))
            mock_get_service.return_value = mock_service

            # Execute room search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                result_state = await process_room_search(update, context)

            # Verify error message sent
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args
            assert (
                "❌ Произошла ошибка при поиске. Попробуйте позже."
                in call_args[1]["text"]
            )

            # Verify correct state returned
            assert result_state == RoomSearchStates.SHOWING_ROOM_RESULTS

    @pytest.mark.asyncio
    async def test_room_search_performance_under_3_seconds(
        self, mock_update_and_context, sample_participants
    ):
        """Test room search completes within performance target (3 seconds)."""
        update, context = mock_update_and_context
        update.message.text = "201"

        # Mock search service with realistic delay
        with patch(
            "src.bot.handlers.room_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()

            async def mock_search_delay(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate realistic API delay
                return sample_participants

            mock_service.search_by_room = mock_search_delay
            mock_get_service.return_value = mock_service

            # Measure execution time
            import time

            start_time = time.time()
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                result_state = await process_room_search(update, context)
            end_time = time.time()

            execution_time = end_time - start_time

            # Verify performance target met (< 3 seconds)
            assert (
                execution_time < 3.0
            ), f"Room search took {execution_time:.2f}s, exceeding 3s limit"

            # Verify successful completion
            assert result_state == RoomSearchStates.SHOWING_ROOM_RESULTS

    @pytest.mark.asyncio
    async def test_room_search_alphanumeric_room_number_support(
        self, mock_update_and_context, sample_participants
    ):
        """Test room search supports alphanumeric room numbers."""
        update, context = mock_update_and_context
        update.message.text = "A201"

        # Update sample data for alphanumeric room
        alphanumeric_participants = [
            Participant(
                record_id="rec003",
                full_name_ru="Алексей Кузнецов",
                full_name_en="Alexey Kuznetsov",
                nickname="Alex",
                role=Role.TEAM,
                department=Department.MEDIA,
                floor=2,
                room_number="A201",
            )
        ]

        # Mock search service
        with patch(
            "src.bot.handlers.room_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_room = AsyncMock(
                return_value=alphanumeric_participants
            )
            mock_get_service.return_value = mock_service

            # Execute room search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                result_state = await process_room_search(update, context)

            # Verify service calls with alphanumeric room
            mock_service.search_by_room.assert_called_once_with("A201")

            # Verify successful result
            assert result_state == RoomSearchStates.SHOWING_ROOM_RESULTS

            # Verify results contain alphanumeric room data
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args
            assert "🏠 Найдено участников в комнате A201: 1" in call_args[1]["text"]
            assert "Алексей Кузнецов" in call_args[1]["text"]
            assert "Роль: Команда" in call_args[1]["text"]
            assert "Департамент: Медиа" in call_args[1]["text"]
