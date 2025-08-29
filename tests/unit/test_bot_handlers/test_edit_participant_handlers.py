"""
Unit tests for participant editing handlers.

Tests conversation flow, state management, and field-specific editing workflows
for the participant editing interface.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, CallbackQuery, Message, User, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.handlers.edit_participant_handlers import (
    EditStates,
    show_participant_edit_menu,
    handle_field_edit_selection,
    handle_text_field_input,
    handle_button_field_selection,
    cancel_editing,
    save_changes
)
from src.models.participant import Participant, Gender, Size, Role, Department, PaymentStatus
from datetime import date


@pytest.fixture
def mock_update():
    """Create mock Update object."""
    update = Mock(spec=Update)
    update.callback_query = Mock(spec=CallbackQuery)
    update.callback_query.answer = AsyncMock()
    update.callback_query.message = Mock(spec=Message)
    update.callback_query.message.edit_text = AsyncMock()
    update.callback_query.from_user = Mock(spec=User)
    update.callback_query.from_user.id = 12345
    
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.text = "Test input"
    
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 12345
    
    return update


@pytest.fixture
def mock_context():
    """Create mock context with user data."""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {
        'current_participant': Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            church='Грейс',
            gender=Gender.MALE,
            size=Size.L,
            role=Role.TEAM,
            department=Department.WORSHIP,
            payment_status=PaymentStatus.PAID,
            payment_amount=1000,
            payment_date=date(2024, 1, 15)
        ),
        'editing_changes': {},
        'editing_field': None
    }
    return context


class TestEditStatesEnum:
    """Test EditStates enum values."""
    
    def test_edit_states_values(self):
        """Test that EditStates has correct integer values."""
        assert EditStates.FIELD_SELECTION.value == 0
        assert EditStates.TEXT_INPUT.value == 1
        assert EditStates.BUTTON_SELECTION.value == 2
        assert EditStates.CONFIRMATION.value == 3


class TestShowParticipantEditMenu:
    """Test show_participant_edit_menu function."""
    
    @pytest.mark.asyncio
    async def test_show_edit_menu_with_participant_data(self, mock_update, mock_context):
        """Test showing edit menu with participant data displays all fields."""
        result = await show_participant_edit_menu(mock_update, mock_context)
        
        # Should return FIELD_SELECTION state
        assert result == EditStates.FIELD_SELECTION
        
        # Should call edit_text with participant data
        mock_update.callback_query.message.edit_text.assert_called_once()
        call_args = mock_update.callback_query.message.edit_text.call_args
        
        message_text = call_args[1]['text']
        assert '✏️ Редактирование участника' in message_text
        assert 'Иван Иванов' in message_text
        assert 'Ivan Ivanov' in message_text
        assert 'Грейс' in message_text
        assert 'Мужской' in message_text
        assert 'L' in message_text
        
        # Should have inline keyboard
        assert 'reply_markup' in call_args[1]
        assert isinstance(call_args[1]['reply_markup'], InlineKeyboardMarkup)
    
    @pytest.mark.asyncio
    async def test_show_edit_menu_without_participant_shows_error(self, mock_update):
        """Test showing edit menu without participant data shows error."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        
        result = await show_participant_edit_menu(mock_update, context)
        
        # Should return FIELD_SELECTION state (graceful handling)
        assert result == EditStates.FIELD_SELECTION
        
        # Should show error message
        mock_update.callback_query.message.edit_text.assert_called_once()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Ошибка' in message_text


class TestHandleFieldEditSelection:
    """Test handle_field_edit_selection function."""
    
    @pytest.mark.asyncio
    async def test_handle_text_field_edit_selection(self, mock_update, mock_context):
        """Test handling text field edit selection prompts for input."""
        mock_update.callback_query.data = 'edit_field:full_name_ru'
        
        result = await handle_field_edit_selection(mock_update, mock_context)
        
        assert result == EditStates.TEXT_INPUT
        assert mock_context.user_data['editing_field'] == 'full_name_ru'
        
        # Should prompt for input
        mock_update.callback_query.message.edit_text.assert_called_once()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Отправьте новое имя на русском' in message_text
    
    @pytest.mark.asyncio
    async def test_handle_button_field_edit_selection(self, mock_update, mock_context):
        """Test handling button field edit selection shows options."""
        mock_update.callback_query.data = 'edit_field:gender'
        
        result = await handle_field_edit_selection(mock_update, mock_context)
        
        assert result == EditStates.BUTTON_SELECTION
        assert mock_context.user_data['editing_field'] == 'gender'
        
        # Should show button options
        mock_update.callback_query.message.edit_text.assert_called_once()
        call_args = mock_update.callback_query.message.edit_text.call_args
        
        message_text = call_args[1]['text']
        assert 'Выберите пол' in message_text
        
        # Should have gender options in keyboard
        keyboard = call_args[1]['reply_markup']
        assert isinstance(keyboard, InlineKeyboardMarkup)
    
    @pytest.mark.asyncio
    async def test_handle_special_field_edit_selection(self, mock_update, mock_context):
        """Test handling special field (payment_amount) edit selection."""
        mock_update.callback_query.data = 'edit_field:payment_amount'
        
        result = await handle_field_edit_selection(mock_update, mock_context)
        
        assert result == EditStates.TEXT_INPUT
        assert mock_context.user_data['editing_field'] == 'payment_amount'
        
        # Should prompt for number input
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Отправьте сумму платежа' in message_text
        assert 'только цифры' in message_text


