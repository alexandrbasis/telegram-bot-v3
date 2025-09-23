"""
Standardized bot messages for consistent user experience.

This module provides centralized message templates for all bot interactions,
ensuring consistent messaging across different handlers and features.
"""


class AccessRequestMessages:
    """Messages for access request workflow."""

    # User-facing messages
    PENDING_REQUEST_RU = (
        "✅ Запрос на доступ принят. Мы уведомим вас, как только админ его обработает."
    )
    PENDING_REQUEST_EN = "✅ Your access request has been recorded. We'll notify you as soon as an admin reviews it."

    EXISTING_PENDING_RU = "⏳ Ваш запрос на доступ уже находится на рассмотрении. Мы уведомим вас после решения администратора."
    EXISTING_PENDING_EN = "⏳ Your access request is already pending review. We'll notify you once an admin makes a decision."

    APPROVED_RU = "✅ Доступ подтверждён! Ваша роль: {access_level}.\n\nИспользуйте /start для начала работы с ботом."
    APPROVED_EN = "✅ You're all set! Assigned access level: {access_level}.\n\nUse /start to begin working with the bot."

    DENIED_RU = "❌ К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором."
    DENIED_EN = "❌ We weren't able to approve your access right now. Contact an admin if you believe this is a mistake."

    ACCESS_GRANTED_RU = "👋 Добро пожаловать! У вас есть доступ к боту.\n\nДоступные команды:\n/search - Поиск участников\n/export - Экспорт данных\n/help - Помощь"
    ACCESS_GRANTED_EN = "👋 Welcome! You have access to the bot.\n\nAvailable commands:\n/search - Search participants\n/export - Export data\n/help - Help"

    # Admin notifications
    NEW_REQUEST_RU = "🔔 Новый запрос на доступ: {display_name} ({user_id})."
    NEW_REQUEST_EN = "🔔 New access request from {display_name} ({user_id})."

    # Admin interface messages
    NO_PENDING_REQUESTS = "✅ Нет ожидающих запросов на доступ."
    REQUESTS_LIST_HEADER = "📋 *Запросы на доступ (страница {page}/{total_pages}):*\n"
    REQUEST_ITEM = "• @{username} (ID: {user_id})\n  Дата: {date}\n"

    # Admin notes
    ADMIN_NOTE_RU = "\n\nКомментарий администратора: {notes}"
    ADMIN_NOTE_EN = "\n\nAdmin note: {notes}"

    # Error messages
    REQUEST_ERROR_RU = (
        "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."
    )
    REQUEST_ERROR_EN = (
        "An error occurred while processing the request. Please try again later."
    )

    ACCESS_CHECK_ERROR_RU = (
        "Произошла ошибка при проверке доступа. Пожалуйста, попробуйте позже."
    )
    ACCESS_CHECK_ERROR_EN = (
        "An error occurred while checking access. Please try again later."
    )

    LOAD_REQUESTS_ERROR_RU = (
        "Произошла ошибка при загрузке запросов. Пожалуйста, попробуйте позже."
    )
    LOAD_REQUESTS_ERROR_EN = (
        "An error occurred while loading requests. Please try again later."
    )

    # Access control messages
    ADMIN_ONLY_RU = "Эта команда доступна только администраторам."
    ADMIN_ONLY_EN = "This command is available to administrators only."

    NEED_APPROVAL_RU = "Для использования этой функции необходимо одобрение администратора. Используйте /start для запроса доступа."
    NEED_APPROVAL_EN = (
        "This function requires administrator approval. Use /start to request access."
    )

    PENDING_PROCESSING_RU = "Ваш запрос на доступ обрабатывается. Пожалуйста, подождите одобрения администратора."
    PENDING_PROCESSING_EN = "Your access request is being processed. Please wait for administrator approval."

    ACCESS_DENIED_INFO_RU = "Доступ к этой функции был отклонен. Обратитесь к администратору для получения дополнительной информации."
    ACCESS_DENIED_INFO_EN = "Access to this function has been denied. Contact an administrator for more information."

    # Button labels
    BTN_APPROVE = "✅ Одобрить"
    BTN_DENY = "❌ Отклонить"
    BTN_PREV_PAGE = "⬅️ Назад"
    BTN_NEXT_PAGE = "➡️ Вперед"
    BTN_CLOSE = "❌ Закрыть"


