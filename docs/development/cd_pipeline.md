# Continuous Deployment (CD) на Railway

Этот документ описывает, как устроен непрерывный деплой (CD) бота: что триггерит деплой, какие файлы его настраивают, что происходит на билде и как управлять релизами.

## Кратко
- Ветка деплоя: `main` (Auto Deployments = ON в Railway).
- Конфиг Railway: `railway.toml` (в корне репозитория).
- Тип сборки: `builder = "dockerfile"` (используется наш `Dockerfile`).
- Команда запуска: `python -m src.main`.
- Рестарты: при падении процесс перезапускается (ON_FAILURE, до 10 раз).

## Что триггерит деплой
- Любой `push` в ветку `main` (merge PR или прямой push).
- Вручную из UI: кнопка `Redeploy` в Deployments.
- Вручную из CLI: `railway up`.

## Как проходит сборка
1. Railway считывает `railway.toml` и видит `builder = "dockerfile"`.
2. Собирает образ строго по нашему `Dockerfile`:
   - Базовый образ: `python:3.11-slim`.
   - Обновляет `pip`, устанавливает зависимости из `requirements.txt`.
   - Копирует `src/`, `start_bot.sh`, `.env.example`.
   - Устанавливает `PYTHONPATH=/app`.
   - Задаёт `CMD ["python", "-m", "src.main"]`.
3. Никаких шагов Nixpacks/Fix‑It (`pip install .`) не выполняется — это исключено выбором Dockerfile.

## Файлы, определяющие деплой
- `railway.toml` (корень):
  ```toml
  [build]
  builder = "dockerfile"

  [deploy]
  startCommand = "python -m src.main"
  restartPolicyType = "ON_FAILURE"
  restartPolicyMaxRetries = 10
  ```
- `Dockerfile` — шаги сборки образа и команда запуска.
- `requirements.txt` — список зависимостей.

## Переменные окружения (Railway → Variables)
- Обязательные: `TELEGRAM_BOT_TOKEN`, `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`.
- Опциональные: `AIRTABLE_TABLE_NAME`, `AIRTABLE_TABLE_ID`, `LOG_LEVEL`, `ENVIRONMENT`.

## Как понять, что всё ок
- В логах деплоя видно `Using Dockerfile` и успешный билд.
- Сервисные логи показывают старт бота без сетевых ошибок.

## Управление релизами
- Перезапуск: Service → Settings → `Restart`.
- Откат: Deployments → выбрать успешный релиз → `Rollback`.
- Чистка кэша сборки при странном поведении: Settings → `Clear build cache` → `Redeploy`.

## Частые вопросы
- "В логах вижу Fix‑It / pip install .": значит используется Nixpacks. Проверьте, что Railway действительно читает `railway.toml` и builder = dockerfile; очистите build cache.
- "Код не обновляется после push": убедитесь, что проект привязан к ветке `main` и Auto Deploy включён.
- "Бот не стартует": проверьте переменные окружения; после добавления — перезапустите сервис.

## Локальные проверки перед пушем
- `./venv/bin/pytest -q` — базовые тесты.
- `./venv/bin/flake8 src tests` и `./venv/bin/mypy src --no-error-summary` — линтер и типы.

После успешного пуша в `main` Railway автоматически соберёт и задеплоит новую версию бота.
