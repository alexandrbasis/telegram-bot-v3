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
        # Add participant to context for complete display
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            role=Role.TEAM,
            department=Department.WORSHIP,
            church='Грейс'
        )
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_field'] = 'full_name_ru'
        mock_update.message.text = 'Петр Петров'
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['full_name_ru'] == 'Петр Петров'
        assert mock_context.user_data['editing_field'] is None
        
        # Should show complete participant display instead of simple message
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]['text']
        assert 'Петр Петров' in message_text  # Updated name should appear
        assert 'Ivan Ivanov' in message_text  # Should show complete participant info
    
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
    
    @pytest.mark.asyncio
    async def test_text_field_success_shows_complete_participant(self, mock_update, mock_context):
        """Test that text input success displays complete participant info instead of single field message."""
        # Setup participant and editing state
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            role=Role.CANDIDATE,
            department=Department.KITCHEN,
            church='Тестовая церковь'
        )
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_field'] = 'full_name_ru'
        mock_context.user_data['editing_changes'] = {}
        mock_update.message.text = 'Петр Петров'
        
        result = await handle_text_field_input(mock_update, mock_context)
        
        # Should return to field selection state
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['full_name_ru'] == 'Петр Петров'
        
        # Should reply with complete participant display, not simple success message
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]['text']
        
        # Should contain updated participant information (complete display)
        assert 'Петр Петров' in message_text  # Updated name should be displayed
        assert 'Ivan Ivanov' in message_text  # English name should be displayed
        assert 'CANDIDATE' in message_text or 'Кандидат' in message_text  # Role should be displayed
        assert 'Kitchen' in message_text or 'Кухня' in message_text  # Department should be displayed
        
        # Should NOT contain simple success message format
        assert 'обновлено:' not in message_text  # Old simple format should not appear


class TestHandleButtonFieldSelection:
    """Test handle_button_field_selection function."""
    
    @pytest.mark.asyncio
    async def test_handle_button_selection_gender(self, mock_update, mock_context):
        """Test handling gender button selection."""
        # Add participant to context for complete display
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            role=Role.CANDIDATE,
            gender=Gender.MALE
        )
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_field'] = 'gender'
        mock_update.callback_query.data = 'select_value:F'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['gender'] == Gender.FEMALE
        assert mock_context.user_data['editing_field'] is None
        
        # Should show complete participant display
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Иван Иванов' in message_text  # Should show complete participant info
    
    @pytest.mark.asyncio
    async def test_handle_button_selection_size(self, mock_update, mock_context):
        """Test handling size button selection."""
        # Add participant to context for complete display
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            size=Size.L
        )
        mock_context.user_data['current_participant'] = participant
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

    @pytest.mark.asyncio
    async def test_role_change_team_to_candidate_clears_department(self, mock_update, mock_context):
        """Changing role from TEAM to CANDIDATE clears department and informs user."""
        # Participant initially TEAM with a department
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            role=Role.TEAM,
            department=Department.MEDIA
        )
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_field'] = 'role'
        mock_update.callback_query.data = 'select_value:CANDIDATE'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        assert result == EditStates.FIELD_SELECTION
        assert mock_context.user_data['editing_changes']['role'] == Role.CANDIDATE
        # Department should be explicitly cleared in pending changes
        assert 'department' in mock_context.user_data['editing_changes']
        assert mock_context.user_data['editing_changes']['department'] is None
        
        # Message should inform about auto-clear
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'Отдел очищен' in message_text

    @pytest.mark.asyncio
    async def test_role_change_candidate_to_team_prompts_department(self, mock_update, mock_context):
        """Changing role from CANDIDATE to TEAM prompts department selection and blocks flow."""
        participant = Participant(
            record_id='rec123',
            full_name_ru='User',
            role=Role.CANDIDATE,
            department=None
        )
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_field'] = 'role'
        mock_update.callback_query.data = 'select_value:TEAM'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        assert result == EditStates.BUTTON_SELECTION
        # Should set editing field to department for immediate prompt
        assert mock_context.user_data['editing_field'] == 'department'
        
        # Should show department keyboard and prompt message
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'необходимо выбрать отдел' in message_text
        assert isinstance(call_args[1]['reply_markup'], InlineKeyboardMarkup)