class ErrorMessages:
    """Standardized error messages for user-facing errors."""

    # Input validation errors
    INVALID_ROOM_NUMBER = (
        "❌ Пожалуйста, введите корректный номер комнаты (должен содержать цифры)."
    )
    INVALID_FLOOR_NUMBER = (
        "❌ Пожалуйста, введите корректный номер этажа (должен быть числом)."
    )
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
    MAINTENANCE_MODE = (
        "❌ Система временно недоступна для обслуживания. Попробуйте позже."
    )

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
    PARTICIPANTS_FOUND_IN_ROOM = (
        "🏠 Найдено участников в комнате {room_number}: {count}"
    )
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
        return SuccessMessages.PARTICIPANTS_FOUND_IN_ROOM.format(
            room_number=room_number, count=count
        )

    @staticmethod
    def participants_found_on_floor(floor: int, count: int) -> str:
        """Format message for participants found on floor."""
        return SuccessMessages.PARTICIPANTS_FOUND_ON_FLOOR.format(
            floor=floor, count=count
        )


class InfoMessages:
    """Informational messages and prompts."""

    # Search prompts
    ENTER_ROOM_NUMBER = "Введите номер комнаты для поиска:"
    ENTER_FLOOR_NUMBER = "Пришлите номер этажа цифрой:"
    ENTER_FLOOR_WITH_DISCOVERY = (
        "Выберите этаж из списка или пришлите номер этажа цифрой:"
    )
    SEARCHING_ROOM = "🔍 Ищу участников в комнате {room_number}..."
    SEARCHING_FLOOR = "🔍 Ищу участников на этаже {floor}..."

    # Floor discovery messages
    AVAILABLE_FLOORS_HEADER = "📍 Доступные этажи:"
    NO_FLOORS_AVAILABLE = "В данный момент участники не размещены ни на одном этаже. Пришлите номер этажа цифрой."
    FLOOR_DISCOVERY_ERROR = "Произошла ошибка. Пришлите номер этажа цифрой."

    # Demographic field input prompts
    ENTER_DATE_OF_BIRTH = (
        "📅 Введите дату рождения в формате ДД/ММ/ГГГГ (например: 22/09/2025):"
    )
    ENTER_AGE = "🔢 Введите возраст (от 0 до 120):"

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
    ROOM_NUMBER_HELP = (
        "💡 Номер комнаты может содержать цифры и буквы (например: 201, A10, B205)."
    )
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


class SearchResultLabels:
    """Localized labels used in participant search result formatting."""

    _LABELS = {
        "ru": {
            "floor": "Этаж",
            "room": "Комната",
            "date_of_birth": "Дата рождения",
            "age": "Возраст",
            "not_available": "Не указано",
            "leader": "Наставник",
            "table": "Стол",
            "notes": "Заметки",
            "years_suffix": "лет",
        },
        "en": {
            "floor": "Floor",
            "room": "Room",
            "date_of_birth": "Date of Birth",
            "age": "Age",
            "not_available": "N/A",
            "leader": "Leader",
            "table": "Table",
            "notes": "Notes",
            "years_suffix": "years",
        },
    }

    @classmethod
    def for_language(cls, language: str) -> dict:
        """Return labels for the requested language (defaults to Russian)."""
        return cls._LABELS.get(language, cls._LABELS["ru"])

    @classmethod
    def get(cls, key: str, language: str = "ru") -> str:
        """Get a localized label by key."""
        return cls.for_language(language)[key]

    @classmethod
    def format_age(cls, age: int, language: str = "ru") -> str:
        """Format age with localized suffix."""
        if language == "ru":
            suffix = cls._ru_year_suffix(age)
            return f"{age} {suffix}"
        suffix = cls.get("years_suffix", language)
        return f"{age} {suffix}"

    @staticmethod
    def _ru_year_suffix(age: int) -> str:
        """Return grammatical suffix for Russian age values."""
        value = abs(int(age))
        if value % 10 == 1 and value % 100 != 11:
            return "год"
        if value % 10 in (2, 3, 4) and value % 100 not in (12, 13, 14):
            return "года"
        return "лет"
