# Исследование: Система уведомлений Airtable

**Дата:** 14 января 2025
**Статус:** Исследование завершено
**Исследователь:** Claude Code

## Краткое описание

Исследование возможностей создания системы уведомлений для отслеживания изменений в базе данных Airtable (добавление новых участников, редактирование существующих записей) с последующей отправкой уведомлений определенным пользователям через Telegram бот.

## Ключевые находки

### 1. Airtable Webhooks API (Официальный подход)

**Возможности:**
- ✅ Отслеживание создания новых записей
- ✅ Отслеживание изменений существующих записей
- ✅ Отслеживание удаления записей
- ✅ Настройка фильтров по конкретным полям/таблицам
- ✅ Проверка подлинности через MAC-подпись

**Требования:**
- Airtable Pro план (платная подписка)
- Публично доступный HTTPS endpoint для получения webhooks
- Правильная настройка webhook через API

**Техническая реализация через pyAirtable:**
```python
from pyairtable.models import WebhookNotification

# Создание webhook
webhook = base.add_webhook(
    notification_url="https://yourbot.com/airtable-webhook",
    webhook_spec={
        "options": {
            "filters": {
                "dataTypes": ["tableData"]
            }
        }
    }
)

# Обработка уведомлений
notification = WebhookNotification.from_request(
    request_data, mac_signature, webhook_secret
)
```

### 2. Airtable Automations (Альтернативный подход)

**Возможности:**
- ✅ Триггеры на создание/обновление записей
- ✅ Отправка данных на внешний webhook
- ✅ Простая настройка через UI Airtable
- ✅ Доступно на бесплатном плане

**Техническая реализация:**
```javascript
// Скрипт в Airtable Automation
let webhookURL = 'YOUR_WEBHOOK_URL';
let payload = {
  records: input.config().record
};

let response = await fetch(webhookURL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
});
```

### 3. Polling система (Простой подход)

**Возможности:**
- ✅ Периодическая проверка изменений
- ✅ Работает с любым планом Airtable
- ✅ Простая реализация

**Недостатки:**
- ❌ Задержка в уведомлениях
- ❌ Дополнительная нагрузка на Airtable API

## Анализ существующей архитектуры бота

### Преимущества для интеграции:

1. **Готовые настройки webhook** (`src/config/settings.py:112-117`)
   - `webhook_url` и `webhook_secret` уже определены в TelegramSettings

2. **pyAirtable библиотека** (`requirements/base.txt:3`)
   - Уже установлена с поддержкой webhooks

3. **Список администраторов** (`src/config/settings.py:133-139`)
   - `admin_user_ids` готов для отправки уведомлений

4. **Система логирования** (`src/services/file_logging_service.py`)
   - Готова для отслеживания событий

### Текущая архитектура (3-слойная):
- **Bot Layer** (`src/bot/`) - Telegram обработчики
- **Service Layer** (`src/services/`) - Бизнес-логика
- **Data Layer** (`src/data/`) - Доступ к данным

## Рекомендуемые варианты реализации

### Вариант 1: Webhooks API (Продвинутый)

**Компоненты для добавления:**
```
src/services/webhook_service.py          # Основной сервис webhook
src/bot/handlers/webhook_handlers.py     # Обработчики webhook событий
src/models/webhook_notification.py       # Модели уведомлений
```

**Преимущества:**
- Мгновенные уведомления
- Официальная поддержка
- Полная интеграция с архитектурой

**Требования:**
- Airtable Pro план
- HTTPS сервер (Flask/FastAPI)
- SSL сертификат

### Вариант 2: Automations + простой webhook (Рекомендуемый)

**Компоненты для добавления:**
```
src/services/notification_service.py     # Сервис уведомлений
webhook_server.py                        # Простой Flask сервер
```

**Преимущества:**
- Работает на бесплатном плане
- Простая настройка
- Быстрая реализация

### Вариант 3: Polling система (Простой)

**Компоненты для добавления:**
```
src/services/change_detection_service.py # Сервис отслеживания изменений
src/utils/scheduler.py                   # Планировщик задач
```

**Преимущества:**
- Не требует внешних зависимостей
- Работает с любым планом
- Простая реализация

## Выводы и рекомендации

### Рекомендуемый подход: Вариант 2 (Automations + webhook)

**Обоснование:**
1. **Немедленная реализация** без смены плана Airtable
2. **Минимальные изменения** в существующем коде
3. **Простое тестирование** и отладка
4. **Возможность апгрейда** до полноценного Webhooks API позже

### Следующие шаги:
1. Настройка простого webhook сервера
2. Конфигурация Airtable Automations
3. Интеграция с системой уведомлений бота
4. Тестирование на реальных данных

### Требуемые изменения в коде:
- Минимальные: добавление 1-2 новых модулей
- Использование существующих admin_user_ids для отправки уведомлений
- Интеграция с существующей системой логирования

## Ссылки на ресурсы

- [pyAirtable Webhooks Documentation](https://pyairtable.readthedocs.io/en/stable/webhooks.html)
- [Airtable Web API Webhooks](https://airtable.com/developers/web/api/webhooks-overview)
- [Bootstrapped Airtable Webhooks Guide](https://bootstrapped.app/guide/how-to-set-up-webhooks-with-airtable-for-real-time-updates)