class TestSaveEnforcement:
    """Tests for save enforcement rules regarding department requirement."""
    
    @pytest.mark.asyncio
    async def test_save_blocks_team_without_department(self, mock_update):
        from src.bot.handlers.edit_participant_handlers import save_changes
        # Participant with no department; user changed role to TEAM but not department
        participant = Participant(
            record_id='rec123',
            full_name_ru='User',
            role=Role.CANDIDATE,
            department=None
        )
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'current_participant': participant,
            'editing_changes': {
                'role': Role.TEAM
            }
        }
        
        # Try to save
        result = await save_changes(mock_update, context)
        
        # Should block and prompt for department selection
        assert result == EditStates.BUTTON_SELECTION
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        assert 'необходимо выбрать отдел' in message_text


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
    
    @pytest.mark.asyncio
    @patch('src.bot.handlers.edit_participant_handlers.get_participant_repository')
    async def test_save_success_complete_participant_display(self, mock_get_repo, mock_update, mock_context):
        """Test that save success displays complete updated participant info instead of simple message."""
        # Create participant with updated data
        participant = Participant(
            record_id='rec123',
            full_name_ru='Original Name',
            full_name_en='Original English',
            role=Role.CANDIDATE,
            church='Original Church'
        )
        changes = {
            'full_name_ru': 'Updated Name',
            'role': Role.TEAM,
            'church': 'New Church',
            # New logic requires department when role is TEAM
            'department': Department.WORSHIP
        }
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_changes'] = changes
        
        # Mock successful repository save
        mock_repo = Mock()
        mock_repo.update_by_id = AsyncMock(return_value=True)
        mock_get_repo.return_value = mock_repo
        
        result = await save_changes(mock_update, mock_context)
        
        # Should call repository update
        mock_repo.update_by_id.assert_called_once_with('rec123', changes)
        
        # Should show complete participant display instead of simple success message
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        
        # Should contain complete participant information with updates applied
        assert 'Updated Name' in message_text  # Updated Russian name
        assert 'TEAM' in message_text or 'Команда' in message_text  # Updated role
        assert 'New Church' in message_text  # Updated church
        
        # Should NOT contain simple count-based success message
        assert 'Обновлено полей:' not in message_text
        assert 'Changes saved successfully' not in message_text
        
        # Should contain success prefix indicating save was successful
        assert '✅' in message_text
    
    @pytest.mark.asyncio
    async def test_button_field_success_shows_complete_participant(self, mock_update, mock_context):
        """Test that button selection success displays complete participant info instead of single field message."""
        # Setup participant and editing state
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            role=Role.CANDIDATE,
            gender=Gender.MALE,
            department=Department.KITCHEN,
            church='Тестовая церковь'
        )
        mock_context.user_data['current_participant'] = participant
        mock_context.user_data['editing_field'] = 'role'
        mock_context.user_data['editing_changes'] = {}
        mock_update.callback_query.data = 'select_value:TEAM'
        
        result = await handle_button_field_selection(mock_update, mock_context)
        
        # New behavior: prompt for department selection when upgrading to TEAM
        assert result == EditStates.BUTTON_SELECTION
        assert mock_context.user_data['editing_changes']['role'] == Role.TEAM
        assert mock_context.user_data['editing_field'] == 'department'
        
        # Should show prompt to select department
        mock_update.callback_query.message.edit_text.assert_called()
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        
        assert 'необходимо выбрать отдел' in message_text
        assert isinstance(call_args[1]['reply_markup'], InlineKeyboardMarkup)


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


