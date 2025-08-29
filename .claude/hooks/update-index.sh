#!/bin/bash

# Project Index Update Hook for telegram-bot-v3
# Автоматически обновляет project_index.json при изменениях файлов

set -e

# Определяем директорию проекта
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    PROJECT_DIR="$CLAUDE_PROJECT_DIR"
else
    # Если переменная не установлена, используем текущую директорию
    PROJECT_DIR="$(pwd)"
fi
HOOK_DIR="$PROJECT_DIR/.claude/hooks"
INDEX_FILE="$PROJECT_DIR/project_index.json"
INDEXER_SCRIPT="$HOOK_DIR/update-index.py"
LOG_FILE="$PROJECT_DIR/.claude/hooks/hook-debug.log"

# Логирование (и в stdout, и в файл)
log() {
    local msg="🔍 [$(date '+%H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# Запись диагностической информации
log "=== Hook triggered ==="
log "CLAUDE_PROJECT_DIR: $CLAUDE_PROJECT_DIR"
log "PROJECT_DIR: $PROJECT_DIR"
log "PWD: $(pwd)"
log "Script path: $INDEXER_SCRIPT"

log "Запуск обновления индекса проекта..."

# Проверка существования индексера
if [ ! -f "$INDEXER_SCRIPT" ]; then
    log "❌ Скрипт индексера не найден: $INDEXER_SCRIPT"
    exit 1
fi

# Создание резервной копии текущего индекса
if [ -f "$INDEX_FILE" ]; then
    cp "$INDEX_FILE" "$INDEX_FILE.backup"
    log "📋 Создана резервная копия индекса"
fi

# Запуск Python индексера
log "🐍 Запуск Python индексера..."
if python3 "$INDEXER_SCRIPT" "$PROJECT_DIR"; then
    log "✅ Индекс успешно обновлен"
    
    # Удаляем резервную копию при успехе
    if [ -f "$INDEX_FILE.backup" ]; then
        rm "$INDEX_FILE.backup"
    fi
else
    log "❌ Ошибка обновления индекса"
    
    # Восстанавливаем из резервной копии при ошибке
    if [ -f "$INDEX_FILE.backup" ]; then
        mv "$INDEX_FILE.backup" "$INDEX_FILE"
        log "🔄 Индекс восстановлен из резервной копии"
    fi
    
    exit 1
fi

log "🎉 Обновление индекса завершено успешно"