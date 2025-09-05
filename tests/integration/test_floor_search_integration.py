"""
Integration tests for floor search functionality.

Tests complete floor search workflow from command to response,
including room grouping, Airtable integration and error scenarios.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from src.bot.handlers.floor_search_handlers import (
    handle_floor_search_command,
    process_floor_search,
    process_floor_search_with_input,
    format_floor_results,
    FloorSearchStates,
)
from src.services.service_factory import get_search_service
from src.models.participant import Participant


class TestFloorSearchIntegration:
    """Integration tests for floor search end-to-end workflows."""

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
    def multi_room_floor_participants(self):
        """Create sample participants on same floor in different rooms."""
        return [
            Participant(
                record_id="rec001",
                full_name_ru="Иван Петров",
                full_name_en="Ivan Petrov",
                nickname="Vanya",
                floor=2,
                room_number="201",
            ),
            Participant(
                record_id="rec002",
                full_name_ru="Мария Сидорова",
                full_name_en="Maria Sidorova",
                nickname="Masha",
                floor=2,
                room_number="201",
            ),
            Participant(
                record_id="rec003",
                full_name_ru="Алексей Кузнецов",
                full_name_en="Alexey Kuznetsov",
                nickname="Alex",
                floor=2,
                room_number="202",
            ),
            Participant(
                record_id="rec004",
                full_name_ru="Елена Васильева",
                full_name_en="Elena Vasilyeva",
                nickname="Lena",
                floor=2,
                room_number="202",
            ),
            Participant(
                record_id="rec005",
                full_name_ru="Дмитрий Орлов",
                full_name_en="Dmitry Orlov",
                nickname="Dima",
                floor=2,
                room_number="203",
            ),
        ]

    @pytest.mark.asyncio
    async def test_floor_search_command_with_valid_floor_success(
        self, mock_update_and_context, multi_room_floor_participants
    ):
        """Test successful floor search with floor number in command."""
        update, context = mock_update_and_context
        update.message.text = "/search_floor 2"

        # Mock search service to return participants
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(
                return_value=multi_room_floor_participants
            )
            mock_get_service.return_value = mock_service

            # Execute floor search
            result_state = await handle_floor_search_command(update, context)

            # Verify service call
            mock_service.search_by_floor.assert_called_once_with(2)

            # Verify response sent to user
            assert update.message.reply_text.call_count == 2  # Loading + results

            # Check loading message
            loading_call = update.message.reply_text.call_args_list[0]
            assert "🔍 Ищу участников на этаже 2" in loading_call[1]["text"]

            # Check results message with room grouping
            results_call = update.message.reply_text.call_args_list[1]
            results_text = results_call[1]["text"]

            assert "🏢 Найдено участников на этаже 2: 5" in results_text
            assert "🚪 Комната 201:" in results_text
            assert "🚪 Комната 202:" in results_text
            assert "🚪 Комната 203:" in results_text
            assert "Иван Петров" in results_text
            assert "Мария Сидорова" in results_text
            assert "Алексей Кузнецов" in results_text
            assert "Елена Васильева" in results_text
            assert "Дмитрий Орлов" in results_text

            # Verify context data stored
            assert (
                context.user_data["floor_search_results"]
                == multi_room_floor_participants
            )
            assert (
                context.user_data["current_floor"] == "2"
            )  # Stored as string from command parsing

            # Verify correct state returned
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

    @pytest.mark.asyncio
    async def test_floor_search_command_without_floor_prompts_input(
        self, mock_update_and_context
    ):
        """Test floor search command without floor number prompts for input."""
        update, context = mock_update_and_context
        update.message.text = "/search_floor"

        # Execute floor search
        result_state = await handle_floor_search_command(update, context)

        # Verify prompt message sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "Введите номер этажа для поиска:" in call_args[1]["text"]

        # Verify correct state returned
        assert result_state == FloorSearchStates.WAITING_FOR_FLOOR

    @pytest.mark.asyncio
    async def test_floor_search_with_invalid_floor_number(
        self, mock_update_and_context
    ):
        """Test floor search with invalid floor number (non-numeric)."""
        update, context = mock_update_and_context
        update.message.text = "ABC"

        # Execute floor search processing
        result_state = await process_floor_search(update, context)

        # Verify error message sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "❌ Пожалуйста, введите корректный номер этажа" in call_args[1]["text"]

        # Verify state remains in waiting
        assert result_state == FloorSearchStates.WAITING_FOR_FLOOR

    @pytest.mark.asyncio
    async def test_floor_search_with_no_participants_found(
        self, mock_update_and_context
    ):
        """Test floor search when no participants found on floor."""
        update, context = mock_update_and_context
        update.message.text = "99"

        # Mock search service to return empty results
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(return_value=[])
            mock_get_service.return_value = mock_service

            # Execute floor search
            result_state = await process_floor_search(update, context)

            # Verify service call
            mock_service.search_by_floor.assert_called_once_with(99)

            # Verify no participants message sent
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args
            assert "❌ На этаже 99 участники не найдены." in call_args[1]["text"]

            # Verify correct state returned
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

    @pytest.mark.asyncio
    async def test_floor_search_with_api_error_handling(self, mock_update_and_context):
        """Test floor search handles API errors gracefully."""
        update, context = mock_update_and_context
        update.message.text = "2"

        # Mock search service to raise exception
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(side_effect=Exception("API Error"))
            mock_get_service.return_value = mock_service

            # Execute floor search
            result_state = await process_floor_search(update, context)

            # Verify error message sent
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args
            assert (
                "❌ Произошла ошибка при поиске. Попробуйте позже."
                in call_args[1]["text"]
            )

            # Verify correct state returned
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

    @pytest.mark.asyncio
    async def test_floor_search_room_grouping_and_sorting(
        self, multi_room_floor_participants
    ):
        """Test floor search properly groups and sorts results by room number."""
        # Test the formatting function directly
        result = format_floor_results(multi_room_floor_participants, 2)

        # Verify header
        assert "🏢 Найдено участников на этаже 2: 5" in result

        # Verify room grouping and sorting (201, 202, 203)
        lines = result.split("\n")
        room_201_idx = next(
            i for i, line in enumerate(lines) if "🚪 Комната 201:" in line
        )
        room_202_idx = next(
            i for i, line in enumerate(lines) if "🚪 Комната 202:" in line
        )
        room_203_idx = next(
            i for i, line in enumerate(lines) if "🚪 Комната 203:" in line
        )

        # Verify proper ordering
        assert room_201_idx < room_202_idx < room_203_idx

        # Verify participants grouped correctly
        # Room 201 should have Иван and Мария
        room_201_section = "\n".join(lines[room_201_idx:room_202_idx])
        assert "Иван Петров" in room_201_section
        assert "Мария Сидорова" in room_201_section

        # Room 202 should have Алексей and Елена
        room_202_section = "\n".join(lines[room_202_idx:room_203_idx])
        assert "Алексей Кузнецов" in room_202_section
        assert "Елена Васильева" in room_202_section

        # Room 203 should have Дмитрий
        room_203_section = "\n".join(lines[room_203_idx:])
        assert "Дмитрий Орлов" in room_203_section

    @pytest.mark.asyncio
    async def test_floor_search_handles_missing_room_numbers(
        self, mock_update_and_context
    ):
        """Test floor search handles participants with missing room numbers."""
        # Create participants with missing room numbers
        participants_with_missing_room = [
            Participant(
                record_id="rec001",
                full_name_ru="Иван Петров",
                full_name_en="Ivan Petrov",
                nickname="Vanya",
                floor=2,
                room_number="201",
            ),
            Participant(
                record_id="rec002",
                full_name_ru="Мария Сидорова",
                full_name_en="Maria Sidorova",
                nickname="Masha",
                floor=2,
                room_number=None,  # Missing room number
            ),
        ]

        # Test the formatting function directly
        result = format_floor_results(participants_with_missing_room, 2)

        # Verify both known and unknown rooms are handled
        assert "🚪 Комната 201:" in result
        assert "🚪 Комната Неизвестно:" in result
        assert "Иван Петров" in result
        assert "Мария Сидорова" in result

    @pytest.mark.asyncio
    async def test_floor_search_alphanumeric_room_sorting(self):
        """Test floor search properly sorts alphanumeric room numbers."""
        participants_mixed_rooms = [
            Participant(
                record_id="rec001",
                full_name_ru="Participant A",
                floor=2,
                room_number="B10",
            ),
            Participant(
                record_id="rec002",
                full_name_ru="Participant B",
                floor=2,
                room_number="205",
            ),
            Participant(
                record_id="rec003",
                full_name_ru="Participant C",
                floor=2,
                room_number="201",
            ),
        ]

        result = format_floor_results(participants_mixed_rooms, 2)
        lines = result.split("\n")

        # Numeric rooms should come first (201, 205), then alphanumeric (B10)
        room_201_idx = next(
            i for i, line in enumerate(lines) if "🚪 Комната 201:" in line
        )
        room_205_idx = next(
            i for i, line in enumerate(lines) if "🚪 Комната 205:" in line
        )
        room_b10_idx = next(
            i for i, line in enumerate(lines) if "🚪 Комната B10:" in line
        )

        assert room_201_idx < room_205_idx < room_b10_idx

    @pytest.mark.asyncio
    async def test_floor_search_performance_under_3_seconds(
        self, mock_update_and_context, multi_room_floor_participants
    ):
        """Test floor search completes within performance target (3 seconds)."""
        update, context = mock_update_and_context
        update.message.text = "2"

        # Mock search service with realistic delay
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()

            async def mock_search_delay(*args, **kwargs):
                await asyncio.sleep(0.2)  # Simulate realistic API delay
                return multi_room_floor_participants

            mock_service.search_by_floor = mock_search_delay
            mock_get_service.return_value = mock_service

            # Measure execution time
            import time

            start_time = time.time()
            result_state = await process_floor_search(update, context)
            end_time = time.time()

            execution_time = end_time - start_time

            # Verify performance target met (< 3 seconds)
            assert (
                execution_time < 3.0
            ), f"Floor search took {execution_time:.2f}s, exceeding 3s limit"

            # Verify successful completion
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

    @pytest.mark.asyncio
    async def test_floor_search_string_floor_number_support(
        self, mock_update_and_context, multi_room_floor_participants
    ):
        """Test floor search supports string floor numbers (e.g., '2')."""
        update, context = mock_update_and_context
        update.message.text = "2"  # String input

        # Mock search service
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(
                return_value=multi_room_floor_participants
            )
            mock_get_service.return_value = mock_service

            # Execute floor search
            result_state = await process_floor_search(update, context)

            # Verify service called with converted integer
            mock_service.search_by_floor.assert_called_once_with(2)

            # Verify successful result
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

            # Verify results contain floor data
            update.message.reply_text.assert_called_once()
            call_args = update.message.reply_text.call_args
            assert "🏢 Найдено участников на этаже 2: 5" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_floor_search_empty_floor_handling(self, mock_update_and_context):
        """Test floor search formatting for empty floor."""
        # Test format function directly with empty list
        result = format_floor_results([], 5)

        # Should return appropriate message for empty floor
        assert result == "❌ На этаже 5 участники не найдены."
