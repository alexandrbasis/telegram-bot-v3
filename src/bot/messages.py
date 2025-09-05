"""
Standardized bot messages for consistent user experience.

This module provides centralized message templates for all bot interactions,
ensuring consistent messaging across different handlers and features.
"""

from typing import Optional


class ErrorMessages:
    """Standardized error messages for user-facing errors."""
    
    # Input validation errors
    INVALID_ROOM_NUMBER = "❌ Пожалуйста, введите корректный номер комнаты (должен содержать цифры)."
    INVALID_FLOOR_NUMBER = "❌ Пожалуйста, введите корректный номер этажа (должен быть числом)."
    INVALID_INPUT_GENERIC = "❌ Некорректный ввод. Пожалуйста, попробуйте еще раз."
    
    # Search result errors
    NO_PARTICIPANTS_IN_ROOM = "❌ В комнате {room_number} участники не найдены."
    NO_PARTICIPANTS_ON_FLOOR = "❌ На этаже {floor} участники не найдены."
    NO_PARTICIPANTS_FOUND = "❌ Участники не найдены."
    PARTICIPANT_NOT_FOUND = "❌ Участник не найден."
    
    # API and network errors
    SEARCH_ERROR_GENERIC = "❌ Произошла ошибка при поиске. Попробуйте позже."
    API_ERROR_RETRY = "❌ Не удалось подключиться к базе данных. Проверьте подключение и попробуйте еще раз."
    NETWORK_TIMEOUT = "❌ Время ожидания истекло. Попробуйте еще раз или проверьте подключение к интернету."
    
    # Save/update errors
    SAVE_ERROR_GENERIC = "❌ Ошибка при сохранении изменений. Проверьте подключение и попробуйте еще раз."
    UPDATE_ERROR_GENERIC = "❌ Произошла ошибка при сохранении. Проверьте подключение и попробуйте еще раз."
    
    # System errors
    SYSTEM_ERROR_GENERIC = "❌ Произошла системная ошибка. Попробуйте еще раз."
    MAINTENANCE_MODE = "❌ Система временно недоступна для обслуживания. Попробуйте позже."

    @staticmethod
    def no_participants_in_room(room_number: str) -> str:
        """Format message for no participants found in specific room."""
        return ErrorMessages.NO_PARTICIPANTS_IN_ROOM.format(room_number=room_number)
    
    @staticmethod
    def no_participants_on_floor(floor: int) -> str:
        """Format message for no participants found on specific floor."""
        return ErrorMessages.NO_PARTICIPANTS_ON_FLOOR.format(floor=floor)

    @staticmethod
    def validation_error(field_name: str, value: str) -> str:
        """Format message for field validation errors."""
        return f"❌ Некорректное значение '{value}' для поля {field_name}. Пожалуйста, введите правильное значение."


class SuccessMessages:
    """Standardized success messages for positive user feedback."""
    
    # Search results
    PARTICIPANTS_FOUND_IN_ROOM = "🏠 Найдено участников в комнате {room_number}: {count}"
    PARTICIPANTS_FOUND_ON_FLOOR = "🏢 Найдено участников на этаже {floor}: {count}"
    SEARCH_COMPLETE = "✅ Поиск завершен."
    
    # Save/update success
    CHANGES_SAVED = "✅ Изменения сохранены."
    PARTICIPANT_UPDATED = "✅ Данные участника обновлены."
    
    # System operations
    OPERATION_COMPLETED = "✅ Операция выполнена успешно."

    @staticmethod
    def participants_found_in_room(room_number: str, count: int) -> str:
        """Format message for participants found in room."""
        return SuccessMessages.PARTICIPANTS_FOUND_IN_ROOM.format(room_number=room_number, count=count)
    
    @staticmethod
    def participants_found_on_floor(floor: int, count: int) -> str:
        """Format message for participants found on floor."""
        return SuccessMessages.PARTICIPANTS_FOUND_ON_FLOOR.format(floor=floor, count=count)


class InfoMessages:
    """Informational messages and prompts."""
    
    # Search prompts
    ENTER_ROOM_NUMBER = "Введите номер комнаты для поиска:"
    ENTER_FLOOR_NUMBER = "Введите номер этажа для поиска:"
    SEARCHING_ROOM = "🔍 Ищу участников в комнате {room_number}..."
    SEARCHING_FLOOR = "🔍 Ищу участников на этаже {floor}..."
    
    # System status
    LOADING = "⏳ Загрузка..."
    PROCESSING = "⚙️ Обработка..."
    CONNECTING = "🔗 Подключение..."

    @staticmethod
    def searching_room(room_number: str) -> str:
        """Format searching message for room."""
        return InfoMessages.SEARCHING_ROOM.format(room_number=room_number)
    
    @staticmethod
    def searching_floor(floor: int) -> str:
        """Format searching message for floor."""
        return InfoMessages.SEARCHING_FLOOR.format(floor=floor)


class RetryMessages:
    """Messages with retry options and guidance."""
    
    RETRY_SEARCH = "Попробовать поиск еще раз?"
    RETRY_SAVE = "Попробовать сохранить еще раз?"
    RETRY_CONNECTION = "Проверьте интернет-соединение и попробуйте еще раз."
    
    # Helpful guidance
    ROOM_NUMBER_HELP = "💡 Номер комнаты может содержать цифры и буквы (например: 201, A10, B205)."
    FLOOR_NUMBER_HELP = "💡 Номер этажа должен быть числом (например: 1, 2, 3, ...)."
    SEARCH_HELP = "💡 Используйте кнопки меню для навигации или введите /start для возврата к началу."
    
    @staticmethod
    def with_help(error_message: str, help_message: str) -> str:
        """Combine error message with helpful guidance."""
        return f"{error_message}\n\n{help_message}"


class ButtonLabels:
    """Standardized button labels for consistent UI."""
    
    # Navigation
    BACK = "🔙 Назад"
    MAIN_MENU = "🏠 Главное меню"
    CANCEL = "❌ Отмена"
    
    # Actions
    RETRY = "🔄 Повторить"
    SAVE = "✅ Сохранить"
    EDIT = "✏️ Редактировать"
    
    # Search
    SEARCH_AGAIN = "🔍 Искать еще раз"
    NEW_SEARCH = "🔍 Новый поиск"