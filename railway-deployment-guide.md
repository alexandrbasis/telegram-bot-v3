# Railway Deployment Guide - Telegram Bot

*Пошаговое руководство по развертыванию Telegram бота на Railway*

## Что такое Railway?

Railway - это современная платформа для развертывания приложений, которая отлично подходит для Telegram ботов. Она поддерживает:
- Длительные процессы (идеально для ботов)
- Автоматическое развертывание из Git
- Простое управление переменными окружения
- Бесплатный тарифный план для начала

## Подготовка проекта

Я уже создал необходимые файлы конфигурации:

### 1. `railway.toml` - основная конфигурация
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python -m src.main"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 2. `requirements.txt` - зависимости Python
```
python-telegram-bot>=20.0
pyairtable>=1.5.0
python-dotenv>=1.0.0
pydantic>=2.0.0
rapidfuzz>=3.0.0
```

### 3. `Procfile` - команда запуска
```
web: python -m src.main
```

## Варианты развертывания

### Вариант 1: Через Web Dashboard (Самый простой)

1. **Зайдите на Railway**
   - Идите на [railway.app](https://railway.app)
   - Войдите через GitHub

2. **Создайте новый проект**
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий `telegram-bot-v3`

3. **Настройте переменные окружения**
   В разделе Variables добавьте:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   AIRTABLE_API_KEY=ваш_airtable_ключ
   AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC
   AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy
   AIRTABLE_TABLE_NAME=Participants
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   ```

4. **Запустите развертывание**
   - Railway автоматически обнаружит Python проект
   - Установит зависимости из `requirements.txt`
   - Запустит бота командой из `Procfile`

### Вариант 2: Через Railway CLI

1. **Войдите в Railway**
   ```bash
   railway login
   ```
   Это откроет браузер для аутентификации.

2. **Инициализируйте проект**
   ```bash
   railway init
   ```
   Выберите "Create new project" и дайте ему имя.

3. **Свяжите с существующим проектом (если есть)**
   ```bash
   railway link
   ```

4. **Добавьте переменные окружения**
   ```bash
   railway variables set TELEGRAM_BOT_TOKEN=ваш_токен
   railway variables set AIRTABLE_API_KEY=ваш_ключ
   railway variables set AIRTABLE_BASE_ID=appRp7Vby2JMzN0mC
   railway variables set AIRTABLE_TABLE_ID=tbl8ivwOdAUvMi3Jy
   railway variables set AIRTABLE_TABLE_NAME=Participants
   railway variables set LOG_LEVEL=INFO
   railway variables set ENVIRONMENT=production
   ```

5. **Разверните проект**
   ```bash
   railway up
   ```

### Вариант 3: Автоматическое развертывание из Git

1. **Подключите репозиторий**
   - В Railway dashboard выберите ваш проект
   - Перейдите в Settings → Source
   - Подключите GitHub репозиторий

2. **Настройте автоматическое развертывание**
   - Каждый push в main/master ветку будет автоматически разворачиваться
   - Pull requests создают preview развертывания

## Управление проектом

### Просмотр логов
```bash
railway logs
```

### Просмотр статуса
```bash
railway status
```

### Открытие dashboard
```bash
railway open
```

### Остановка сервиса
```bash
railway down
```

### Перезапуск сервиса
В Railway dashboard: Service → Settings → Restart

## Получение переменных окружения

Вам понадобятся:

### 1. Telegram Bot Token
- Найдите @BotFather в Telegram
- Создайте нового бота: `/newbot`
- Скопируйте токен

### 2. Airtable API Key
- Зайдите на [airtable.com/create/tokens](https://airtable.com/create/tokens)
- Создайте Personal Access Token
- Дайте доступ к вашей базе данных

### 3. Airtable Base ID и Table ID
- Откройте вашу Airtable базу
- В URL найдите ID: `https://airtable.com/appXXXXXXXX/tblYYYYYYYY`
- `appXXXXXXXX` - это Base ID
- `tblYYYYYYYY` - это Table ID

## Мониторинг и отладка

### Проверка логов развертывания
В Railway dashboard:
- Перейдите в Deploy → Logs
- Смотрите Build Logs для проблем установки
- Смотрите Deploy Logs для проблем запуска

### Типичные ошибки

1. **ModuleNotFoundError**
   - Проверьте, что все зависимости в `requirements.txt`
   - Убедитесь, что структура проекта правильная

2. **Environment variables not set**
   - Проверьте, что все переменные добавлены в Variables
   - Перезапустите сервис после добавления переменных

3. **Port binding errors**
   - Railway автоматически назначает порт
   - Не нужно слушать конкретный порт для Telegram ботов

### Полезные команды Railway CLI

```bash
# Список всех проектов
railway projects

# Информация о текущем проекте  
railway status

# Просмотр переменных окружения
railway variables

# Выполнение команд в Railway окружении
railway run python -m src.main

# Подключение к локальной разработке с Railway переменными
railway shell
```

## Масштабирование

Railway автоматически управляет ресурсами, но вы можете:
- Мониторить использование CPU/RAM в dashboard
- Настроить автоперезапуск при сбоях
- Добавить алерты на email

## Стоимость

- **Starter план**: $0/месяц, $5 кредитов бесплатно
- **Developer план**: $20/месяц включает $20 кредитов
- Бот обычно потребляет ~$1-3/месяц

## Следующие шаги

1. Создайте аккаунт на Railway
2. Подготовьте переменные окружения
3. Выберите один из вариантов развертывания
4. Протестируйте бота
5. Настройте мониторинг

---

*Railway идеально подходит для Telegram ботов благодаря поддержке длительных процессов и простой настройке!*