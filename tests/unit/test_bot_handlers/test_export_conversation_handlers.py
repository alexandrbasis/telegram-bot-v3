"""
Tests for export conversation handlers.

Validates conversation flow, state transitions, admin validation,
and integration with export services through service factory.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import CallbackQuery, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.export_conversation_handlers import (
    start_export_selection,
    handle_export_type_selection,
    handle_department_selection,
    cancel_export,
    get_export_conversation_handler,
)
from src.bot.handlers.export_states import ExportStates, ExportCallbackData


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
        with patch('src.bot.handlers.export_conversation_handlers.is_admin_user', return_value=True):
            result = await start_export_selection(update, context)

        # Should return the SELECTING_EXPORT_TYPE state
        assert result == ExportStates.SELECTING_EXPORT_TYPE

        # Should send export selection keyboard
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "🔧 Выберите тип экспорта" in call_args[0][0]  # Russian text
        assert call_args[1]['reply_markup'] is not None  # Keyboard provided

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
        with patch('src.bot.handlers.export_conversation_handlers.is_admin_user', return_value=False):
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
        mock_export_service.export_to_csv_async = AsyncMock(return_value="test,csv,data")

        with patch('src.services.service_factory.get_export_service', return_value=mock_export_service):
            result = await handle_export_type_selection(update, context)

        # Should transition to PROCESSING_EXPORT state
        assert result == ExportStates.PROCESSING_EXPORT

        # Should acknowledge callback
        query.answer.assert_called_once()

        # Should update message text
        query.edit_message_text.assert_called_once()

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
        assert call_args[1]['reply_markup'] is not None  # Department keyboard

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
        mock_export_service.export_to_csv_async = AsyncMock(return_value="bible,readers,data")

        with patch('src.services.service_factory.get_bible_readers_export_service', return_value=mock_export_service):
            result = await handle_export_type_selection(update, context)

        # Should transition to PROCESSING_EXPORT state
        assert result == ExportStates.PROCESSING_EXPORT

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
        mock_export_service.export_filtered_to_csv_async = AsyncMock(return_value="kitchen,participants,data")

        with patch('src.services.service_factory.get_export_service', return_value=mock_export_service):
            result = await handle_department_selection(update, context)

        # Should transition to PROCESSING_EXPORT state
        assert result == ExportStates.PROCESSING_EXPORT

        # Should call export service with department filter
        mock_export_service.export_filtered_to_csv_async.assert_called_once()
        call_args = mock_export_service.export_filtered_to_csv_async.call_args
        assert call_args[1]['department'] == "Kitchen"

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
        assert hasattr(handler, 'states')
        assert hasattr(handler, 'entry_points')
        assert hasattr(handler, 'fallbacks')

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
        assert hasattr(entry_point, 'callback')
        # Should be a CommandHandler (checking type name)
        assert entry_point.__class__.__name__ == 'CommandHandler'

    def test_conversation_handler_state_transitions(self):
        """Test that state handlers are properly mapped."""
        handler = get_export_conversation_handler()

        # Each state should have callback query handlers
        for state in [ExportStates.SELECTING_EXPORT_TYPE, ExportStates.SELECTING_DEPARTMENT]:
            state_handlers = handler.states.get(state, [])
            assert len(state_handlers) > 0

            # Should have at least one CallbackQueryHandler
            has_callback_handler = any(
                hasattr(h, 'pattern') for h in state_handlers
            )
            assert has_callback_handler