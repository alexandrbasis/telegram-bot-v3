# Техническое руководство по реализации уведомлений Airtable

## Обзор вариантов реализации

### Вариант 1: Официальный Webhooks API

#### Требуемые компоненты

```
src/services/webhook_service.py          # Основной сервис webhook
src/services/notification_service.py     # Сервис отправки уведомлений
src/bot/handlers/webhook_handlers.py     # Обработчики webhook событий
src/models/webhook_notification.py       # Модели уведомлений
src/utils/webhook_server.py              # FastAPI/Flask сервер для webhook
```

#### Примеры кода

**1. Webhook Service (`src/services/webhook_service.py`)**
```python
"""
Сервис для работы с Airtable Webhooks API.
"""

import logging
from typing import Dict, List, Optional
from pyairtable import Api
from pyairtable.models import WebhookNotification
from src.config.settings import get_settings
from src.models.webhook_notification import NotificationPayload

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self):
        settings = get_settings()
        self.api = Api(settings.database.airtable_api_key)
        self.base = self.api.base(settings.database.airtable_base_id)
        self.webhook_secret = settings.telegram.webhook_secret

    async def setup_participant_webhook(self, webhook_url: str) -> str:
        """
        Создает webhook для отслеживания изменений в таблице участников.

        Returns:
            str: ID созданного webhook
        """
        try:
            webhook = self.base.add_webhook(
                notification_url=webhook_url,
                webhook_spec={
                    "options": {
                        "filters": {
                            "dataTypes": ["tableData"],
                            "recordChangeScope": "tbl8ivwOdAUvMi3Jy"  # Participants table
                        }
                    }
                }
            )

            logger.info(f"Webhook created with ID: {webhook.id}")
            return webhook.id

        except Exception as e:
            logger.error(f"Failed to create webhook: {e}")
            raise

    async def validate_notification(self, request_data: bytes, mac_signature: str) -> Optional[WebhookNotification]:
        """
        Валидирует входящее уведомление от Airtable.

        Returns:
            WebhookNotification или None если валидация не прошла
        """
        try:
            notification = WebhookNotification.from_request(
                request_data, mac_signature, self.webhook_secret
            )
            logger.info(f"Received valid webhook notification: {notification.webhook.id}")
            return notification

        except Exception as e:
            logger.error(f"Invalid webhook notification: {e}")
            return None

    async def get_payloads(self, webhook_id: str, cursor: Optional[str] = None) -> List[Dict]:
        """
        Получает данные изменений из webhook.

        Returns:
            List[Dict]: Список изменений
        """
        try:
            webhook = self.base.webhook(webhook_id)
            payloads = []

            for payload in webhook.payloads(cursor=cursor):
                payloads.append(payload)

            return payloads

        except Exception as e:
            logger.error(f"Failed to retrieve payloads: {e}")
            return []
```

**2. Notification Service (`src/services/notification_service.py`)**
```python
"""
Сервис для отправки уведомлений администраторам.
"""

import logging
from typing import List, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from src.config.settings import get_settings
from src.models.participant import Participant

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        settings = get_settings()
        self.admin_ids = settings.telegram.admin_user_ids

    async def notify_participant_created(self, participant_data: Dict[str, Any]) -> None:
        """
        Отправляет уведомление о создании нового участника.
        """
        try:
            participant = Participant.from_airtable_record(participant_data)

            message = (
                f"🆕 <b>Добавлен новый участник</b>\n\n"
                f"👤 <b>Имя:</b> {participant.russian_name or participant.english_name}\n"
                f"📧 <b>Email:</b> {participant.email or 'Не указан'}\n"
                f"📱 <b>Телефон:</b> {participant.phone or 'Не указан'}\n"
                f"🏠 <b>Комната:</b> {participant.room_number or 'Не назначена'}"
            )

            await self._send_to_admins(message)
            logger.info(f"Sent new participant notification for: {participant.russian_name}")

        except Exception as e:
            logger.error(f"Failed to send participant creation notification: {e}")

    async def notify_participant_updated(self, old_data: Dict, new_data: Dict) -> None:
        """
        Отправляет уведомление об изменении данных участника.
        """
        try:
            old_participant = Participant.from_airtable_record(old_data)
            new_participant = Participant.from_airtable_record(new_data)

            changes = self._detect_changes(old_participant, new_participant)
            if not changes:
                return

            name = new_participant.russian_name or new_participant.english_name
            message = (
                f"✏️ <b>Обновлены данные участника</b>\n\n"
                f"👤 <b>Участник:</b> {name}\n\n"
                f"<b>Изменения:</b>\n"
            )

            for field, change in changes.items():
                message += f"• <b>{field}:</b> {change['old']} → {change['new']}\n"

            await self._send_to_admins(message)
            logger.info(f"Sent participant update notification for: {name}")

        except Exception as e:
            logger.error(f"Failed to send participant update notification: {e}")

    async def _send_to_admins(self, message: str) -> None:
        """
        Отправляет сообщение всем администраторам.
        """
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode='HTML'
                )
            except TelegramError as e:
                logger.error(f"Failed to send message to admin {admin_id}: {e}")

    def _detect_changes(self, old: Participant, new: Participant) -> Dict[str, Dict[str, str]]:
        """
        Определяет изменения между двумя версиями участника.
        """
        changes = {}
        fields_to_check = [
            ('russian_name', 'Русское имя'),
            ('english_name', 'Английское имя'),
            ('email', 'Email'),
            ('phone', 'Телефон'),
            ('room_number', 'Комната'),
            ('floor', 'Этаж')
        ]

        for field, display_name in fields_to_check:
            old_value = getattr(old, field)
            new_value = getattr(new, field)

            if old_value != new_value:
                changes[display_name] = {
                    'old': old_value or 'Не указано',
                    'new': new_value or 'Не указано'
                }

        return changes
```

