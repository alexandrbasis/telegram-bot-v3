"""
Integration tests for search→edit→save workflow.

Tests the complete user flow from searching participants to editing and saving changes.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from telegram import User, Chat, Message, Update, CallbackQuery
from telegram.ext import ContextTypes

from src.models.participant import Participant, Role, Gender, Size, Department
from src.data.repositories.participant_repository import RepositoryError, NotFoundError


class TestSearchToEditFlow:
    """Integration tests for complete search→edit→save workflow."""

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
        query.data = "edit_participant_rec123"
        query.answer = AsyncMock()
        return query

    @pytest.fixture
    def mock_update(self, mock_callback_query):
        """Mock Telegram update with callback query."""
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
            record_id="rec123456789012345",
            full_name_ru="Тест Участник",
            role=Role.CANDIDATE,
            gender=Gender.MALE,
            size=Size.L,
            department=Department.CHAPEL,
            payment_amount=1000
        )

    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_complete_edit_and_save_workflow(
        self, 
        mock_get_repo, 
        mock_update, 
        mock_context, 
        sample_participant
    ):
        """Test complete workflow: select participant → edit fields → save changes."""
        # Setup: participant in context from search results
        mock_context.user_data['current_participant'] = sample_participant
        mock_context.user_data['editing_changes'] = {}
        
        # Setup repository mock
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(return_value=True)
        mock_get_repo.return_value = mock_repo

        # Step 1: Show edit menu for participant
        from src.bot.handlers.edit_participant_handlers import show_participant_edit_menu
        
        result = await show_participant_edit_menu(mock_update, mock_context)
        
        # Should show editing interface
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Тест Участник' in message_text
        assert 'Редактирование' in message_text

        # Step 2: Simulate field edit (change role to TEAM)
        mock_update.callback_query.data = "edit_field:role"
        
        from src.bot.handlers.edit_participant_handlers import handle_field_edit_selection
        
        result = await handle_field_edit_selection(mock_update, mock_context)
        
        # Should show role selection buttons
        mock_update.callback_query.message.edit_text.assert_called()
        
        # Step 3: Select new role value
        mock_update.callback_query.data = "role:TEAM"
        
        from src.bot.handlers.edit_participant_handlers import handle_button_field_selection
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        # Should update editing changes and show updated edit menu
        assert mock_context.user_data['editing_changes']['role'] == Role.TEAM

        # Step 4: Add another change (payment amount)  
        mock_context.user_data['editing_field'] = 'payment_amount'
        mock_update.message = mock_update.callback_query.message
        mock_update.message.text = "1500"  # New payment amount
        mock_update.message.reply_text = AsyncMock()
        mock_update.effective_user = mock_update.callback_query.from_user
        
        from src.bot.handlers.edit_participant_handlers import handle_text_field_input
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        # Should update payment amount
        assert mock_context.user_data['editing_changes']['payment_amount'] == 1500

        # Step 5: Show save confirmation
        mock_update.callback_query.data = "show_save_confirmation"
        
        from src.bot.handlers.edit_participant_handlers import show_save_confirmation
        
        result = await show_save_confirmation(mock_update, mock_context)
        
        # Should show confirmation with changes summary
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        
        assert 'подтвердить' in message_text.lower()
        assert 'TEAM' in message_text  # Should show role change
        assert '1500' in message_text  # Should show payment amount change

        # Step 6: Confirm save
        mock_update.callback_query.data = "confirm_save"
        
        from src.bot.handlers.edit_participant_handlers import save_changes
        
        result = await save_changes(mock_update, mock_context)
        
        # Should call repository update with correct changes
        mock_repo.update_by_id.assert_called_once_with(
            "rec123456789012345",
            {'role': Role.TEAM, 'payment_amount': 1500}
        )
        
        # Should show success message
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'сохранен' in message_text.lower()
        
        # Should clear editing state
        assert mock_context.user_data['editing_changes'] == {}

    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_edit_and_cancel_workflow(
        self,
        mock_get_repo,
        mock_update,
        mock_context,
        sample_participant
    ):
        """Test edit workflow with cancel - changes should not be saved."""
        # Setup: participant in context with some changes
        mock_context.user_data['current_participant'] = sample_participant
        mock_context.user_data['editing_changes'] = {
            'role': Role.TEAM,
            'payment_amount': 2000
        }
        
        # Setup repository mock (should not be called)
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock()
        mock_get_repo.return_value = mock_repo

        # Cancel editing
        mock_update.callback_query.data = "cancel_editing"
        
        from src.bot.handlers.edit_participant_handlers import cancel_editing
        
        result = await cancel_editing(mock_update, mock_context)
        
        # Should not call repository
        mock_repo.update_by_id.assert_not_called()
        
        # Should clear editing state
        assert mock_context.user_data['editing_changes'] == {}
        assert mock_context.user_data['editing_field'] is None
        
        # Should show cancellation message
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'отменено' in message_text.lower()

    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_save_with_error_and_retry_workflow(
        self,
        mock_get_repo,
        mock_update,
        mock_context,
        sample_participant
    ):
        """Test save error with retry functionality."""
        # Setup: participant with changes
        mock_context.user_data['current_participant'] = sample_participant
        mock_context.user_data['editing_changes'] = {'role': Role.TEAM}
        
        # Setup repository to fail first, then succeed on retry
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(side_effect=[False, True])  # Fail, then succeed
        mock_get_repo.return_value = mock_repo

        # First save attempt (should fail)
        from src.bot.handlers.edit_participant_handlers import save_changes
        
        result = await save_changes(mock_update, mock_context)
        
        # Should show error with retry option
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'ошибка' in message_text.lower()
        
        # Check retry button is present
        reply_markup = call_args[1]['reply_markup']
        buttons = reply_markup.inline_keyboard
        retry_found = any(
            any('повтор' in btn.text.lower() for btn in row) 
            for row in buttons
        )
        assert retry_found, "Should have retry button"

        # Retry save (should succeed)
        mock_update.callback_query.data = "retry_save"
        
        from src.bot.handlers.edit_participant_handlers import retry_save
        
        result = await retry_save(mock_update, mock_context)
        
        # Should call repository twice (initial + retry)
        assert mock_repo.update_by_id.call_count == 2
        
        # Should show success message on retry
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'сохранен' in message_text.lower()
        
        # Should clear editing state after successful retry
        assert mock_context.user_data['editing_changes'] == {}

    @pytest.mark.asyncio
    async def test_field_validation_prevents_invalid_saves(
        self, 
        mock_update, 
        mock_context,
        sample_participant
    ):
        """Test that field validation prevents saving invalid data."""
        # Setup: participant in context
        mock_context.user_data['current_participant'] = sample_participant
        mock_context.user_data['editing_field'] = 'payment_amount'
        
        # Try to input invalid payment amount
        mock_update.message = mock_update.callback_query.message  
        mock_update.message.text = "invalid_number"
        mock_update.message.reply_text = AsyncMock()
        mock_update.effective_user = mock_update.callback_query.from_user
        
        from src.bot.handlers.edit_participant_handlers import handle_text_field_input
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        # Should not add invalid data to editing_changes
        editing_changes = mock_context.user_data.get('editing_changes', {})
        assert 'payment_amount' not in editing_changes
        
        # Should show validation error
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]['text']
        assert 'ошибка' in message_text.lower() or 'неверн' in message_text.lower()