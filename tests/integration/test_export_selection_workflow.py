"""
End-to-end integration tests for export selection workflow.

Tests complete conversation flow from /export command through selection
menus to actual export processing with service integration.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import CallbackQuery, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.export_conversation_handlers import (
    cancel_export,
    handle_department_selection,
    handle_export_type_selection,
    start_export_selection,
)
from src.bot.handlers.export_states import ExportCallbackData, ExportStates


class TestExportSelectionWorkflow:
    """Test complete export selection workflow integration."""

    @pytest.mark.asyncio
    async def test_complete_export_all_workflow(self):
        """Test complete workflow for Export All selection."""
        # Create mock update and context
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.message = AsyncMock(spec=Message)
        update.message.reply_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock admin validation
        with patch(
            "src.bot.handlers.export_conversation_handlers.is_admin_user",
            return_value=True,
        ):
            # Start export selection
            result = await start_export_selection(update, context)

        # Should enter SELECTING_EXPORT_TYPE state
        assert result == ExportStates.SELECTING_EXPORT_TYPE

        # Should display export selection menu
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "🔧 Выберите тип экспорта" in call_args[0][0]
        assert call_args[1]["reply_markup"] is not None

        # Now simulate user selecting "Export All"
        query_update = MagicMock(spec=Update)
        query_update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        query_update.callback_query = AsyncMock(spec=CallbackQuery)
        query_update.callback_query.data = ExportCallbackData.EXPORT_ALL
        query_update.callback_query.answer = AsyncMock()
        query_update.callback_query.edit_message_text = AsyncMock()

        # Mock export service
        mock_export_service = AsyncMock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="participant1,data\nparticipant2,data"
        )

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            with patch(
                "src.bot.handlers.export_conversation_handlers._send_export_file"
            ) as mock_send_file:
                result = await handle_export_type_selection(query_update, context)

        # Should end conversation after processing export
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

        # Should call export service
        mock_export_service.export_to_csv_async.assert_called_once()

        # Should call file sending
        mock_send_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_department_selection_workflow(self):
        """Test complete workflow for department selection."""
        # Start with export type selection
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.callback_query = AsyncMock(spec=CallbackQuery)
        update.callback_query.data = ExportCallbackData.EXPORT_BY_DEPARTMENT
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        # Handle export by department selection
        result = await handle_export_type_selection(update, context)

        # Should enter SELECTING_DEPARTMENT state
        assert result == ExportStates.SELECTING_DEPARTMENT

        # Should show department selection keyboard
        update.callback_query.edit_message_text.assert_called_once()
        call_args = update.callback_query.edit_message_text.call_args
        assert "🏢 Выберите отдел" in call_args[0][0]
        assert call_args[1]["reply_markup"] is not None

        # Now simulate user selecting Kitchen department
        dept_update = MagicMock(spec=Update)
        dept_update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        dept_update.callback_query = AsyncMock(spec=CallbackQuery)
        dept_update.callback_query.data = ExportCallbackData.department_callback(
            "Kitchen"
        )
        dept_update.callback_query.answer = AsyncMock()
        dept_update.callback_query.edit_message_text = AsyncMock()

        context.bot_data = {"settings": MagicMock()}

        # Mock export service for department filtering
        mock_export_service = AsyncMock()
        mock_export_service.get_participants_by_department_as_csv = AsyncMock(
            return_value="kitchen_participant,data"
        )

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            with patch(
                "src.bot.handlers.export_conversation_handlers._send_export_file"
            ) as mock_send_file:
                result = await handle_department_selection(dept_update, context)

        # Should end conversation after processing export
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

        # Should call export service with department filter
        mock_export_service.get_participants_by_department_as_csv.assert_called_once()
        call_args = mock_export_service.get_participants_by_department_as_csv.call_args
        # Should be called with Department enum value
        from src.models.participant import Department

        call_args[0][0] == Department("Kitchen")

    @pytest.mark.asyncio
    async def test_bible_readers_export_workflow(self):
        """Test complete workflow for Bible Readers export."""
        # Create mock update for Bible Readers selection
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.callback_query = AsyncMock(spec=CallbackQuery)
        update.callback_query.data = ExportCallbackData.EXPORT_BIBLE_READERS
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock Bible Readers export service
        mock_bible_service = AsyncMock()
        mock_bible_service.export_to_csv_async = AsyncMock(
            return_value="reader1,scripture,location"
        )

        with patch(
            "src.services.service_factory.get_bible_readers_export_service",
            return_value=mock_bible_service,
        ):
            with patch(
                "src.bot.handlers.export_conversation_handlers._send_export_file"
            ) as mock_send_file:
                result = await handle_export_type_selection(update, context)

        # Should end conversation after processing export
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

        # Should call Bible Readers export service
        mock_bible_service.export_to_csv_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_roe_export_workflow(self):
        """Test complete workflow for ROE export."""
        # Create mock update for ROE selection
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.callback_query = AsyncMock(spec=CallbackQuery)
        update.callback_query.data = ExportCallbackData.EXPORT_ROE
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock ROE export service
        mock_roe_service = AsyncMock()
        mock_roe_service.export_to_csv_async = AsyncMock(
            return_value="topic1,presenter,schedule"
        )

        with patch(
            "src.services.service_factory.get_roe_export_service",
            return_value=mock_roe_service,
        ):
            with patch(
                "src.bot.handlers.export_conversation_handlers._send_export_file"
            ) as mock_send_file:
                result = await handle_export_type_selection(update, context)

        # Should end conversation after processing export
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

        # Should call ROE export service
        mock_roe_service.export_to_csv_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_department_back_navigation(self):
        """Test back navigation from department selection."""
        # Create mock update for back button
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.callback_query = AsyncMock(spec=CallbackQuery)
        update.callback_query.data = ExportCallbackData.BACK_TO_EXPORT_SELECTION
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        result = await handle_department_selection(update, context)

        # Should return to SELECTING_EXPORT_TYPE state
        assert result == ExportStates.SELECTING_EXPORT_TYPE

        # Should show export selection keyboard again
        update.callback_query.edit_message_text.assert_called_once()
        call_args = update.callback_query.edit_message_text.call_args
        assert "🔧 Выберите тип экспорта" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_cancel_workflow(self):
        """Test cancellation workflow."""
        # Create mock update for cancel button
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.callback_query = AsyncMock(spec=CallbackQuery)
        update.callback_query.data = ExportCallbackData.CANCEL
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

        result = await cancel_export(update, context)

        # Should end conversation
        assert result == -1  # ConversationHandler.END

        # Should send cancellation message
        update.callback_query.edit_message_text.assert_called_once()
        call_args = update.callback_query.edit_message_text.call_args
        assert "❌" in call_args[0][0]
        assert "отмен" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_role_based_export_workflows(self):
        """Test role-based export workflows (Team and Candidates)."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock export service
        mock_export_service = AsyncMock()
        mock_export_service.get_participants_by_role_as_csv = AsyncMock(
            return_value="filtered,participants"
        )

        # Test Team export
        team_update = MagicMock(spec=Update)
        team_update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        team_update.callback_query = AsyncMock(spec=CallbackQuery)
        team_update.callback_query.data = ExportCallbackData.EXPORT_TEAM
        team_update.callback_query.answer = AsyncMock()
        team_update.callback_query.edit_message_text = AsyncMock()

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            with patch(
                "src.bot.handlers.export_conversation_handlers._send_export_file"
            ):
                result = await handle_export_type_selection(team_update, context)

        # Should call with Role.TEAM
        from src.models.participant import Role

        mock_export_service.get_participants_by_role_as_csv.assert_called_with(
            Role.TEAM
        )
        # Should end conversation after processing export
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

        # Test Candidates export
        mock_export_service.reset_mock()
        candidates_update = MagicMock(spec=Update)
        candidates_update.effective_user = User(
            id=123, first_name="Admin", is_bot=False
        )
        candidates_update.callback_query = AsyncMock(spec=CallbackQuery)
        candidates_update.callback_query.data = ExportCallbackData.EXPORT_CANDIDATES
        candidates_update.callback_query.answer = AsyncMock()
        candidates_update.callback_query.edit_message_text = AsyncMock()

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            with patch(
                "src.bot.handlers.export_conversation_handlers._send_export_file"
            ):
                result = await handle_export_type_selection(candidates_update, context)

        # Should call with Role.CANDIDATE
        mock_export_service.get_participants_by_role_as_csv.assert_called_with(
            Role.CANDIDATE
        )
        assert result == ConversationHandler.END

    @pytest.mark.asyncio
    async def test_error_handling_during_export(self):
        """Test error handling during export processing."""
        # Create mock update
        update = MagicMock(spec=Update)
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        update.callback_query = AsyncMock(spec=CallbackQuery)
        update.callback_query.data = ExportCallbackData.EXPORT_ALL
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {"settings": MagicMock()}

        # Mock export service to raise exception
        mock_export_service = AsyncMock()
        mock_export_service.export_to_csv_async = AsyncMock(
            side_effect=Exception("Export failed")
        )

        with patch(
            "src.services.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            result = await handle_export_type_selection(update, context)

        # Should still end conversation even with error
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

        # Should send error message
        update.callback_query.edit_message_text.assert_called()
        error_call = None
        for call in update.callback_query.edit_message_text.call_args_list:
            if "❌" in call[0][0]:
                error_call = call
                break

        assert error_call is not None, "Error message should be sent"