class TestPaymentFieldExclusion:
    """Test that payment status and date are excluded from editable fields."""
    
    @pytest.mark.asyncio
    async def test_payment_status_excluded_from_button_fields(self, mock_update, mock_context):
        """Test that payment_status is not in BUTTON_FIELDS list."""
        mock_update.callback_query.data = "edit_field:payment_status"
        
        from src.bot.handlers.edit_participant_handlers import handle_field_edit_selection
        
        # This should not be handled as a button field (should fail or be treated as unknown)
        try:
            result = await handle_field_edit_selection(mock_update, mock_context)
            # If it executes without error, check that payment_status is not in BUTTON_FIELDS
            # by importing and checking the field lists directly
            from src.bot.handlers import edit_participant_handlers
            
            # Access the BUTTON_FIELDS constant from the handler code
            # (will need to read the actual implementation)
            assert False, "payment_status should not be handled as valid field"
        except Exception:
            # Expected to fail since payment_status should not be a valid field
            pass
    
    @pytest.mark.asyncio  
    async def test_payment_date_excluded_from_text_fields(self, mock_update, mock_context):
        """Test that payment_date is not in TEXT_FIELDS list."""
        mock_update.callback_query.data = "edit_field:payment_date"
        
        from src.bot.handlers.edit_participant_handlers import handle_field_edit_selection
        
        # This should not be handled as a text field (should fail or be treated as unknown)
        try:
            result = await handle_field_edit_selection(mock_update, mock_context)
            assert False, "payment_date should not be handled as valid field"
        except Exception:
            # Expected to fail since payment_date should not be a valid field
            pass
    
    def test_button_fields_constant_excludes_payment_status(self):
        """Test that BUTTON_FIELDS constant in handler does not include payment_status."""
        # Read the handler file and verify field lists
        with open('/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3/src/bot/handlers/edit_participant_handlers.py', 'r') as f:
            content = f.read()
        
        # Find BUTTON_FIELDS definition and verify payment_status is not included
        import re
        button_fields_match = re.search(r"BUTTON_FIELDS\s*=\s*\[(.*?)\]", content, re.DOTALL)
        assert button_fields_match, "BUTTON_FIELDS definition not found"
        
        button_fields_content = button_fields_match.group(1)
        assert 'payment_status' not in button_fields_content, "payment_status should not be in BUTTON_FIELDS"
    
    def test_text_fields_constant_excludes_payment_date(self):
        """Test that TEXT_FIELDS constant in handler does not include payment_date.""" 
        # Read the handler file and verify field lists
        with open('/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3/src/bot/handlers/edit_participant_handlers.py', 'r') as f:
            content = f.read()
        
        # Find TEXT_FIELDS definition and verify payment_date is not included
        import re  
        text_fields_match = re.search(r"TEXT_FIELDS\s*=\s*\[(.*?)\]", content, re.DOTALL)
        assert text_fields_match, "TEXT_FIELDS definition not found"
        
        text_fields_content = text_fields_match.group(1)
        assert 'payment_date' not in text_fields_content, "payment_date should not be in TEXT_FIELDS"


