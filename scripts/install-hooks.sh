#!/bin/bash
# Скрипт установки git hooks для Tres Dias Telegram Bot v3
# Использование: ./scripts/install-hooks.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Git Hooks Installer - Tres Dias Telegram Bot v3          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Проверка, что мы в корне репозитория
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Ошибка: Запустите скрипт из корня репозитория${NC}"
    exit 1
fi

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Виртуальное окружение не найдено${NC}"
    echo -e "${BLUE}ℹ️  Создание виртуального окружения...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Виртуальное окружение создано${NC}\n"
fi

# Активация виртуального окружения и установка зависимостей
if [ ! -f "venv/bin/black" ] || [ ! -f "venv/bin/flake8" ]; then
    echo -e "${YELLOW}⚠️  Отсутствуют необходимые инструменты качества кода${NC}"
    echo -e "${BLUE}ℹ️  Установка зависимостей...${NC}"

    source venv/bin/activate
    pip install -q -r requirements/dev.txt
    deactivate

    echo -e "${GREEN}✅ Зависимости установлены${NC}\n"
fi

# Путь к директории hooks
HOOKS_DIR=".git/hooks"
PRE_COMMIT_HOOK="$HOOKS_DIR/pre-commit"

# Резервная копия существующего hook (если есть)
if [ -f "$PRE_COMMIT_HOOK" ] && [ ! -L "$PRE_COMMIT_HOOK" ]; then
    BACKUP_FILE="$PRE_COMMIT_HOOK.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}⚠️  Существующий pre-commit hook обнаружен${NC}"
    echo -e "${BLUE}ℹ️  Создание резервной копии: $BACKUP_FILE${NC}"
    cp "$PRE_COMMIT_HOOK" "$BACKUP_FILE"
    echo -e "${GREEN}✅ Резервная копия создана${NC}\n"
fi

# Определяем источник hook файла
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_SOURCE="$HOOKS_DIR/pre-commit"

# Копируем hook (он уже должен быть в .git/hooks/ из предыдущего шага)
if [ ! -f "$HOOK_SOURCE" ]; then
    echo -e "${RED}❌ Ошибка: pre-commit hook не найден в $HOOKS_DIR${NC}"
    echo -e "${YELLOW}ℹ️  Создайте hook файл сначала${NC}"
    exit 1
fi

# Делаем hook исполняемым
chmod +x "$PRE_COMMIT_HOOK"

echo -e "${GREEN}✅ Pre-commit hook установлен успешно!${NC}\n"

# Информация об установленном hook
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Установленные проверки:                                   ║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║${NC}  ✅ Проверка размера файлов                               ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ✅ Проверка конфликтов слияния                           ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ✅ Проверка debug-кода                                   ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ✅ Валидация синтаксиса Python                           ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  🔧 Автоматическое форматирование (isort + black)         ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ✅ Линтинг (flake8)                                       ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ✅ Проверка типов (mypy)                                 ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}  ✅ Быстрые unit-тесты                                     ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}📝 Примечание:${NC}"
echo -e "   • Hook запускается автоматически при каждом коммите"
echo -e "   • Чтобы пропустить проверки: ${GREEN}git commit --no-verify${NC}"
echo -e "   • Для отключения hook: ${YELLOW}chmod -x $PRE_COMMIT_HOOK${NC}\n"

echo -e "${GREEN}🎉 Готово! Теперь каждый коммит будет проверяться автоматически.${NC}\n"