**3. FastAPI Webhook Server (`src/utils/webhook_server.py`)**
```python
"""
FastAPI сервер для приема Airtable webhooks.
"""

import asyncio
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from telegram import Bot
from src.services.webhook_service import WebhookService
from src.services.notification_service import NotificationService
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

app = FastAPI(title="Airtable Webhook Server")

# Глобальные сервисы
webhook_service = WebhookService()
settings = get_settings()
bot = Bot(token=settings.telegram.bot_token)
notification_service = NotificationService(bot)

@app.post("/airtable-webhook")
async def handle_airtable_webhook(request: Request):
    """
    Обрабатывает входящие webhook уведомления от Airtable.
    """
    try:
        # Получаем данные запроса
        body = await request.body()
        mac_signature = request.headers.get("X-Airtable-Content-MAC")

        if not mac_signature:
            raise HTTPException(status_code=400, detail="Missing MAC signature")

        # Валидируем уведомление
        notification = await webhook_service.validate_notification(body, mac_signature)
        if not notification:
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # Получаем данные изменений
        payloads = await webhook_service.get_payloads(
            notification.webhook.id,
            cursor=notification.cursor
        )

        # Обрабатываем изменения
        for payload in payloads:
            await process_payload(payload)

        return {"status": "success", "processed": len(payloads)}

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_payload(payload: dict):
    """
    Обрабатывает отдельный payload с изменениями.
    """
    try:
        for table_id, changes in payload.get("tables", {}).items():
            if table_id != "tbl8ivwOdAUvMi3Jy":  # Только таблица участников
                continue

            for change in changes.get("changedRecords", []):
                if change["changeType"] == "created":
                    await notification_service.notify_participant_created(
                        change["current"]
                    )
                elif change["changeType"] == "updated":
                    await notification_service.notify_participant_updated(
                        change["previous"],
                        change["current"]
                    )

    except Exception as e:
        logger.error(f"Payload processing error: {e}")

@app.get("/health")
async def health_check():
    """
    Проверка здоровья сервера.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

#### Интеграция с основным ботом

**Обновление `src/main.py`:**
```python
import threading
from src.utils.webhook_server import app
import uvicorn

def start_webhook_server():
    """
    Запускает webhook сервер в отдельном потоке.
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)

async def run_bot():
    # ... существующий код ...

    # Запускаем webhook сервер в фоновом режиме
    webhook_thread = threading.Thread(
        target=start_webhook_server,
        daemon=True
    )
    webhook_thread.start()

    # ... остальной код запуска бота ...
```

### Вариант 2: Airtable Automations + простой webhook (Рекомендуемый)

#### Требуемые компоненты

```
src/services/simple_notification_service.py  # Простой сервис уведомлений
webhook_listener.py                          # Flask сервер (отдельный файл)
```

#### Примеры кода

**1. Простой Webhook Listener (`webhook_listener.py`)**
```python
"""
Простой Flask сервер для приема уведомлений от Airtable Automations.
"""

import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Bot
from src.config.settings import get_settings
from src.services.simple_notification_service import SimpleNotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация сервисов
settings = get_settings()
bot = Bot(token=settings.telegram.bot_token)
notification_service = SimpleNotificationService(bot)

@app.route("/airtable-automation", methods=["POST"])
def handle_airtable_automation():
    """
    Обрабатывает уведомления от Airtable Automations.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Определяем тип события
        event_type = data.get("action")  # created, updated, deleted
        record_data = data.get("record", {})

        # Асинхронная обработка
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if event_type == "created":
            loop.run_until_complete(
                notification_service.notify_participant_created(record_data)
            )
        elif event_type == "updated":
            old_data = data.get("previous_record", {})
            loop.run_until_complete(
                notification_service.notify_participant_updated(old_data, record_data)
            )

        loop.close()

        logger.info(f"Processed {event_type} event for record {record_data.get('id')}")
        return jsonify({"status": "success"})

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """
    Проверка здоровья сервера.
    """
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
```

**2. Simple Notification Service (`src/services/simple_notification_service.py`)**
```python
"""
Упрощенный сервис уведомлений для Airtable Automations.
"""

