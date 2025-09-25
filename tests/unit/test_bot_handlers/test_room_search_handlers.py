from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.room_search_handlers import (
    RoomSearchStates,
    format_room_results_russian,
    handle_room_search_command,
    process_room_search,
    process_room_search_with_number,
)
from src.models.participant import Department, Participant, Role


def test_format_room_results_russian_empty():
    result = format_room_results_russian([], "101")
    assert result == "❌ В комнате 101 участники не найдены."


def test_format_room_results_russian_structure():
    participants = [
        Participant(
            record_id="rec1",
            full_name_ru="Иван Иванов",
            full_name_en="Ivan Ivanov",
            role=Role.TEAM,
            department=Department.ADMINISTRATION,
            floor=2,
            room_number="201",
        ),
        Participant(
            record_id="rec2",
            full_name_ru="Пётр Петров",
            full_name_en="Pyotr Petrov",
            role=Role.CANDIDATE,
            department=Department.WORSHIP,
            floor=2,
            room_number="201",
        ),
    ]

    result = format_room_results_russian(participants, "201")
    assert "🏠 Найдено участников в комнате 201: 2" in result

    # First participant
    assert "1. Иван Иванов (Ivan Ivanov)" in result
    assert "Роль: Команда" in result
    assert "Департамент: Администрация" in result
    assert "Этаж: 2" in result

    # Second participant
    assert "2. Пётр Петров (Pyotr Petrov)" in result
    assert "Роль: Кандидат" in result
    assert "Департамент: Прославление" in result


class TestRoomSearchHandlersAuthorization:
    """Test authorization controls for room search handlers."""

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.fixture
    def mock_unauthorized_update(self):
        """Mock update with unauthorized user."""
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 999999
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        update.message.text = "/search_room 101"
        return update

    @pytest.fixture
    def mock_authorized_update(self):
        """Mock update with authorized user."""
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        update.message.text = "/search_room 101"
        return update

    @pytest.mark.asyncio
    async def test_handle_room_search_command_denies_unauthorized_user(
        self, mock_unauthorized_update, mock_context
    ):
        """Test room search command denies access to unauthorized users."""
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = None

            result = await handle_room_search_command(
                mock_unauthorized_update, mock_context
            )

            # Should deny access
            mock_unauthorized_update.message.reply_text.assert_called_once()
            call_args = mock_unauthorized_update.message.reply_text.call_args
            message_text = call_args[0][0]  # First positional argument
            assert "❌" in message_text
            assert "комнат" in message_text.lower()
            assert result is None

    @pytest.mark.asyncio
    async def test_handle_room_search_command_allows_authorized_user(
        self, mock_authorized_update, mock_context
    ):
        """Test room search command allows access to authorized users."""
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            with patch(
                "src.services.service_factory.get_search_service"
            ) as mock_get_service:
                mock_get_role.return_value = "viewer"
                mock_service = Mock()
                mock_service.search_by_room.return_value = []
                mock_get_service.return_value = mock_service

                result = await handle_room_search_command(
                    mock_authorized_update, mock_context
                )

                # Should allow access and proceed
                assert result == RoomSearchStates.SHOWING_ROOM_RESULTS

    @pytest.mark.asyncio
    async def test_process_room_search_denies_unauthorized_user(
        self, mock_unauthorized_update, mock_context
    ):
        """Test process room search denies access to unauthorized users."""
        mock_unauthorized_update.message.text = "101"
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = None

            result = await process_room_search(mock_unauthorized_update, mock_context)

            # Should deny access
            mock_unauthorized_update.message.reply_text.assert_called_once()
            call_args = mock_unauthorized_update.message.reply_text.call_args
            message_text = call_args[0][0]
            assert "❌" in message_text
            assert "комнат" in message_text.lower()
            assert result is None

    @pytest.mark.asyncio
    async def test_process_room_search_with_number_denies_unauthorized_user(
        self, mock_unauthorized_update, mock_context
    ):
        """Test process room search with number denies access to unauthorized users."""
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = None

            result = await process_room_search_with_number(
                mock_unauthorized_update, mock_context, "101"
            )

            # Should deny access
            mock_unauthorized_update.message.reply_text.assert_called_once()
            call_args = mock_unauthorized_update.message.reply_text.call_args
            message_text = call_args[0][0]
            assert "❌" in message_text
            assert "комнат" in message_text.lower()
            assert result is None
