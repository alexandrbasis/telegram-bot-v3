"""
Unit tests for room search bot handlers and conversation flow.

Tests bot handler functions for room search functionality with ConversationHandler
state management and Russian interface.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import (
    Update,
    CallbackQuery,
    Message,
    User,
    Chat,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes

from src.bot.handlers.room_search_handlers import (
    process_room_search,
    handle_room_search_command,
    RoomSearchStates,
)
from src.models.participant import Participant


class TestRoomSearchStates:
    """Test room search conversation states enum."""

    def test_room_search_states_values(self):
        """Test that room search states have correct integer values."""
        assert RoomSearchStates.WAITING_FOR_ROOM == 20
        assert RoomSearchStates.SHOWING_ROOM_RESULTS == 21


class TestHandleRoomSearchCommand:
    """Test /search_room command handler."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for message."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        chat = Mock(spec=Chat)

        user.id = 123456789
        user.first_name = "TestUser"
        user.username = "testuser"

        chat.id = 123456789
        chat.type = "private"

        message.from_user = user
        message.chat = chat
        message.text = "/search_room 205"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock ContextTypes.DEFAULT_TYPE."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    @patch("src.bot.handlers.room_search_handlers.get_search_service")
    async def test_handle_room_search_command_with_room_number(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test /search_room command with room number."""
        # Mock search service
        mock_service = AsyncMock()
        mock_service.search_by_room_formatted.return_value = [
            "1. Иван Петров (Ivan Petrov) - Этаж: 2, Комната: 205"
        ]
        mock_service.search_by_room.return_value = [
            Participant(
                record_id="rec123", full_name_ru="Иван Петров", room="205", floor=2
            )
        ]
        mock_get_service.return_value = mock_service

        # Test should process room number directly
        result = await handle_room_search_command(mock_update_message, mock_context)

        # Should transition to showing results
        assert result == RoomSearchStates.SHOWING_ROOM_RESULTS

        # Should have called reply_text twice (processing + results)
        assert mock_update_message.message.reply_text.call_count >= 1

        # Check that search was initiated (first call should contain search indication)
        first_call = mock_update_message.message.reply_text.call_args_list[0][1]
        assert (
            "ищу" in first_call["text"].lower()
            or "найдено" in first_call["text"].lower()
        )

    @pytest.mark.asyncio
    async def test_handle_room_search_command_without_room_number(self, mock_context):
        """Test /search_room command without room number."""
        # Mock update with just /search_room
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456789
        user.first_name = "TestUser"

        message.from_user = user
        message.text = "/search_room"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        result = await handle_room_search_command(update, mock_context)

        # Should ask for room number
        assert result == RoomSearchStates.WAITING_FOR_ROOM

        # Should reply with prompt for room number
        message.reply_text.assert_called()
        call_args = message.reply_text.call_args[1]
        assert "номер комнаты" in call_args["text"].lower()


class TestProcessRoomSearch:
    """Test room search processing logic."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for message with room number."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456789
        user.first_name = "TestUser"

        message.from_user = user
        message.text = "205"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock ContextTypes.DEFAULT_TYPE."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.fixture
    def sample_participants(self):
        """Sample participants for room 205."""
        return [
            Participant(
                record_id="rec123",
                full_name_ru="Иван Петров",
                full_name_en="Ivan Petrov",
                room="205",
                floor=2,
            ),
            Participant(
                record_id="rec456",
                full_name_ru="Мария Сидорова",
                full_name_en="Maria Sidorova",
                room="205",
                floor=2,
            ),
        ]

    @pytest.mark.asyncio
    @patch("src.bot.handlers.room_search_handlers.get_search_service")
    async def test_process_room_search_found_participants(
        self, mock_get_service, mock_update_message, mock_context, sample_participants
    ):
        """Test processing room search with found participants."""
        # Mock search service
        mock_service = AsyncMock()
        mock_service.search_by_room_formatted.return_value = [
            "1. Иван Петров (Ivan Petrov) - Этаж: 2, Комната: 205",
            "2. Мария Сидорова (Maria Sidorova) - Этаж: 2, Комната: 205",
        ]
        mock_service.search_by_room.return_value = sample_participants
        mock_get_service.return_value = mock_service

        result = await process_room_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == RoomSearchStates.SHOWING_ROOM_RESULTS

        # Should call search service with room number
        mock_service.search_by_room_formatted.assert_called_with("205", language="ru")
        mock_service.search_by_room.assert_called_with("205")

        # Should store results in context
        assert len(mock_context.user_data["room_search_results"]) == 2

        # Should send formatted results
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        result_text = call_args["text"]
        assert "Найдено участников" in result_text
        assert "Иван Петров" in result_text
        assert "Мария Сидорова" in result_text

    @pytest.mark.asyncio
    @patch("src.bot.handlers.room_search_handlers.get_search_service")
    async def test_process_room_search_no_participants(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test processing room search with no participants found."""
        # Mock empty search results
        mock_service = AsyncMock()
        mock_service.search_by_room_formatted.return_value = []
        mock_service.search_by_room.return_value = []
        mock_get_service.return_value = mock_service

        result = await process_room_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == RoomSearchStates.SHOWING_ROOM_RESULTS

        # Should send no results message
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        assert "не найдены" in call_args["text"].lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.room_search_handlers.get_search_service")
    async def test_process_room_search_invalid_room_number(
        self, mock_get_service, mock_context
    ):
        """Test processing room search with invalid room number."""
        # Mock update with non-numeric room
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456789
        message.from_user = user
        message.text = "abc"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        result = await process_room_search(update, mock_context)

        # Should return waiting for room state
        assert result == RoomSearchStates.WAITING_FOR_ROOM

        # Should send error message
        message.reply_text.assert_called()
        call_args = message.reply_text.call_args[1]
        assert "номер комнаты" in call_args["text"].lower()
        assert (
            "цифры" in call_args["text"].lower() or "число" in call_args["text"].lower()
        )

        # Should not call search service
        mock_get_service.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.room_search_handlers.get_search_service")
    async def test_process_room_search_service_error(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test handling search service error."""
        # Mock service error
        mock_service = AsyncMock()
        mock_service.search_by_room_formatted.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service

        result = await process_room_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == RoomSearchStates.SHOWING_ROOM_RESULTS

        # Should send error message
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        assert "ошибка" in call_args["text"].lower()
