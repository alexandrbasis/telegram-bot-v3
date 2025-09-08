"""
Unit tests for floor search bot handlers and conversation flow.

Tests bot handler functions for floor search functionality with ConversationHandler
state management and Russian interface with room-by-room breakdown.
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from telegram import (CallbackQuery, Chat, InlineKeyboardMarkup, Message,
                      ReplyKeyboardMarkup, Update, User)
from telegram.ext import ContextTypes

from src.bot.handlers.floor_search_handlers import (
    FloorSearchStates, handle_floor_search_command, process_floor_search)
from src.models.participant import Participant


class TestFloorSearchStates:
    """Test floor search conversation states enum."""

    def test_floor_search_states_values(self):
        """Test that floor search states have correct integer values."""
        assert FloorSearchStates.WAITING_FOR_FLOOR == 30
        assert FloorSearchStates.SHOWING_FLOOR_RESULTS == 31


class TestHandleFloorSearchCommand:
    """Test /search_floor command handler."""

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
        message.text = "/search_floor 2"
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
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_handle_floor_search_command_with_floor_number(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test /search_floor command with floor number."""
        # Mock search service
        mock_service = AsyncMock()
        mock_service.search_by_floor.return_value = [
            Participant(
                record_id="rec123",
                full_name_ru="Иван Петров",
                room_number="201",
                floor=2,
            ),
            Participant(
                record_id="rec456",
                full_name_ru="Мария Сидорова",
                room_number="205",
                floor=2,
            ),
        ]
        mock_get_service.return_value = mock_service

        # Test should process floor number directly
        result = await handle_floor_search_command(mock_update_message, mock_context)

        # Should transition to showing results
        assert result == FloorSearchStates.SHOWING_FLOOR_RESULTS

        # Should have called reply_text
        assert mock_update_message.message.reply_text.call_count >= 1

        # Check that search was initiated
        first_call = mock_update_message.message.reply_text.call_args_list[0][1]
        assert (
            "этаж" in first_call["text"].lower()
            or "найдено" in first_call["text"].lower()
        )

    @pytest.mark.asyncio
    async def test_handle_floor_search_command_without_floor_number(self, mock_context):
        """Test /search_floor command without floor number."""
        # Mock update with just /search_floor
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456789
        user.first_name = "TestUser"

        message.from_user = user
        message.text = "/search_floor"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        result = await handle_floor_search_command(update, mock_context)

        # Should ask for floor number
        assert result == FloorSearchStates.WAITING_FOR_FLOOR

        # Should reply with prompt for floor number
        message.reply_text.assert_called()
        call_args = message.reply_text.call_args[1]
        assert "номер этажа" in call_args["text"].lower()


class TestProcessFloorSearch:
    """Test floor search processing logic."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for message with floor number."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456789
        user.first_name = "TestUser"

        message.from_user = user
        message.text = "2"
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
    def sample_floor_participants(self):
        """Sample participants for floor 2 with different rooms."""
        return [
            Participant(
                record_id="rec123",
                full_name_ru="Иван Петров",
                full_name_en="Ivan Petrov",
                room_number="201",
                floor=2,
            ),
            Participant(
                record_id="rec456",
                full_name_ru="Мария Сидорова",
                full_name_en="Maria Sidorova",
                room_number="201",
                floor=2,
            ),
            Participant(
                record_id="rec789",
                full_name_ru="Алексей Иванов",
                full_name_en="Alexey Ivanov",
                room_number="205",
                floor=2,
            ),
        ]

    @pytest.mark.asyncio
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_process_floor_search_found_participants(
        self,
        mock_get_service,
        mock_update_message,
        mock_context,
        sample_floor_participants,
    ):
        """Test processing floor search with found participants grouped by room."""
        # Mock search service
        mock_service = AsyncMock()
        mock_service.search_by_floor.return_value = sample_floor_participants
        mock_get_service.return_value = mock_service

        result = await process_floor_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == FloorSearchStates.SHOWING_FLOOR_RESULTS

        # Should call search service with floor number
        mock_service.search_by_floor.assert_called_with(2)

        # Should store results in context
        assert len(mock_context.user_data["floor_search_results"]) == 3

        # Should send formatted results grouped by room
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        result_text = call_args["text"]
        assert "найдено участников" in result_text.lower()
        assert "комната 201" in result_text.lower()
        assert "комната 205" in result_text.lower()
        assert "иван петров" in result_text.lower()
        assert "мария сидорова" in result_text.lower()
        assert "алексей иванов" in result_text.lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_process_floor_search_no_participants(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test processing floor search with no participants found."""
        # Mock empty search results
        mock_service = AsyncMock()
        mock_service.search_by_floor.return_value = []
        mock_get_service.return_value = mock_service

        result = await process_floor_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == FloorSearchStates.SHOWING_FLOOR_RESULTS

        # Should send no results message
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        assert "не найдены" in call_args["text"].lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_process_floor_search_invalid_floor_number(
        self, mock_get_service, mock_context
    ):
        """Test processing floor search with invalid floor number."""
        # Mock update with non-numeric floor
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456789
        message.from_user = user
        message.text = "abc"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        result = await process_floor_search(update, mock_context)

        # Should return waiting for floor state
        assert result == FloorSearchStates.WAITING_FOR_FLOOR

        # Should send error message
        message.reply_text.assert_called()
        call_args = message.reply_text.call_args[1]
        assert "номер этажа" in call_args["text"].lower()
        assert (
            "число" in call_args["text"].lower() or "цифры" in call_args["text"].lower()
        )

        # Should not call search service
        mock_get_service.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_process_floor_search_service_error(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test handling search service error."""
        # Mock service error
        mock_service = AsyncMock()
        mock_service.search_by_floor.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service

        result = await process_floor_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == FloorSearchStates.SHOWING_FLOOR_RESULTS

        # Should send error message
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        assert "ошибка" in call_args["text"].lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_process_floor_search_room_grouping(
        self, mock_get_service, mock_update_message, mock_context
    ):
        """Test that floor search results are properly grouped by room."""
        # Mock participants in different rooms
        participants = [
            Participant(
                record_id="rec1", full_name_ru="Участник 1", room_number="201", floor=2
            ),
            Participant(
                record_id="rec2", full_name_ru="Участник 2", room_number="201", floor=2
            ),
            Participant(
                record_id="rec3", full_name_ru="Участник 3", room_number="205", floor=2
            ),
        ]

        mock_service = AsyncMock()
        mock_service.search_by_floor.return_value = participants
        mock_get_service.return_value = mock_service

        result = await process_floor_search(mock_update_message, mock_context)

        # Should return showing results state
        assert result == FloorSearchStates.SHOWING_FLOOR_RESULTS

        # Should format results with room grouping
        mock_update_message.message.reply_text.assert_called()
        call_args = mock_update_message.message.reply_text.call_args[1]
        result_text = call_args["text"]

        # Should show room headers
        assert "комната 201" in result_text.lower()
        assert "комната 205" in result_text.lower()

        # Should show participants under correct rooms
        lines = result_text.split("\n")
        room_201_index = next(
            i for i, line in enumerate(lines) if "комната 201" in line.lower()
        )
        room_205_index = next(
            i for i, line in enumerate(lines) if "комната 205" in line.lower()
        )

        # Room 201 should come before room 205 (sorted order)
        assert room_201_index < room_205_index