class TestHandleTextFieldInput:
    """Test handle_text_field_input function."""
    
    @pytest.mark.asyncio
    async def test_handle_text_input_valid_text_field(self, mock_update, mock_context):
        """Test handling valid text input for text field."""
        mock_context.user_data['editing_field'] = 'full_name_ru'
        mock_update.message.text = 'Петр Петров'
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['full_name_ru'] == 'Петр Петров'
        assert mock_context.user_data['editing_field'] is None
        
        # Should confirm change and return to edit menu
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]['text']
        assert 'обновлено' in message_text
    
    @pytest.mark.asyncio
    async def test_handle_text_input_valid_number_field(self, mock_update, mock_context):
        """Test handling valid numeric input for payment amount."""
        mock_context.user_data['editing_field'] = 'payment_amount'
        mock_update.message.text = '1500'
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['payment_amount'] == 1500
    
    @pytest.mark.asyncio
    async def test_handle_text_input_invalid_number_field(self, mock_update, mock_context):
        """Test handling invalid numeric input shows error."""
        mock_context.user_data['editing_field'] = 'payment_amount'
        mock_update.message.text = 'not_a_number'
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        assert result == EditStates.TEXT_INPUT  # Stay in input state
        assert 'payment_amount' not in mock_context.user_data['editing_changes']
        
        # Should show error message
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]['text']
        assert 'Ошибка' in message_text
        assert 'цифры' in message_text
    
    @pytest.mark.asyncio
    async def test_handle_text_input_invalid_date_field(self, mock_update, mock_context):
        """Test handling invalid date input shows error."""
        mock_context.user_data['editing_field'] = 'payment_date'
        mock_update.message.text = 'invalid-date'
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        assert result == EditStates.TEXT_INPUT  # Stay in input state
        assert 'payment_date' not in mock_context.user_data['editing_changes']
        
        # Should show error message
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]['text']
        assert 'Ошибка' in message_text
        assert 'ГГГГ-ММ-ДД' in message_text


class TestHandleButtonFieldSelection:
    """Test handle_button_field_selection function."""
    
    @pytest.mark.asyncio
    async def test_handle_button_selection_gender(self, mock_update, mock_context):
        """Test handling gender button selection."""
        mock_context.user_data['editing_field'] = 'gender'
        mock_update.callback_query.data = 'select_value:F'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['gender'] == Gender.FEMALE
        assert mock_context.user_data['editing_field'] is None
        
        # Should confirm change
        mock_update.callback_query.message.edit_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_button_selection_size(self, mock_update, mock_context):
        """Test handling size button selection."""
        mock_context.user_data['editing_field'] = 'size'
        mock_update.callback_query.data = 'select_value:XL'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['size'] == Size.XL
    
    @pytest.mark.asyncio
    async def test_handle_button_selection_invalid_value(self, mock_update, mock_context):
        """Test handling invalid button value shows error."""
        mock_context.user_data['editing_field'] = 'gender'
        mock_update.callback_query.data = 'select_value:INVALID'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        assert result == EditStates.BUTTON_SELECTION  # Stay in selection state
        assert 'gender' not in mock_context.user_data['editing_changes']


class TestCancelEditing:
    """Test cancel_editing function."""
    
    @pytest.mark.asyncio
    async def test_cancel_editing_clears_state(self, mock_update, mock_context):
        """Test canceling editing clears all editing state."""
        mock_context.user_data['editing_changes'] = {'full_name_ru': 'Changed Name'}
        mock_context.user_data['editing_field'] = 'full_name_ru'
        
        # Import the SearchStates from search_handlers for return state
        from src.bot.handlers.search_handlers import SearchStates
        result = await cancel_editing(mock_update, mock_context)
        
        assert result == SearchStates.SHOWING_RESULTS
        assert mock_context.user_data['editing_changes'] == {}
        assert mock_context.user_data['editing_field'] is None
        
        # Should show cancellation message
        mock_update.callback_query.message.edit_text.assert_called()


