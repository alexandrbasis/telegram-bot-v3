"""
Unit tests for edit keyboards functionality.

Tests keyboard generation for different field types and validation of button layouts.
"""

import pytest
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.keyboards.edit_keyboards import (
    create_participant_edit_keyboard,
    create_field_edit_keyboard,
    create_save_cancel_keyboard
)
from src.models.participant import Gender, Size, Role, Department, PaymentStatus


class TestCreateParticipantEditKeyboard:
    """Test create_participant_edit_keyboard function."""
    
    def test_create_participant_edit_keyboard_structure(self):
        """Test that participant edit keyboard has all field buttons."""
        keyboard = create_participant_edit_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        # Check that we have buttons for all 13 fields
        expected_fields = [
            'full_name_ru', 'full_name_en', 'church', 'country_and_city',
            'contact_information', 'submitted_by', 'gender', 'size', 
            'role', 'department', 'payment_status', 'payment_amount', 'payment_date'
        ]
        
        button_data = [btn.callback_data for btn in all_buttons if btn.callback_data.startswith('edit_field:')]
        field_names = [data.split(':')[1] for data in button_data]
        
        for field in expected_fields:
            assert field in field_names, f"Missing button for field: {field}"
    
    def test_create_participant_edit_keyboard_has_save_cancel_buttons(self):
        """Test that keyboard includes save and cancel buttons."""
        keyboard = create_participant_edit_keyboard()
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons]
        
        assert 'save_changes' in button_data
        assert 'cancel_edit' in button_data
    
    def test_create_participant_edit_keyboard_button_text_in_russian(self):
        """Test that field edit buttons have Russian labels."""
        keyboard = create_participant_edit_keyboard()
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        # Check some key button texts
        button_texts = [btn.text for btn in all_buttons]
        
        # Check for key Russian labels
        assert any("Имя (русское)" in text for text in button_texts)
        assert any("Пол" in text for text in button_texts)
        assert any("Размер" in text for text in button_texts)
        assert any("Церковь" in text for text in button_texts)


class TestCreateFieldEditKeyboard:
    """Test create_field_edit_keyboard function for different field types."""
    
    def test_create_gender_keyboard(self):
        """Test gender field keyboard has correct options."""
        keyboard = create_field_edit_keyboard('gender')
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        values = [data.split(':')[1] for data in button_data]
        
        assert 'M' in values
        assert 'F' in values
        
        # Check Russian labels
        button_texts = [btn.text for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        assert any("Мужской" in text for text in button_texts)
        assert any("Женский" in text for text in button_texts)
    
    def test_create_size_keyboard(self):
        """Test size field keyboard has all size options."""
        keyboard = create_field_edit_keyboard('size')
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        values = [data.split(':')[1] for data in button_data]
        
        expected_sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL']
        for size in expected_sizes:
            assert size in values
    
    def test_create_role_keyboard(self):
        """Test role field keyboard has role options."""
        keyboard = create_field_edit_keyboard('role')
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        values = [data.split(':')[1] for data in button_data]
        
        assert 'CANDIDATE' in values
        assert 'TEAM' in values
        
        # Check Russian labels
        button_texts = [btn.text for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        assert any("Кандидат" in text for text in button_texts)
        assert any("Команда" in text for text in button_texts)
    
    def test_create_department_keyboard(self):
        """Test department field keyboard has all department options."""
        keyboard = create_field_edit_keyboard('department')
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        values = [data.split(':')[1] for data in button_data]
        
        expected_departments = [
            'ROE', 'Chapel', 'Setup', 'Palanka', 'Administration',
            'Kitchen', 'Decoration', 'Bell', 'Refreshment', 'Worship',
            'Media', 'Clergy', 'Rectorate'
        ]
        
        for dept in expected_departments:
            assert dept in values
    
    def test_create_payment_status_keyboard(self):
        """Test payment status field keyboard has payment options."""
        keyboard = create_field_edit_keyboard('payment_status')
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        values = [data.split(':')[1] for data in button_data]
        
        assert 'Paid' in values
        assert 'Partial' in values
        assert 'Unpaid' in values
        
        # Check Russian labels
        button_texts = [btn.text for btn in all_buttons if btn.callback_data.startswith('select_value:')]
        assert any("Оплачено" in text for text in button_texts)
        assert any("Частично" in text for text in button_texts)
        assert any("Не оплачено" in text for text in button_texts)
    
    def test_create_keyboard_unknown_field_raises_error(self):
        """Test that unknown field type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown field type"):
            create_field_edit_keyboard('unknown_field')
    
    def test_all_field_keyboards_have_cancel_button(self):
        """Test that all field keyboards include cancel button."""
        field_types = ['gender', 'size', 'role', 'department', 'payment_status']
        
        for field_type in field_types:
            keyboard = create_field_edit_keyboard(field_type)
            
            # Flatten keyboard to get all buttons
            all_buttons = []
            for row in keyboard.inline_keyboard:
                all_buttons.extend(row)
            
            button_data = [btn.callback_data for btn in all_buttons]
            assert 'cancel_edit' in button_data, f"Missing cancel button in {field_type} keyboard"


class TestCreateSaveCancelKeyboard:
    """Test create_save_cancel_keyboard function."""
    
    def test_create_save_cancel_keyboard_structure(self):
        """Test save/cancel keyboard has correct buttons."""
        keyboard = create_save_cancel_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_data = [btn.callback_data for btn in all_buttons]
        
        assert 'save_changes' in button_data
        assert 'cancel_edit' in button_data
    
    def test_create_save_cancel_keyboard_button_text(self):
        """Test save/cancel keyboard has Russian button text."""
        keyboard = create_save_cancel_keyboard()
        
        # Flatten keyboard to get all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        button_texts = [btn.text for btn in all_buttons]
        
        assert any("Сохранить" in text for text in button_texts)
        assert any("Отмена" in text for text in button_texts)
    
    def test_keyboard_layout_is_two_buttons_in_one_row(self):
        """Test that save/cancel buttons are in one row."""
        keyboard = create_save_cancel_keyboard()
        
        # Should have one row with two buttons
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 2