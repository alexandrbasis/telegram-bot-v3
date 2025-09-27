"""
Tests for export conversation handlers.

Validates conversation flow, state transitions, admin validation,
and integration with export services through service factory.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import CallbackQuery, Message, Update, User
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.handlers.export_conversation_handlers import (
    _send_export_file,
    cancel_export,
    get_export_conversation_handler,
    handle_department_selection,
    handle_export_type_selection,
    start_export_selection,
)
from src.bot.handlers.export_states import ExportCallbackData, ExportStates


class TestExportConversationEntryPoint:
    """Test export conversation entry point and admin validation."""

    @pytest.mark.asyncio
    async def test_start_export_selection_admin_access(self):
        """Test that start_export_selection validates admin access."""
        # Create mock update and context
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Test", is_bot=False)
        update.message = AsyncMock(spec=Message)
        update.message.reply_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock admin validation to return True
        with patch(
            "src.bot.handlers.export_conversation_handlers.is_admin_user",
            return_value=True,
        ):
            result = await start_export_selection(update, context)

        # Should return the SELECTING_EXPORT_TYPE state
        assert result == ExportStates.SELECTING_EXPORT_TYPE

        # Should send export selection keyboard
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "🔧 Выберите тип экспорта" in call_args[0][0]  # Russian text
        assert call_args[1]["reply_markup"] is not None  # Keyboard provided

    @pytest.mark.asyncio
    async def test_start_export_selection_non_admin_denied(self):
        """Test that non-admin users are denied access."""
        # Create mock update and context
        update = MagicMock(spec=Update)
        update.effective_user = User(id=456, first_name="NonAdmin", is_bot=False)
        update.message = AsyncMock(spec=Message)
        update.message.reply_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock admin validation to return False
        with patch(
            "src.bot.handlers.export_conversation_handlers.is_admin_user",
            return_value=False,
        ):
            result = await start_export_selection(update, context)

        # Should end conversation
        assert result == -1  # ConversationHandler.END

        # Should send access denied message
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "🚫" in call_args[0][0]  # Access denied emoji
        assert "прав" in call_args[0][0]  # Russian for "rights/permissions"


class TestExportTypeSelection:
    """Test export type selection callback handling."""

    @pytest.mark.asyncio
    async def test_handle_export_all_selection(self):
        """Test handling of Export All selection."""
        # Create mock callback query
        query = AsyncMock(spec=CallbackQuery)
        query.data = ExportCallbackData.EXPORT_ALL
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock export service
        mock_export_service = AsyncMock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="test,csv,data"
        )

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            result = await handle_export_type_selection(update, context)

        # Should end the conversation
        assert result == ConversationHandler.END

        # Should acknowledge callback
        query.answer.assert_called_once()

        # Should update message text twice (start + completion)
        assert query.edit_message_text.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_department_selection_flow(self):
        """Test handling of Export by Department selection."""
        # Create mock callback query
        query = AsyncMock(spec=CallbackQuery)
        query.data = ExportCallbackData.EXPORT_BY_DEPARTMENT
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        result = await handle_export_type_selection(update, context)

        # Should transition to SELECTING_DEPARTMENT state
        assert result == ExportStates.SELECTING_DEPARTMENT

        # Should acknowledge callback
        query.answer.assert_called_once()

        # Should show department selection keyboard
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert call_args[1]["reply_markup"] is not None  # Department keyboard

    @pytest.mark.asyncio
    async def test_handle_bible_readers_export(self):
        """Test handling of Bible Readers export selection."""
        # Create mock callback query
        query = AsyncMock(spec=CallbackQuery)
        query.data = ExportCallbackData.EXPORT_BIBLE_READERS
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock Bible Readers export service
        mock_export_service = AsyncMock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="bible,readers,data"
        )

        with patch(
            "src.services.service_factory.get_bible_readers_export_service",
            return_value=mock_export_service,
        ):
            result = await handle_export_type_selection(update, context)

        # Should end the conversation
        assert result == ConversationHandler.END

        # Should call Bible Readers export service
        mock_export_service.export_to_csv_async.assert_called_once()


class TestDepartmentSelection:
    """Test department selection callback handling."""

    @pytest.mark.asyncio
    async def test_handle_department_selection_valid(self):
        """Test handling of valid department selection."""
        # Create mock callback query for Kitchen department
        query = AsyncMock(spec=CallbackQuery)
        query.data = ExportCallbackData.department_callback("Kitchen")
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock participant export service with department filtering
        mock_export_service = AsyncMock()
        mock_export_service.get_participants_by_department_as_csv = AsyncMock(
            return_value="kitchen,participants,data"
        )

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            result = await handle_department_selection(update, context)

        # Should end the conversation
        assert result == ConversationHandler.END

        # Should call export service with department filter
        mock_export_service.get_participants_by_department_as_csv.assert_called_once()
        call_args = mock_export_service.get_participants_by_department_as_csv.call_args
        assert call_args[0][0].value == "Kitchen"

    @pytest.mark.asyncio
    async def test_handle_department_back_navigation(self):
        """Test handling of back button in department selection."""
        # Create mock callback query for back button
        query = AsyncMock(spec=CallbackQuery)
        query.data = ExportCallbackData.BACK_TO_EXPORT_SELECTION
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        result = await handle_department_selection(update, context)

        # Should return to SELECTING_EXPORT_TYPE state
        assert result == ExportStates.SELECTING_EXPORT_TYPE

        # Should show export selection keyboard again
        query.edit_message_text.assert_called_once()


class TestCancelAndErrorHandling:
    """Test cancel functionality and error handling."""

    @pytest.mark.asyncio
    async def test_cancel_export_conversation(self):
        """Test that cancel properly ends conversation."""
        # Create mock callback query for cancel
        query = AsyncMock(spec=CallbackQuery)
        query.data = ExportCallbackData.CANCEL
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = MagicMock(spec=Update)
        update.callback_query = query

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        result = await cancel_export(update, context)

        # Should end conversation
        assert result == -1  # ConversationHandler.END

        # Should send cancellation message
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "❌" in call_args[0][0]  # Cancel emoji
        assert "отмен" in call_args[0][0].lower()  # Russian for "cancelled"


class TestConversationHandlerSetup:
    """Test conversation handler configuration."""

    def test_get_export_conversation_handler_structure(self):
        """Test that conversation handler is properly configured."""
        handler = get_export_conversation_handler()

        # Should be a ConversationHandler
        assert hasattr(handler, "states")
        assert hasattr(handler, "entry_points")
        assert hasattr(handler, "fallbacks")

        # Should have all required states
        assert ExportStates.SELECTING_EXPORT_TYPE in handler.states
        assert ExportStates.SELECTING_DEPARTMENT in handler.states
        assert ExportStates.PROCESSING_EXPORT in handler.states

        # Should have entry points for /export command
        assert len(handler.entry_points) > 0

        # Should have fallback handlers for cancel
        assert len(handler.fallbacks) > 0

    def test_conversation_handler_entry_points(self):
        """Test that conversation handler has correct entry points."""
        handler = get_export_conversation_handler()

        # Should have CommandHandler for /export
        entry_point = handler.entry_points[0]
        assert hasattr(entry_point, "callback")
        # Should be a CommandHandler (checking type name)
        assert entry_point.__class__.__name__ == "CommandHandler"

    def test_conversation_handler_state_transitions(self):
        """Test that state handlers are properly mapped."""
        handler = get_export_conversation_handler()

        # Each state should have callback query handlers
        for state in [
            ExportStates.SELECTING_EXPORT_TYPE,
            ExportStates.SELECTING_DEPARTMENT,
        ]:
            state_handlers = handler.states.get(state, [])
            assert len(state_handlers) > 0

            # Should have at least one CallbackQueryHandler
            has_callback_handler = any(hasattr(h, "pattern") for h in state_handlers)
            assert has_callback_handler


class TestExportFileDeliveryWithRussianDescriptions:
    """Test export file delivery includes Russian export type descriptions."""

    @pytest.mark.asyncio
    async def test_send_export_file_includes_russian_description_for_candidates(self):
        """Test that candidates export includes Russian description in success message."""
        # Create mock query with message
        query = AsyncMock(spec=CallbackQuery)
        query.message = AsyncMock(spec=Message)
        query.message.reply_document = AsyncMock()
        query.edit_message_text = AsyncMock()

        csv_data = "#,Name,Age\n1,John Doe,25\n2,Jane Smith,30"

        # Mock format_export_success_message to capture the call
        with patch(
            "src.bot.handlers.export_conversation_handlers.format_export_success_message"
        ) as mock_format:
            mock_format.return_value = (
                "✅ Экспорт завершен успешно!\nВыгружены: Кандидаты"
            )

            await _send_export_file(csv_data, "participants_candidates", query, 123)

            # Verify format_export_success_message was called with export_type
            mock_format.assert_called_once()
            call_args = mock_format.call_args
            call_kwargs = call_args[1] if len(call_args) > 1 else call_args.kwargs

            # Should include export_type parameter
            assert "export_type" in call_kwargs
            assert call_kwargs["export_type"] == "candidates"

    @pytest.mark.asyncio
    async def test_send_export_file_includes_russian_description_for_team(self):
        """Test that team export includes Russian description in success message."""
        query = AsyncMock(spec=CallbackQuery)
        query.message = AsyncMock(spec=Message)
        query.message.reply_document = AsyncMock()
        query.edit_message_text = AsyncMock()

        csv_data = "#,Name,Role\n1,John Doe,TEAM\n2,Jane Smith,TEAM"

        with patch(
            "src.bot.handlers.export_conversation_handlers.format_export_success_message"
        ) as mock_format:
            mock_format.return_value = (
                "✅ Экспорт завершен успешно!\nВыгружены: Тим Мемберы"
            )

            await _send_export_file(csv_data, "participants_team", query, 123)

            mock_format.assert_called_once()
            call_args = mock_format.call_args
            call_kwargs = call_args[1] if len(call_args) > 1 else call_args.kwargs

            assert "export_type" in call_kwargs
            assert call_kwargs["export_type"] == "team"

    @pytest.mark.asyncio
    async def test_send_export_file_includes_russian_description_for_roe(self):
        """Test that ROE export includes Russian description in success message."""
        query = AsyncMock(spec=CallbackQuery)
        query.message = AsyncMock(spec=Message)
        query.message.reply_document = AsyncMock()
        query.edit_message_text = AsyncMock()

        csv_data = "#,Session,Date\n1,Session 1,2025-01-01\n2,Session 2,2025-01-02"

        with patch(
            "src.bot.handlers.export_conversation_handlers.format_export_success_message"
        ) as mock_format:
            mock_format.return_value = "✅ Экспорт завершен успешно!\nВыгружены: РОЭ"

            await _send_export_file(csv_data, "roe_sessions", query, 123)

            mock_format.assert_called_once()
            call_args = mock_format.call_args
            call_kwargs = call_args[1] if len(call_args) > 1 else call_args.kwargs

            assert "export_type" in call_kwargs
            assert call_kwargs["export_type"] == "roe"

    @pytest.mark.asyncio
    async def test_send_export_file_includes_russian_description_for_bible_readers(
        self,
    ):
        """Test that Bible readers export includes Russian description in success message."""
        query = AsyncMock(spec=CallbackQuery)
        query.message = AsyncMock(spec=Message)
        query.message.reply_document = AsyncMock()
        query.edit_message_text = AsyncMock()

        csv_data = "#,Name,Passage\n1,John Doe,Psalm 23\n2,Jane Smith,Matthew 5"

        with patch(
            "src.bot.handlers.export_conversation_handlers.format_export_success_message"
        ) as mock_format:
            mock_format.return_value = "✅ Экспорт завершен успешно!\nВыгружены: Чтецы"

            await _send_export_file(csv_data, "bible_readers", query, 123)

            mock_format.assert_called_once()
            call_args = mock_format.call_args
            call_kwargs = call_args[1] if len(call_args) > 1 else call_args.kwargs

            assert "export_type" in call_kwargs
            assert call_kwargs["export_type"] == "bible_readers"

    @pytest.mark.asyncio
    async def test_send_export_file_includes_russian_description_for_departments(self):
        """Test that department export includes Russian description in success message."""
        query = AsyncMock(spec=CallbackQuery)
        query.message = AsyncMock(spec=Message)
        query.message.reply_document = AsyncMock()
        query.edit_message_text = AsyncMock()

        csv_data = "#,Name,Department\n1,John Doe,IT\n2,Jane Smith,HR"

        with patch(
            "src.bot.handlers.export_conversation_handlers.format_export_success_message"
        ) as mock_format:
            mock_format.return_value = (
                "✅ Экспорт завершен успешно!\nВыгружены: Департаменты"
            )

            await _send_export_file(csv_data, "participants_admin", query, 123)

            mock_format.assert_called_once()
            call_args = mock_format.call_args
            call_kwargs = call_args[1] if len(call_args) > 1 else call_args.kwargs

            assert "export_type" in call_kwargs
            assert call_kwargs["export_type"] == "departments"