class TestSaveChanges:
    """Test save_changes function."""
    
    @pytest.mark.asyncio
    async def test_save_changes_with_no_changes(self, mock_update, mock_context):
        """Test saving with no changes shows message."""
        mock_context.user_data['editing_changes'] = {}
        
        from src.bot.handlers.search_handlers import SearchStates
        result = await save_changes(mock_update, mock_context)
        
        assert result == SearchStates.SHOWING_RESULTS
        
        # Should show no changes message
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Нет изменений' in message_text
    
    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_save_changes_with_changes_success(self, mock_get_repo, mock_update, mock_context):
        """Test successful save with changes."""
        mock_context.user_data['editing_changes'] = {
            'full_name_ru': 'Новое Имя',
            'gender': Gender.FEMALE
        }
        
        # Mock repository
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(return_value=True)
        mock_get_repo.return_value = mock_repo
        
        from src.bot.handlers.search_handlers import SearchStates
        result = await save_changes(mock_update, mock_context)
        
        assert result == SearchStates.SHOWING_RESULTS
        
        # Should call repository update
        mock_repo.update_by_id.assert_called_once()
        
        # Should show success message
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Изменения сохранены' in message_text
        
        # Should clear editing state
        assert mock_context.user_data['editing_changes'] == {}
    
    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_save_changes_repository_error(self, mock_get_repo, mock_update, mock_context):
        """Test save with repository error shows error message."""
        mock_context.user_data['editing_changes'] = {'full_name_ru': 'Новое Имя'}
        
        # Mock repository error
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(side_effect=Exception("DB Error"))
        mock_get_repo.return_value = mock_repo
        
        from src.bot.handlers.search_handlers import SearchStates
        result = await save_changes(mock_update, mock_context)
        
        assert result == SearchStates.SHOWING_RESULTS
        
        # Should show error message
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'ошибка' in message_text


class TestSaveConfirmation:
    """Test save confirmation workflow."""
    
    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_save_confirmation_shows_pending_changes(self, mock_get_repo, mock_update, mock_context):
        """Test that save confirmation shows all pending changes before save."""
        participant = Participant(
            record_id="rec123",
            full_name_ru="Тест Участник",
            role=Role.CANDIDATE
        )
        changes = {
            'full_name_ru': 'Новое Имя', 
            'role': Role.TEAM,
            'payment_amount': 500
        }
        mock_context.user_data['editing_changes'] = changes
        mock_context.user_data['current_participant'] = participant
        
        from src.bot.handlers.edit_participant_handlers import show_save_confirmation
        
        result = await show_save_confirmation(mock_update, mock_context)
        
        # Should show confirmation with changes summary
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        
        assert 'подтвердить' in message_text.lower()
        assert 'Новое Имя' in message_text  # Should show new value
        assert 'TEAM' in message_text  # Should show role change
        assert '500' in message_text  # Should show payment amount
    
    @pytest.mark.asyncio 
    async def test_save_confirmation_no_changes(self, mock_update, mock_context):
        """Test save confirmation with no changes."""
        mock_context.user_data['editing_changes'] = {}
        mock_context.user_data['current_participant'] = None
        
        from src.bot.handlers.edit_participant_handlers import show_save_confirmation
        
        result = await show_save_confirmation(mock_update, mock_context)
        
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'нет изменений' in message_text.lower()


class TestErrorHandlingWithRetry:
    """Test error handling and retry functionality."""
    
    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_save_with_retry_option_on_failure(self, mock_get_repo, mock_update, mock_context):
        """Test that save failure shows retry option."""
        participant = Participant(record_id="rec123", full_name_ru="Test")
        changes = {'full_name_ru': 'New Name'}
        mock_context.user_data['editing_changes'] = changes
        mock_context.user_data['current_participant'] = participant
        
        # Mock repository failure
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(return_value=False)
        mock_get_repo.return_value = mock_repo
        
        from src.bot.handlers.edit_participant_handlers import save_changes
        
        result = await save_changes(mock_update, mock_context)
        
        # Should show error with retry button
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        
        # Check message has retry option
        reply_markup = call_args[1]['reply_markup']
        buttons = reply_markup.inline_keyboard
        
        # Should have retry button
        retry_found = any(
            any('повтор' in btn.text.lower() or 'retry' in btn.callback_data.lower() 
                for btn in row) 
            for row in buttons
        )
        assert retry_found, "Should have retry button in keyboard"
    
    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_retry_save_operation(self, mock_get_repo, mock_update, mock_context):
        """Test retry save operation after previous failure."""
        participant = Participant(record_id="rec123", full_name_ru="Test")
        changes = {'full_name_ru': 'New Name'}
        mock_context.user_data['editing_changes'] = changes
        mock_context.user_data['current_participant'] = participant
        
        # Mock repository success on retry
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(return_value=True)
        mock_get_repo.return_value = mock_repo
        
        from src.bot.handlers.edit_participant_handlers import retry_save
        
        result = await retry_save(mock_update, mock_context)
        
        # Should retry and succeed
        mock_repo.update_by_id.assert_called_once()
        
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'сохранен' in message_text.lower()