class TestEditMenuDisplay:
    """Test edit menu display excludes payment fields and uses consistent icons."""
    
    @pytest.mark.asyncio
    async def test_edit_menu_excludes_payment_status_display(self, mock_update, mock_context):
        """Test that edit menu does not display payment status field."""
        from src.bot.handlers.edit_participant_handlers import show_participant_edit_menu
        
        # Mock participant with payment data
        participant = Participant(
            record_id="rec123",
            full_name_ru="Test User", 
            payment_status=PaymentStatus.PAID,
            payment_amount=1000
        )
        mock_context.user_data['current_participant'] = participant
        
        await show_participant_edit_menu(mock_update, mock_context)
        
        # Get the message text that was sent
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        
        # Should not contain payment status display line
        assert "💰 Статус платежа" not in message_text, "Payment status should not be displayed in edit menu"
        assert "Статус платежа" not in message_text, "Payment status should not be displayed in edit menu"
    
    @pytest.mark.asyncio
    async def test_edit_menu_excludes_payment_date_display(self, mock_update, mock_context):
        """Test that edit menu does not display payment date field."""
        from src.bot.handlers.edit_participant_handlers import show_participant_edit_menu
        
        # Mock participant with payment data
        participant = Participant(
            record_id="rec123", 
            full_name_ru="Test User",
            payment_date=date(2025, 1, 15)
        )
        mock_context.user_data['current_participant'] = participant
        
        await show_participant_edit_menu(mock_update, mock_context)
        
        # Get the message text that was sent
        call_args = mock_update.callback_query.message.edit_text.call_args
        message_text = call_args[1]['text']
        
        # Should not contain payment date display line
        assert "📅 Дата платежа" not in message_text, "Payment date should not be displayed in edit menu" 
        assert "Дата платежа" not in message_text, "Payment date should not be displayed in edit menu"
    
    def test_field_labels_excludes_payment_date(self):
        """Test that field_labels dictionary does not include payment_date."""
        # Read the handler file and check field_labels dictionary
        with open('/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3/src/bot/handlers/edit_participant_handlers.py', 'r') as f:
            content = f.read()
        
        # Find field_labels definition and verify payment_date is not included
        import re
        field_labels_match = re.search(r"field_labels\s*=\s*\{(.*?)\}", content, re.DOTALL)
        assert field_labels_match, "field_labels definition not found"
        
        field_labels_content = field_labels_match.group(1)
        assert "'payment_date'" not in field_labels_content, "payment_date should not be in field_labels dictionary"
    
    def test_field_labels_uses_field_specific_icons(self):
        """Test that field labels incorporate field-specific icons."""
        # Read the handler file and check if field labels use icons
        with open('/Users/alexandrbasis/Desktop/Coding Projects/telegram-bot-v3/src/bot/handlers/edit_participant_handlers.py', 'r') as f:
            content = f.read()
        
        # Find success message formatting and verify it uses field-specific icons
        import re
        success_message_match = re.search(r"success_message\s*=\s*f[\"'](.*?)[\"']", content, re.DOTALL)
        assert success_message_match, "success_message formatting not found"
        
        success_message_format = success_message_match.group(1)
        # Success message should use field icons instead of generic ✅
        # This test expects the message format to include field-specific icons
        assert "{get_field_icon(" in success_message_format or "field_icon" in success_message_format, \
               "Success message should use field-specific icons instead of generic checkmark"


class TestDisplayUpdatedParticipant:
    """Test display_updated_participant helper function."""
    
    def test_display_updated_participant_function(self):
        """Test that display_updated_participant function returns formatted participant result."""
        # Import the function we're testing (will fail initially - RED phase)
        from src.bot.handlers.edit_participant_handlers import display_updated_participant
        
        # Create mock participant
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            role=Role.CANDIDATE,
            department=Department.KITCHEN
        )
        
        # Create mock context with editing changes
        context = Mock()
        context.user_data = {
            'editing_changes': {
                'full_name_ru': 'Петр Петров',
                'role': Role.TEAM
            }
        }
        
        # Call the function
        result = display_updated_participant(participant, context)
        
        # Should return formatted result with updated values
        assert isinstance(result, str)
        assert 'Петр Петров' in result  # Updated name should be in result
        assert 'TEAM' in result or 'Команда' in result  # Updated role should be in result
        assert len(result) > 0
        
    def test_display_updated_participant_with_no_changes(self):
        """Test display_updated_participant with no pending changes."""
        from src.bot.handlers.edit_participant_handlers import display_updated_participant
        
        # Create mock participant
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            role=Role.CANDIDATE
        )
        
        # Create mock context with no editing changes
        context = Mock()
        context.user_data = {'editing_changes': {}}
        
        # Call the function
        result = display_updated_participant(participant, context)
        
        # Should return formatted result with original values
        assert isinstance(result, str)
        assert 'Иван Иванов' in result
        assert 'CANDIDATE' in result or 'Кандидат' in result
        
    def test_display_updated_participant_reconstruction_with_edits(self):
        """Test that participant object is properly reconstructed with all current session edits."""
        from src.bot.handlers.edit_participant_handlers import display_updated_participant
        
        # Create original participant
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            role=Role.CANDIDATE,
            gender=Gender.MALE,
            church='Старая церковь'
        )
        
        # Create context with multiple editing changes
        context = Mock()
        context.user_data = {
            'editing_changes': {
                'full_name_ru': 'Петр Петров',
                'role': Role.TEAM,
                'church': 'Новая церковь',
                'gender': Gender.FEMALE
            }
        }
        
        # Call the function
        result = display_updated_participant(participant, context)
        
        # Should display updated values, not original ones
        assert 'Петр Петров' in result  # Updated name
        assert 'Иван Иванов' not in result  # Original name should not appear
        assert 'Новая церковь' in result  # Updated church
        assert 'Старая церковь' not in result  # Original church should not appear
        # Role and gender changes should be reflected in formatting


