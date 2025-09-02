import asyncio
from unittest.mock import Mock, AsyncMock
from src.bot.handlers.edit_participant_handlers import handle_text_field_input, display_updated_participant
from src.models.participant import Participant, Gender, Role, Department
from telegram import Update, Message, User

# Create mock objects
update = Mock(spec=Update)
update.message = Mock(spec=Message)
update.message.reply_text = AsyncMock()
update.message.text = "Новое Имя"
update.effective_user = Mock(spec=User)
update.effective_user.id = 12345

# Create context with participant
context = Mock()
context.user_data = {
    'current_participant': Participant(
        record_id='rec123',
        full_name_ru='Иван Иванов',
        full_name_en='Ivan Ivanov',
        role=Role.CANDIDATE,
        department=Department.KITCHEN,
        gender=Gender.MALE
    ),
    'editing_changes': {},
    'editing_field': 'full_name_ru'
}

# Test the display function directly
result = display_updated_participant(context.user_data['current_participant'], context)
print("Display function output:")
print(result)
print("\n" + "="*50 + "\n")

# Now test the actual handler
async def test_handler():
    await handle_text_field_input(update, context)
    # Check what was sent to the user
    if update.message.reply_text.called:
        call_args = update.message.reply_text.call_args
        message_text = call_args[1].get('text', call_args[0][0] if call_args[0] else '')
        print("Message sent to user after text field edit:")
        print(message_text)
    else:
        print("ERROR: reply_text was not called!")

asyncio.run(test_handler())