import logging
from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class SimpleNotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        settings = get_settings()
        self.admin_ids = settings.telegram.admin_user_ids

    async def notify_participant_created(self, record_data: Dict[str, Any]) -> None:
        """
        Отправляет уведомление о новом участнике.
        """
        try:
            fields = record_data.get("fields", {})

            name = (
                fields.get("Русское имя") or
                fields.get("Имя (русские буквы)") or
                fields.get("English Name") or
                "Неизвестный участник"
            )

            email = fields.get("Email", "Не указан")
            phone = fields.get("Телефон", "Не указан")
            room = fields.get("Комната", "Не назначена")

            message = (
                f"🆕 <b>Добавлен новый участник</b>\n\n"
                f"👤 <b>Имя:</b> {name}\n"
                f"📧 <b>Email:</b> {email}\n"
                f"📱 <b>Телефон:</b> {phone}\n"
                f"🏠 <b>Комната:</b> {room}"
            )

            await self._send_to_admins(message)
            logger.info(f"Sent new participant notification: {name}")

        except Exception as e:
            logger.error(f"Failed to send creation notification: {e}")

    async def notify_participant_updated(self, old_data: Dict, new_data: Dict) -> None:
        """
        Отправляет уведомление об изменении участника.
        """
        try:
            old_fields = old_data.get("fields", {})
            new_fields = new_data.get("fields", {})

            name = (
                new_fields.get("Русское имя") or
                new_fields.get("English Name") or
                "Неизвестный участник"
            )

            changes = self._detect_field_changes(old_fields, new_fields)
            if not changes:
                return

            message = (
                f"✏️ <b>Обновлены данные участника</b>\n\n"
                f"👤 <b>Участник:</b> {name}\n\n"
                f"<b>Изменения:</b>\n"
            )

            for field, change in changes.items():
                message += f"• <b>{field}:</b> {change['old']} → {change['new']}\n"

            await self._send_to_admins(message)
            logger.info(f"Sent update notification: {name}")

        except Exception as e:
            logger.error(f"Failed to send update notification: {e}")

    async def _send_to_admins(self, message: str) -> None:
        """
        Отправляет сообщение всем администраторам.
        """
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode='HTML'
                )
            except TelegramError as e:
                logger.error(f"Failed to send to admin {admin_id}: {e}")

    def _detect_field_changes(self, old_fields: Dict, new_fields: Dict) -> Dict[str, Dict[str, str]]:
        """
        Определяет изменения в полях записи.
        """
        changes = {}
        important_fields = {
            "Русское имя": "Русское имя",
            "English Name": "Английское имя",
            "Email": "Email",
            "Телефон": "Телефон",
            "Комната": "Комната"
        }

        for field_key, display_name in important_fields.items():
            old_value = old_fields.get(field_key)
            new_value = new_fields.get(field_key)

            if old_value != new_value:
                changes[display_name] = {
                    'old': old_value or 'Не указано',
                    'new': new_value or 'Не указано'
                }

        return changes
```

### Настройка Airtable Automation

**Скрипт для Airtable Automation:**
```javascript
// Этот скрипт настраивается в Airtable Automations
// Триггер: When record created/updated в таблице Participants

let webhookURL = 'https://your-domain.com/airtable-automation';

// Определяем тип события
let action = 'created'; // или 'updated' в зависимости от триггера

let payload = {
    action: action,
    record: input.config().record,
    // Для updated триггера также можно добавить:
    // previous_record: input.config().previous_record
};

let response = await fetch(webhookURL, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
});

if (response.ok) {
    console.log('Webhook sent successfully');
} else {
    console.log('Webhook failed:', response.status);
}
```

## Требования к инфраструктуре

### Для варианта 1 (Webhooks API):
- Airtable Pro план ($20/месяц)
- HTTPS домен с SSL сертификатом
- Сервер для размещения (VPS/Cloud)

### Для варианта 2 (Automations):
- Airtable бесплатный план
- HTTPS домен с SSL сертификатом
- Сервер для размещения (VPS/Cloud)

## Рекомендации по развертыванию

1. **Тестирование:** Начать с локального ngrok туннеля
2. **Продакшн:** Использовать облачные сервисы (Railway, Heroku, DigitalOcean)
3. **Мониторинг:** Добавить логирование и health checks
4. **Безопасность:** Использовать HTTPS и валидацию подписей