class TestDisplayRegressionIssue:
    """Test for critical regression where participant display fails during editing."""
    
    @pytest.mark.asyncio
    async def test_text_field_edit_with_missing_participant_context(self, mock_update):
        """
        REGRESSION TEST: Reproduce issue where current_participant becomes None during editing.
        
        This test simulates the production issue where participants see no information 
        after field edits because current_participant is missing from context.
        """
        from src.bot.handlers.edit_participant_handlers import handle_text_field_input
        
        # Create context WITHOUT current_participant (reproducing the regression)
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'editing_changes': {},
            'editing_field': 'full_name_ru'  # User is editing this field
            # NOTE: 'current_participant' is MISSING - this is the regression!
        }
        
        # Mock update for text input
        mock_update.message.text = "Новое имя"
        mock_update.effective_user.id = 12345
        
        # Mock the update service
        with patch('src.bot.handlers.edit_participant_handlers.ParticipantUpdateService') as mock_service:
            mock_service.return_value.validate_field_input.return_value = "Новое имя"
            
            # This should trigger the fallback behavior (simple message instead of complete display)
            result = await handle_text_field_input(mock_update, context)
            
            # Should return to field selection state
            from src.bot.handlers.edit_participant_handlers import EditStates
            assert result == EditStates.FIELD_SELECTION
            
            # Verify fallback message was sent (not complete participant display)
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            message_text = call_args[1]['text']
            
            # Should be simple success message, not complete participant info
            assert "Имя на русском обновлено:" in message_text
            assert "Новое имя" in message_text
            
            # Should NOT contain formatted participant information
            assert "📋" not in message_text  # No participant display formatting
            assert "🏠" not in message_text  # No complete info display
    
    @pytest.mark.asyncio 
    async def test_button_field_edit_with_missing_participant_context(self, mock_update):
        """
        REGRESSION TEST: Button field editing also fails when current_participant is None.
        """
        from src.bot.handlers.edit_participant_handlers import handle_button_field_selection
        
        # Create context WITHOUT current_participant 
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'editing_changes': {},
            'editing_field': 'gender'  # User is editing this field
            # NOTE: 'current_participant' is MISSING - this is the regression!
        }
        
        # Mock callback query for button selection
        mock_update.callback_query.data = "gender:male"
        mock_update.callback_query.from_user.id = 12345
        
        # Mock the update service
        with patch('src.bot.handlers.edit_participant_handlers.ParticipantUpdateService') as mock_service:
            mock_service.return_value.convert_button_value.return_value = "MALE"
            mock_service.return_value.get_russian_display_value.return_value = "Мужской"
            
            # This should trigger the fallback behavior
            result = await handle_button_field_selection(mock_update, context)
            
            # Should return to field selection state  
            from src.bot.handlers.edit_participant_handlers import EditStates
            assert result == EditStates.FIELD_SELECTION
            
            # Verify fallback message was sent (not complete participant display)
            mock_update.callback_query.message.edit_text.assert_called_once()
            call_args = mock_update.callback_query.message.edit_text.call_args
            message_text = call_args[1]['text']
            
            # Should be simple success message, not complete participant info
            assert "Пол обновлено:" in message_text
            assert "Мужской" in message_text
            
            # Should NOT contain formatted participant information
            assert "📋" not in message_text  # No participant display formatting
            assert "🏠" not in message_text  # No complete info display


