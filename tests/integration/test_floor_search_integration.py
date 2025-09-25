"""
Integration tests for floor search functionality.

Tests complete floor search workflow from command to response,
including room grouping, Airtable integration and error scenarios.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from telegram import CallbackQuery, Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.floor_search_handlers import (
    FloorSearchStates,
    format_floor_results,
    handle_floor_discovery_callback,
    handle_floor_search_command,
    handle_floor_selection_callback,
    process_floor_search,
    process_floor_search_with_input,
)
from src.models.participant import Participant
from src.services.service_factory import get_search_service


@pytest.fixture
def multi_room_floor_participants():
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


@pytest.fixture
def mock_update_and_context():
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


class TestFloorSearchIntegration:
    """Integration tests for floor search end-to-end workflows."""

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

            # Execute floor search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
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

        # Execute floor search with authorization mocking
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "viewer"
            result_state = await handle_floor_search_command(update, context)

        # Verify prompt messages sent (now sends two messages)
        assert update.message.reply_text.call_count == 2

        # First call should have the discovery message with inline keyboard
        first_call = update.message.reply_text.call_args_list[0]
        assert "Выберите этаж из списка" in first_call[1]["text"]

        # Second call should have navigation reply keyboard
        second_call = update.message.reply_text.call_args_list[1]
        assert "Используйте кнопку выше" in second_call[1]["text"]

        # Verify correct state returned
        assert result_state == FloorSearchStates.WAITING_FOR_FLOOR

    @pytest.mark.asyncio
    async def test_floor_search_with_invalid_floor_number(
        self, mock_update_and_context
    ):
        """Test floor search with invalid floor number (non-numeric)."""
        update, context = mock_update_and_context
        update.message.text = "ABC"

        # Execute floor search processing with authorization mocking
        with patch("src.utils.access_control.get_user_role") as mock_get_role:
            mock_get_role.return_value = "viewer"
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

            # Execute floor search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
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

            # Execute floor search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
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
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
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

            # Execute floor search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
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

    @pytest.mark.asyncio
    async def test_floor_search_cancel(self, mock_update_and_context):
        """Test cancel from WAITING_FOR_FLOOR state returns to main menu."""
        from src.bot.handlers.search_handlers import SearchStates, cancel_search
        from src.bot.keyboards.search_keyboards import NAV_CANCEL

        update, context = mock_update_and_context
        update.message.text = NAV_CANCEL  # "❌ Отмена"

        # Execute cancel search
        result_state = await cancel_search(update, context)

        # Verify welcome message sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args

        # Check message content
        assert "Добро пожаловать в бот Tres Dias!" in call_args[1]["text"]
        assert "Выберите тип поиска участников" in call_args[1]["text"]

        # Check reply markup is main menu keyboard
        assert call_args[1]["reply_markup"] is not None

        # Verify search results cleared
        assert context.user_data["search_results"] == []

        # Verify correct state returned
        assert result_state == SearchStates.MAIN_MENU


class TestFloorSearchCallbackIntegration:
    """Integration tests for complete floor search journey with interactive callbacks."""

    @pytest.fixture
    def mock_callback_update_and_context(self):
        """Create mock Update with CallbackQuery and Context for testing."""
        # Create mock user
        user = Mock(spec=User)
        user.id = 12345
        user.first_name = "Test"

        # Create mock chat
        chat = Mock(spec=Chat)
        chat.id = 67890

        # Create mock message for callback
        message = Mock(spec=Message)
        message.reply_text = AsyncMock()
        message.edit_text = AsyncMock()

        # Create mock callback query
        callback_query = Mock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.message = message
        callback_query.data = ""

        # Create mock update with callback query
        update = Mock(spec=Update)
        update.effective_user = user
        update.effective_chat = chat
        update.callback_query = callback_query

        # Create mock context
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        context.bot = Mock()
        context.bot.send_message = AsyncMock()

        return update, context

    @pytest.fixture
    def available_floors(self):
        """Sample floors for testing."""
        return [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_complete_floor_discovery_journey_success(
        self,
        mock_callback_update_and_context,
        multi_room_floor_participants,
        available_floors,
    ):
        """Test complete user journey: floor search → discovery button → floors list → floor selection → results."""
        update, context = mock_callback_update_and_context

        # === Step 1: Floor discovery callback ===
        update.callback_query.data = "floor_discovery"

        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.get_available_floors = AsyncMock(return_value=available_floors)
            mock_service.search_by_floor = AsyncMock(
                return_value=multi_room_floor_participants
            )
            mock_get_service.return_value = mock_service

            # Execute floor discovery
            await handle_floor_discovery_callback(update, context)

            # Verify callback acknowledged
            update.callback_query.answer.assert_called_once()

            # Verify floors service called
            mock_service.get_available_floors.assert_called_once()

            # Verify message edited with available floors
            update.callback_query.message.edit_text.assert_called_once()
            edit_call_args = update.callback_query.message.edit_text.call_args
            assert "📍 Доступные этажи:" in edit_call_args[1]["text"]

            # Verify floor selection keyboard was provided
            assert edit_call_args[1]["reply_markup"] is not None

        # === Step 2: Floor selection callback ===
        # Reset mocks for floor selection
        update.callback_query.answer.reset_mock()
        update.callback_query.message.edit_text.reset_mock()
        update.callback_query.data = "floor_select_2"

        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(
                return_value=multi_room_floor_participants
            )
            mock_get_service.return_value = mock_service

            # Create a temporary message for the handler (mimics line 338 in floor_search_handlers)
            update.message = update.callback_query.message

            # Execute floor selection
            result_state = await handle_floor_selection_callback(update, context)

            # Verify callback acknowledged
            update.callback_query.answer.assert_called_once()

            # Verify floor number parsed correctly and stored
            assert context.user_data["current_floor"] == "2"

            # Verify searching message sent
            update.callback_query.message.edit_text.assert_called()
            search_call_args = update.callback_query.message.edit_text.call_args_list[0]
            assert "🔍 Ищу участников на этаже 2" in search_call_args[1]["text"]

            # Verify floor search service called
            mock_service.search_by_floor.assert_called_once_with(2)

            # Verify results stored in context
            assert (
                context.user_data["floor_search_results"]
                == multi_room_floor_participants
            )

            # Verify correct state returned
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

    @pytest.mark.asyncio
    async def test_floor_discovery_api_error_fallback(
        self, mock_callback_update_and_context
    ):
        """Test floor discovery handles API errors gracefully with fallback."""
        update, context = mock_callback_update_and_context
        update.callback_query.data = "floor_discovery"

        # Mock search service to raise exception
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.get_available_floors = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_service.return_value = mock_service

            # Execute floor discovery
            await handle_floor_discovery_callback(update, context)

            # Verify callback acknowledged
            update.callback_query.answer.assert_called_once()

            # Verify error message sent
            update.callback_query.message.edit_text.assert_called_once()
            error_call_args = update.callback_query.message.edit_text.call_args
            assert (
                "Произошла ошибка. Пришлите номер этажа цифрой."
                in error_call_args[1]["text"]
            )

    @pytest.mark.asyncio
    async def test_floor_discovery_no_floors_available(
        self, mock_callback_update_and_context
    ):
        """Test floor discovery handles empty floors response."""
        update, context = mock_callback_update_and_context
        update.callback_query.data = "floor_discovery"

        # Mock search service to return empty floors list
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.get_available_floors = AsyncMock(return_value=[])
            mock_get_service.return_value = mock_service

            # Execute floor discovery
            await handle_floor_discovery_callback(update, context)

            # Verify callback acknowledged
            update.callback_query.answer.assert_called_once()

            # Verify appropriate message sent for no floors
            update.callback_query.message.edit_text.assert_called_once()
            no_floors_call_args = update.callback_query.message.edit_text.call_args
            assert (
                "В данный момент участники не размещены ни на одном этаже"
                in no_floors_call_args[1]["text"]
            )

    @pytest.mark.asyncio
    async def test_floor_selection_invalid_callback_data(
        self, mock_callback_update_and_context
    ):
        """Test floor selection handles invalid callback data gracefully."""
        update, context = mock_callback_update_and_context
        update.callback_query.data = "invalid_floor_data"

        # Execute floor selection
        result_state = await handle_floor_selection_callback(update, context)

        # Verify callback acknowledged
        update.callback_query.answer.assert_called_once()

        # Verify error message sent
        update.callback_query.message.edit_text.assert_called_once()
        error_call_args = update.callback_query.message.edit_text.call_args
        assert "❌ Произошла системная ошибка" in error_call_args[1]["text"]

        # Verify returns to waiting state for retry
        assert result_state == FloorSearchStates.WAITING_FOR_FLOOR

    @pytest.mark.asyncio
    async def test_floor_selection_with_no_participants_found(
        self, mock_callback_update_and_context
    ):
        """Test floor selection when no participants found on selected floor."""
        update, context = mock_callback_update_and_context
        update.callback_query.data = "floor_select_99"

        # Mock search service to return empty results
        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(return_value=[])
            mock_get_service.return_value = mock_service

            # Create temporary message for handler
            update.message = update.callback_query.message

            # Execute floor selection
            result_state = await handle_floor_selection_callback(update, context)

            # Verify callback acknowledged
            update.callback_query.answer.assert_called_once()

            # Verify floor search called with correct floor
            mock_service.search_by_floor.assert_called_once_with(99)

            # Verify empty results handled properly
            assert context.user_data["current_floor"] == "99"
            assert context.user_data["floor_search_results"] == []

            # Verify correct state returned
            assert result_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

    @pytest.mark.asyncio
    async def test_callback_handlers_acknowledge_queries(
        self, mock_callback_update_and_context, available_floors
    ):
        """Test that all callback handlers properly acknowledge callback queries to stop loading spinner."""
        update, context = mock_callback_update_and_context

        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.get_available_floors = AsyncMock(return_value=available_floors)
            mock_service.search_by_floor = AsyncMock(return_value=[])
            mock_get_service.return_value = mock_service

            # Test floor discovery callback acknowledgment
            update.callback_query.data = "floor_discovery"
            await handle_floor_discovery_callback(update, context)
            update.callback_query.answer.assert_called()

            # Reset for floor selection test
            update.callback_query.answer.reset_mock()
            update.callback_query.data = "floor_select_1"
            update.message = update.callback_query.message

            # Test floor selection callback acknowledgment
            await handle_floor_selection_callback(update, context)
            update.callback_query.answer.assert_called()

    @pytest.mark.asyncio
    async def test_backward_compatibility_traditional_and_interactive_coexist(
        self,
        mock_update_and_context,
        mock_callback_update_and_context,
        multi_room_floor_participants,
    ):
        """Test that traditional floor input and interactive callbacks can work simultaneously."""
        # Test traditional text input
        text_update, text_context = mock_update_and_context
        text_update.message.text = "2"

        # Test interactive callback
        callback_update, callback_context = mock_callback_update_and_context
        callback_update.callback_query.data = "floor_select_2"
        callback_update.message = callback_update.callback_query.message

        with patch(
            "src.bot.handlers.floor_search_handlers.get_search_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.search_by_floor = AsyncMock(
                return_value=multi_room_floor_participants
            )
            mock_get_service.return_value = mock_service

            # Execute traditional search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                traditional_state = await process_floor_search(
                    text_update, text_context
                )

            # Execute callback search with authorization mocking
            with patch("src.utils.access_control.get_user_role") as mock_get_role:
                mock_get_role.return_value = "viewer"
                callback_state = await handle_floor_selection_callback(
                    callback_update, callback_context
                )

            # Both should reach the same final state
            assert traditional_state == FloorSearchStates.SHOWING_FLOOR_RESULTS
            assert callback_state == FloorSearchStates.SHOWING_FLOOR_RESULTS

            # Both should call search service with same floor
            assert mock_service.search_by_floor.call_count == 2
            mock_service.search_by_floor.assert_any_call(2)  # From both calls

            # Both should store results in context
            assert text_context.user_data["current_floor"] == "2"
            assert callback_context.user_data["current_floor"] == "2"
            assert (
                text_context.user_data["floor_search_results"]
                == multi_room_floor_participants
            )
            assert (
                callback_context.user_data["floor_search_results"]
                == multi_room_floor_participants
            )
