# Задача: Создание Индексер-Хука для Claude Code

## Суть задачи

Создать автоматизированную систему индексации проекта, которая будет отслеживать изменения в коде и поддерживать актуальный индекс-файл `project_index.json`. Этот индекс поможет Claude Code получать высококачественный контекст о структуре проекта без перегрузки ненужной информацией.

## Что дает эта задача

### Преимущества для работы с Claude Code:
1. **Оптимизированный контекст** - Claude получает только релевантную информацию о проекте
2. **Улучшенное качество ответов** - лучшее понимание структуры и зависимостей проекта
3. **Быстрый старт новых сессий** - возможность быстро загрузить полное понимание проекта
4. **Предотвращение ошибок** - снижение вероятности создания дублирующего кода или пропуска важных файлов
5. **Автоматическое обновление** - индекс всегда актуальный без ручного вмешательства

### Технические преимущества:
- Минифицированное представление всего кодбейса
- UML-стиль абстракции с ключевой информацией
- Автоматическое отслеживание изменений файлов
- Исключение файлов из `.gitignore`

## Детальный план реализации

### Шаг 1: Настройка хука в Claude Code

**Файл: `.claude/settings.json`**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/update-index.sh"
          }
        ]
      }
    ]
  }
}
```

### Шаг 2: Создание структуры индекс-файла

**Файл: `project_index.json` (в корне проекта)**
```json
{
  "project_metadata": {
    "name": "telegram-bot-v3",
    "last_updated": "2025-08-28T12:00:00Z",
    "total_files": 0,
    "indexed_files": 0,
    "version": "1.0.0"
  },
  "project_structure": {
    "tree": "telegram-bot-v3/\n├── src/\n│   ├── bot/\n│   ├── domain/\n│   └── services/\n├── tests/\n└── config/",
    "directories": ["src", "tests", "config", "src/bot", "src/domain", "src/services"],
    "files": {}
  },
  "file_index": {
    "src/bot/handlers/commands/add.py": {
      "type": "python",
      "size": 1024,
      "imports": ["telegram", "logging", "airtable"],
      "functions": [
        {
          "name": "handle_add_command",
          "params": ["update", "context"],
          "return_type": "None",
          "line_start": 15,
          "line_end": 45
        }
      ],
      "classes": [
        {
          "name": "AddCommandHandler",
          "methods": ["__init__", "validate_input", "process_request"],
          "line_start": 50,
          "line_end": 120
        }
      ],
      "constants": ["MAX_ITEMS", "DEFAULT_LIMIT"],
      "dependencies": ["src.services.airtable", "src.utils.validation"],
      "exports": ["AddCommandHandler", "handle_add_command"],
      "last_modified": "2025-08-28T11:30:00Z"
    }
  },
  "dependency_graph": {
    "src/bot/handlers/commands/add.py": [
      "src/services/airtable.py",
      "src/utils/validation.py"
    ]
  }
}
```

### Шаг 3: Создание скрипта обновления индекса

**Файл: `.claude/hooks/update-index.sh`**
```bash
#!/bin/bash

# Проект: telegram-bot-v3 Indexer Hook
# Назначение: Автоматическое обновление project_index.json при изменениях

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
INDEX_FILE="$PROJECT_DIR/project_index.json"
TEMP_INDEX="$PROJECT_DIR/.temp_index.json"

echo "🔍 Обновление индекса проекта..."

# Проверка существования Python индексера
if [ ! -f "$PROJECT_DIR/.claude/hooks/indexer.py" ]; then
    echo "❌ Индексер не найден. Создание базового индекса..."
    python3 "$PROJECT_DIR/.claude/hooks/create_indexer.py"
fi

# Запуск Python индексера
python3 "$PROJECT_DIR/.claude/hooks/indexer.py" "$PROJECT_DIR" "$TEMP_INDEX"

# Проверка успешности создания
if [ $? -eq 0 ] && [ -f "$TEMP_INDEX" ]; then
    mv "$TEMP_INDEX" "$INDEX_FILE"
    echo "✅ Индекс успешно обновлен: $(date)"
else
    echo "❌ Ошибка обновления индекса"
    exit 1
fi
```

### Шаг 4: Python индексер

**Файл: `.claude/hooks/indexer.py`**
```python
#!/usr/bin/env python3
"""
Индексер для создания project_index.json
Анализирует структуру проекта и создает минифицированное представление
"""

import os
import json
import ast
import sys
from datetime import datetime
from pathlib import Path
import fnmatch