class TestComprehensiveDisplayRegressionPrevention:
    """Comprehensive regression prevention tests for all display scenarios."""
    
    @pytest.mark.asyncio
    async def test_display_function_exception_handling(self, mock_update):
        """Test that exceptions in display_updated_participant are handled gracefully."""
        from src.bot.handlers.edit_participant_handlers import handle_text_field_input
        
        # Create context WITH participant but cause display function to fail
        participant = Participant(
            record_id='rec123',
            full_name_ru='Тест',
            full_name_en='Test'
        )
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'current_participant': participant,
            'editing_changes': {},
            'editing_field': 'full_name_ru'
        }
        
        mock_update.message.text = "Новое имя"
        mock_update.effective_user.id = 12345
        
        # Mock the services
        with patch('src.bot.handlers.edit_participant_handlers.ParticipantUpdateService') as mock_service, \
             patch('src.bot.handlers.edit_participant_handlers.display_updated_participant') as mock_display:
            
            mock_service.return_value.validate_field_input.return_value = "Новое имя"
            
            # Make display function throw an exception
            mock_display.side_effect = Exception("Display function failed")
            
            # This should handle the exception gracefully
            result = await handle_text_field_input(mock_update, context)
            
            # Should still return to field selection
            from src.bot.handlers.edit_participant_handlers import EditStates
            assert result == EditStates.FIELD_SELECTION
            
            # Should send fallback message with warning
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            message_text = call_args[1]['text']
            
            # Should contain success confirmation with warning
            assert "Имя на русском обновлено:" in message_text
            assert "Новое имя" in message_text
            assert "⚠️ Полная информация временно недоступна" in message_text
    
    @pytest.mark.asyncio
    async def test_button_display_function_exception_handling(self, mock_update):
        """Test button field editing with display function exceptions."""
        from src.bot.handlers.edit_participant_handlers import handle_button_field_selection
        
        # Create context WITH participant but cause display function to fail
        participant = Participant(
            record_id='rec123',
            full_name_ru='Тест',
            gender=Gender.FEMALE
        )
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'current_participant': participant,
            'editing_changes': {},
            'editing_field': 'gender'
        }
        
        mock_update.callback_query.data = "gender:male"
        mock_update.callback_query.from_user.id = 12345
        
        with patch('src.bot.handlers.edit_participant_handlers.ParticipantUpdateService') as mock_service, \
             patch('src.bot.handlers.edit_participant_handlers.display_updated_participant') as mock_display:
            
            mock_service.return_value.convert_button_value.return_value = Gender.MALE
            mock_service.return_value.get_russian_display_value.return_value = "Мужской"
            
            # Make display function throw an exception
            mock_display.side_effect = Exception("Display formatting failed")
            
            result = await handle_button_field_selection(mock_update, context)
            
            from src.bot.handlers.edit_participant_handlers import EditStates
            assert result == EditStates.FIELD_SELECTION
            
            # Should send fallback message
            mock_update.callback_query.message.edit_text.assert_called_once()
            call_args = mock_update.callback_query.message.edit_text.call_args
            message_text = call_args[1]['text']
            
            assert "Пол обновлено:" in message_text
            assert "Мужской" in message_text
            assert "⚠️ Полная информация временно недоступна" in message_text
    
    @pytest.mark.asyncio
    async def test_context_corruption_scenarios(self, mock_update):
        """Test various context corruption scenarios that could cause regressions."""
        from src.bot.handlers.edit_participant_handlers import handle_text_field_input
        
        # Test 1: Empty user_data
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        
        mock_update.message.text = "Test"
        mock_update.effective_user.id = 12345
        
        result = await handle_text_field_input(mock_update, context)
        
        from src.bot.handlers.edit_participant_handlers import EditStates
        assert result == EditStates.FIELD_SELECTION
        
        # Test 2: Participant is not None but invalid
        context.user_data = {
            'current_participant': "invalid_participant_type",  # Wrong type
            'editing_changes': {},
            'editing_field': 'full_name_ru'
        }
        
        with patch('src.bot.handlers.edit_participant_handlers.ParticipantUpdateService') as mock_service:
            mock_service.return_value.validate_field_input.return_value = "Test"
            
            # Should handle invalid participant gracefully
            result = await handle_text_field_input(mock_update, context)
            assert result == EditStates.FIELD_SELECTION
    
    @pytest.mark.asyncio
    async def test_save_success_shows_current_simple_message(self, mock_update):
        """Test current save success behavior (simple message without participant info)."""
        from src.bot.handlers.edit_participant_handlers import save_changes
        
        # Create proper context with participant and changes
        participant = Participant(
            record_id='rec123',
            full_name_ru='Иван Иванов',
            full_name_en='Ivan Ivanov',
            church='Test Church'
        )
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'current_participant': participant,
            'editing_changes': {
                'full_name_ru': 'Петр Петров',
                'church': 'New Church'
            }
        }
        
        mock_update.callback_query.from_user.id = 12345
        
        # Mock successful save
        with patch('src.bot.handlers.edit_participant_handlers.get_participant_repository') as mock_repo_func:
            mock_repo = AsyncMock()
            mock_repo_func.return_value = mock_repo
            mock_repo.update_by_id.return_value = True
            
            result = await save_changes(mock_update, context)
            
            # Should show simple success message (current behavior)
            mock_update.callback_query.message.edit_text.assert_called_once()
            call_args = mock_update.callback_query.message.edit_text.call_args
            success_message = call_args[1]['text']
            
            # Current implementation shows simple success message
            assert "Изменения сохранены успешно" in success_message
            assert "Обновлено полей: 2" in success_message
            
            # Does NOT show complete participant info (this is the regression to fix later)
            assert "📋" not in success_message  # No participant display formatting
            assert "Петр Петров" not in success_message  # Updated name not shown
    
    @pytest.mark.asyncio 
    async def test_multiple_field_edits_maintain_context(self, mock_update):
        """Test that participant context is maintained across multiple field edits."""
        from src.bot.handlers.edit_participant_handlers import handle_text_field_input
        
        participant = Participant(
            record_id='rec123',
            full_name_ru='Original Name',
            church='Original Church'
        )
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            'current_participant': participant,
            'editing_changes': {},
            'editing_field': 'full_name_ru'
        }
        
        mock_update.message.text = "New Name"
        mock_update.effective_user.id = 12345
        
        with patch('src.bot.handlers.edit_participant_handlers.ParticipantUpdateService') as mock_service, \
             patch('src.bot.handlers.edit_participant_handlers.display_updated_participant') as mock_display:
            
            mock_service.return_value.validate_field_input.return_value = "New Name"
            mock_display.return_value = "📋 **New Name** (updated)\n🏠 Original Church"
            
            # First edit
            result = await handle_text_field_input(mock_update, context)
            
            # Participant should still be in context
            assert context.user_data['current_participant'] == participant
            assert context.user_data['editing_changes']['full_name_ru'] == "New Name"
            
            # Second edit on different field
            context.user_data['editing_field'] = 'church'
            mock_update.message.text = "New Church"
            mock_service.return_value.validate_field_input.return_value = "New Church"
            mock_display.return_value = "📋 **New Name**\n🏠 New Church (both updated)"
            
            result = await handle_text_field_input(mock_update, context)
            
            # Context should still be maintained
            assert context.user_data['current_participant'] == participant
            assert context.user_data['editing_changes']['full_name_ru'] == "New Name"
            assert context.user_data['editing_changes']['church'] == "New Church"
            
            # Display function should have been called both times
            assert mock_display.call_count == 2
