#!/bin/bash

# Project Index Update Hook for telegram-bot-v3
# Автоматически обновляет project_index.json при изменениях файлов

set -e

# Логирование (и в stdout, и в файл)
debug_log() {
    local msg="🔍 [$(date '+%H:%M:%S')] $1"
    echo "$msg"
    # LOG_FILE будет определен позже, поэтому проверяем его существование
    if [ -n "$LOG_FILE" ]; then
        echo "$msg" >> "$LOG_FILE"
    fi
}

# Определяем директорию проекта
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    PROJECT_DIR="$CLAUDE_PROJECT_DIR"
else
    # Если переменная не установлена, используем текущую директорию
    PROJECT_DIR="$(pwd)"
fi

# Защита от проблем с пробелами в путях - принудительная проверка
if [[ "$PROJECT_DIR" == *" "* ]]; then
    debug_log "⚠️  Обнаружены пробелы в пути проекта: $PROJECT_DIR"
fi
HOOK_DIR="$PROJECT_DIR/.claude/hooks"
INDEX_FILE="$PROJECT_DIR/project_index.json"
INDEXER_SCRIPT="$HOOK_DIR/update-index.py"
LOG_FILE="$PROJECT_DIR/.claude/hooks/hook-debug.log"
LOCK_DIR="$PROJECT_DIR/.claude/hooks/.update-index.lock"


# Запись диагностической информации
debug_log "=== Hook triggered ==="
debug_log "CLAUDE_PROJECT_DIR: $CLAUDE_PROJECT_DIR"
debug_log "PROJECT_DIR: $PROJECT_DIR"
debug_log "PWD: $(pwd)"
debug_log "Script path: $INDEXER_SCRIPT"

debug_log "Запуск обновления индекса проекта..."

# Concurrency guard
if mkdir "$LOCK_DIR" 2>/dev/null; then
    debug_log "🔒 Установлена блокировка обновления индекса"
    trap 'rm -rf "$LOCK_DIR"' EXIT
else
    debug_log "⏭️  Пропуск: обновление уже выполняется (lock)"
    exit 0
fi

# Проверка существования индексера
if [ ! -f "$INDEXER_SCRIPT" ]; then
    debug_log "❌ Скрипт индексера не найден: $INDEXER_SCRIPT"
    exit 1
fi

# Skip if nothing relevant changed since last index write
if [ -f "$INDEX_FILE" ]; then
    # Limit to key areas to avoid noise
    CHANGED_FILE=$(find "$PROJECT_DIR" \( \
        -path "$PROJECT_DIR/src/*" -o \
        -path "$PROJECT_DIR/tests/*" -o \
        -path "$PROJECT_DIR/docs/*" -o \
        -path "$PROJECT_DIR/.claude/*" \
      \) -type f \
      ! -name "project_index.json" \
      ! -name "hook-debug.log" \
      -newer "$INDEX_FILE" -print -quit 2>/dev/null)
    if [ -z "$CHANGED_FILE" ]; then
        debug_log "ℹ️  Нет изменений после последнего индекса. Пропуск."
        exit 0
    else
        debug_log "🆕 Обнаружены изменения: $CHANGED_FILE"
    fi
    # Create a backup after we know we will proceed
    cp "$INDEX_FILE" "$INDEX_FILE.backup" && debug_log "📋 Создана резервная копия индекса"
fi

# Запуск Python индексера
debug_log "🐍 Запуск Python индексера..."
debug_log "📍 Команда: python3 \"$INDEXER_SCRIPT\" \"$PROJECT_DIR\""

# Используем eval для корректной обработки путей с пробелами
if eval "python3 \"$INDEXER_SCRIPT\" \"$PROJECT_DIR\""; then
    debug_log "✅ Индекс успешно обновлен"
    
    # Удаляем резервную копию при успехе
    if [ -f "$INDEX_FILE.backup" ]; then
        rm "$INDEX_FILE.backup"
    fi
else
    debug_log "❌ Ошибка обновления индекса"
    
    # Восстанавливаем из резервной копии при ошибке
    if [ -f "$INDEX_FILE.backup" ]; then
        mv "$INDEX_FILE.backup" "$INDEX_FILE"
        debug_log "🔄 Индекс восстановлен из резервной копии"
    fi
    
    exit 1
fi

debug_log "🎉 Обновление индекса завершено успешно"