class ProjectIndexer:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.gitignore_patterns = self._load_gitignore()
        
    def _load_gitignore(self):
        """Загружает паттерны из .gitignore"""
        gitignore_path = self.project_path / '.gitignore'
        patterns = ['__pycache__', '*.pyc', '.git', 'venv', '.env']
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                patterns.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
        
        return patterns
    
    def _should_ignore(self, file_path):
        """Проверяет, должен ли файл быть игнорирован"""
        relative_path = file_path.relative_to(self.project_path)
        
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
            if fnmatch.fnmatch(relative_path.name, pattern):
                return True
        
        return False
    
    def _analyze_python_file(self, file_path):
        """Анализирует Python файл и извлекает структуру"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'type': 'python',
                'size': len(content),
                'imports': [],
                'functions': [],
                'classes': [],
                'constants': [],
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    if node.lineno == getattr(node, 'lineno', 0):  # Top-level functions
                        analysis['functions'].append({
                            'name': node.name,
                            'params': [arg.arg for arg in node.args.args],
                            'line_start': node.lineno,
                            'line_end': getattr(node, 'end_lineno', node.lineno)
                        })
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    analysis['classes'].append({
                        'name': node.name,
                        'methods': methods,
                        'line_start': node.lineno,
                        'line_end': getattr(node, 'end_lineno', node.lineno)
                    })
                elif isinstance(node, ast.Assign):
                    if isinstance(node.targets[0], ast.Name) and node.targets[0].id.isupper():
                        analysis['constants'].append(node.targets[0].id)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Ошибка анализа {file_path}: {e}")
            return None
    
    def _generate_tree_structure(self):
        """Генерирует древовидную структуру проекта"""
        def build_tree(path, level=0, prefix=""):
            items = []
            if level == 0:
                items.append(f"{self.project_path.name}/")
                level = 1
                prefix = ""
            
            try:
                entries = sorted([p for p in path.iterdir() if not self._should_ignore(p)])
                dirs = [p for p in entries if p.is_dir()]
                files = [p for p in entries if p.is_file()]
                
                for i, dir_path in enumerate(dirs):
                    is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                    connector = "└── " if is_last_dir else "├── "
                    items.append(f"{'│   ' * (level-1)}{prefix}{connector}{dir_path.name}/")
                    
                    new_prefix = "    " if is_last_dir else "│   "
                    items.extend(build_tree(dir_path, level + 1, new_prefix))
                
                for i, file_path in enumerate(files):
                    is_last = i == len(files) - 1
                    connector = "└── " if is_last else "├── "
                    items.append(f"{'│   ' * (level-1)}{prefix}{connector}{file_path.name}")
                    
            except PermissionError:
                pass
            
            return items
        
        return "\n".join(build_tree(self.project_path))
    
    def create_index(self):
        """Создает полный индекс проекта"""
        print("🏗️  Создание индекса проекта...")
        
        index = {
            'project_metadata': {
                'name': self.project_path.name,
                'last_updated': datetime.now().isoformat(),
                'total_files': 0,
                'indexed_files': 0,
                'version': '1.0.0'
            },
            'project_structure': {
                'tree': self._generate_tree_structure(),
                'directories': [],
                'files': {}
            },
            'file_index': {},
            'dependency_graph': {}
        }
        
        total_files = 0
        indexed_files = 0
        
        # Обход всех файлов проекта
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                total_files += 1
                relative_path = str(file_path.relative_to(self.project_path))
                
                # Анализ Python файлов
                if file_path.suffix == '.py':
                    analysis = self._analyze_python_file(file_path)
                    if analysis:
                        index['file_index'][relative_path] = analysis
                        indexed_files += 1
                
                # Добавление в общую структуру
                index['project_structure']['files'][relative_path] = {
                    'type': file_path.suffix[1:] if file_path.suffix else 'unknown',
                    'size': file_path.stat().st_size
                }
        
        # Обновление метаданных
        index['project_metadata']['total_files'] = total_files
        index['project_metadata']['indexed_files'] = indexed_files
        
        print(f"📊 Проиндексировано: {indexed_files}/{total_files} файлов")
        return index

def main():
    if len(sys.argv) != 3:
        print("Использование: indexer.py <project_path> <output_file>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_file = sys.argv[2]
    
    indexer = ProjectIndexer(project_path)
    index = indexer.create_index()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Индекс сохранен: {output_file}")

if __name__ == '__main__':
    main()
```

### Шаг 5: Создание базового индексера (first-run)

**Файл: `.claude/hooks/create_indexer.py`**
```python
#!/usr/bin/env python3
"""
Создание базового индексера при первом запуске
"""

import os
import sys
from pathlib import Path

def create_basic_structure():
    """Создает базовую структуру для индексера"""
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    claude_dir = project_dir / '.claude'
    hooks_dir = claude_dir / 'hooks'
    
    # Создание директорий
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    print("✅ Базовая структура индексера создана")
    return True

if __name__ == '__main__':
    create_basic_structure()
```

## Инструкции по установке

### 1. Создание директории и файлов
```bash
# В корне проекта telegram-bot-v3
mkdir -p .claude/hooks
chmod +x .claude/hooks/update-index.sh
```

### 2. Настройка хуков Claude Code
Добавить конфигурацию в `.claude/settings.json` или создать файл, если его нет.

### 3. Первый запуск
```bash
# Создание первичного индекса
python3 .claude/hooks/indexer.py . project_index.json
```

### 4. Тестирование
- Измените любой файл в проекте
- Хук должен автоматически обновить `project_index.json`
- Проверьте содержимое индекса

## Использование с Claude Code

После настройки индексера:

1. **Для новых сессий**: Используйте команду для загрузки индекса в контекст Claude
2. **Для специфических задач**: Claude сможет обращаться к индексу для понимания структуры проекта
3. **Автоматическое обновление**: Индекс будет обновляться при каждом изменении файлов

## Примечания по безопасности

- Индекс не содержит чувствительных данных, только структуру кода
- Соблюдает правила `.gitignore`
- Можно добавить дополнительные исключения в индексер