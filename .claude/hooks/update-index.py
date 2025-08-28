#!/usr/bin/env python3
"""
Project Index Updater для telegram-bot-v3

Автоматически обновляет project_index.json при изменениях в структуре проекта.
Анализирует Python файлы и извлекает ключевую информацию для AI-агентов.
"""

import os
import json
import ast
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import fnmatch
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('indexer')

class ProjectIndexer:
    """Индексер проекта для создания структурированного представления."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.gitignore_patterns = self._load_gitignore()
        self.src_path = self.project_path / 'src'
        
    def _load_gitignore(self) -> List[str]:
        """Загружает паттерны из .gitignore для исключения файлов."""
        gitignore_path = self.project_path / '.gitignore'
        default_patterns = [
            '__pycache__', '*.pyc', '*.pyo', '*.pyd', 
            '.git', 'venv', '.env', '.venv',
            '*.egg-info', 'dist', 'build',
            '.DS_Store', '.pytest_cache'
        ]
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    patterns = [line.strip() for line in f 
                              if line.strip() and not line.startswith('#')]
                    default_patterns.extend(patterns)
            except Exception as e:
                logger.warning(f"Ошибка чтения .gitignore: {e}")
        
        return default_patterns
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Проверяет, должен ли файл быть игнорирован."""
        try:
            relative_path = file_path.relative_to(self.project_path)
            
            for pattern in self.gitignore_patterns:
                if fnmatch.fnmatch(str(relative_path), pattern):
                    return True
                if fnmatch.fnmatch(relative_path.name, pattern):
                    return True
                    
        except ValueError:
            # Файл не в проекте
            return True
            
        return False
    
    def _analyze_python_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Анализирует Python файл и извлекает структурную информацию."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'role': self._determine_file_role(file_path),
                'purpose': self._extract_module_docstring(tree),
                'key_exports': [],
                'dependencies': [],
                'features': []
            }
            
            # Анализ импортов
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        if alias.name.startswith('src.'):
                            analysis['dependencies'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        if node.module.startswith('src.'):
                            analysis['dependencies'].append(node.module)
            
            # Анализ экспортов
            exports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Публичные функции
                        exports.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    exports.append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            exports.append(target.id)
            
            analysis['key_exports'] = exports[:5]  # Топ 5 экспортов
            
            # Определение особенностей файла
            analysis['features'] = self._detect_features(tree, content)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Ошибка анализа {file_path}: {e}")
            return None
    
    def _determine_file_role(self, file_path: Path) -> str:
        """Определяет роль файла в архитектуре."""
        relative_path = str(file_path.relative_to(self.project_path))
        
        if 'main.py' in file_path.name:
            return 'application_entry_point'
        elif 'test_' in file_path.name or '/tests/' in relative_path:
            return 'test'
        elif '/models/' in relative_path:
            return 'domain_model'
        elif '/services/' in relative_path:
            return 'business_service'
        elif '/data/' in relative_path or '/repositories/' in relative_path:
            return 'data_access_layer'
        elif '/bot/' in relative_path or '/handlers/' in relative_path:
            return 'presentation_layer'
        elif '/config/' in relative_path:
            return 'configuration'
        elif '/utils/' in relative_path:
            return 'utility'
        else:
            return 'module'
    
    def _extract_module_docstring(self, tree: ast.AST) -> str:
        """Извлекает docstring модуля."""
        if (isinstance(tree, ast.Module) and tree.body and 
            isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant)):
            docstring = tree.body[0].value.value
            if isinstance(docstring, str):
                # Берем первую строку docstring
                return docstring.split('\n')[0].strip()
        return ""
    
    def _detect_features(self, tree: ast.AST, content: str) -> List[str]:
        """Определяет особенности и паттерны в коде."""
        features = []
        
        # Проверка на async/await
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                features.append('async_patterns')
                break
        
        # Проверка на Pydantic
        if 'pydantic' in content or 'BaseModel' in content:
            features.append('pydantic_validation')
        
        # Проверка на enum
        if 'from enum import' in content or 'Enum' in content:
            features.append('enum_types')
        
        # Проверка на Airtable интеграцию
        if 'airtable' in content.lower():
            features.append('airtable_integration')
        
        # Проверка на логирование
        if 'logging' in content:
            features.append('logging')
            
        return features
    
    def _generate_project_tree(self) -> str:
        """Генерирует древовидное представление проекта."""
        def build_tree_part(path: Path, level: int = 0, is_last: bool = True) -> List[str]:
            items = []
            
            if level == 0:
                items.append(f"{self.project_path.name}/")
                level = 1
            
            try:
                # Получаем только важные директории и файлы
                entries = []
                if path.is_dir():
                    for item in sorted(path.iterdir()):
                        if not self._should_ignore(item):
                            entries.append(item)
                
                # Разделяем на директории и файлы
                dirs = [p for p in entries if p.is_dir()]
                files = [p for p in entries if p.is_file() and self._is_important_file(p)]
                
                all_items = dirs + files
                
                for i, item in enumerate(all_items):
                    is_last_item = (i == len(all_items) - 1)
                    prefix = "└── " if is_last_item else "├── "
                    indent = "    " * (level - 1)
                    
                    if item.is_dir():
                        items.append(f"{indent}{prefix}{item.name}/")
                        if level < 3:  # Ограничиваем глубину
                            sub_items = build_tree_part(item, level + 1, is_last_item)
                            items.extend(sub_items)
                    else:
                        description = self._get_file_description(item)
                        display_name = f"{item.name} ({description})" if description else item.name
                        items.append(f"{indent}{prefix}{display_name}")
                        
            except PermissionError:
                pass
                
            return items
        
        tree_lines = build_tree_part(self.project_path)
        return '\n'.join(tree_lines)
    
    def _is_important_file(self, file_path: Path) -> bool:
        """Определяет, является ли файл важным для отображения в дереве."""
        important_files = {
            'main.py', 'settings.py', 'conftest.py', 
            'README.md', 'CLAUDE.md', 'requirements.txt',
            'pyproject.toml', 'start_bot.sh', 'project_index.json'
        }
        
        important_patterns = ['*.py', '*.md', '*.txt', '*.toml', '*.sh', '*.json']
        
        if file_path.name in important_files:
            return True
            
        for pattern in important_patterns:
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
                
        return False
    
    def _get_file_description(self, file_path: Path) -> str:
        """Получает краткое описание файла."""
        descriptions = {
            'main.py': 'application entry point',
            'settings.py': 'centralized app configuration',
            'conftest.py': 'pytest configuration',
            'participant.py': 'participant data model with enums',
            'search_service.py': 'fuzzy search with Russian/English support',
            'search_conversation.py': 'main search conversation flow',
            'airtable_client.py': 'low-level Airtable API client',
            'airtable_participant_repo.py': 'participant repository',
            'field_mappings.py': 'Airtable field ID mappings',
            'CLAUDE.md': 'project guidance for Claude Code',
            'start_bot.sh': 'bot startup script'
        }
        
        return descriptions.get(file_path.name, '')
    
    def update_index(self) -> Dict[str, Any]:
        """Обновляет индекс проекта."""
        logger.info("🔍 Начинаю обновление индекса проекта...")
        
        # Загружаем существующий индекс
        index_file = self.project_path / 'project_index.json'
        existing_index = {}
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
                logger.info("📄 Загружен существующий индекс")
            except Exception as e:
                logger.warning(f"Ошибка загрузки существующего индекса: {e}")
        
        # Получаем список всех существующих файлов для обнаружения удаленных
        current_files = set()
        if self.src_path.exists():
            for py_file in self.src_path.rglob('*.py'):
                if not self._should_ignore(py_file) and py_file.name != '__init__.py':
                    relative_path = str(py_file.relative_to(self.project_path))
                    current_files.add(relative_path)
        
        # Найти удаленные файлы
        old_files = set()
        if 'key_modules' in existing_index:
            old_files = set(existing_index['key_modules'].keys())
        
        deleted_files = old_files - current_files
        new_files = current_files - old_files
        
        if deleted_files:
            logger.info(f"🗑️  Удалены файлы: {', '.join(deleted_files)}")
        if new_files:
            logger.info(f"➕ Добавлены файлы: {', '.join(new_files)}")
        
        # Создаем новую версию индекса
        updated_index = {
            "project_overview": {
                "name": "telegram-bot-v3",
                "description": "Telegram bot for participant management with Airtable integration and Russian/English fuzzy search",
                "architecture": "3-layer architecture (bot/services/data) with repository pattern",
                "main_language": "python",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # Сохраняем структуру проекта
        updated_index["project_structure"] = {
            "tree": self._generate_project_tree(),
            "directory_details": existing_index.get("project_structure", {}).get("directory_details", {}),
            "key_files": existing_index.get("project_structure", {}).get("key_files", {})
        }
        
        # Анализируем ключевые модули
        key_modules = {}
        python_files_analyzed = 0
        
        if self.src_path.exists():
            for py_file in self.src_path.rglob('*.py'):
                if not self._should_ignore(py_file) and py_file.name != '__init__.py':
                    relative_path = str(py_file.relative_to(self.project_path))
                    analysis = self._analyze_python_file(py_file)
                    
                    if analysis:
                        key_modules[relative_path] = analysis
                        python_files_analyzed += 1
        
        updated_index["key_modules"] = key_modules
        
        # Сохраняем остальные разделы из существующего индекса
        sections_to_preserve = [
            "architecture_patterns", "key_features", 
            "current_development_context", "testing_approach",
            "environment_requirements"
        ]
        
        for section in sections_to_preserve:
            if section in existing_index:
                updated_index[section] = existing_index[section]
        
        # Обновляем статистику
        updated_index["project_statistics"] = {
            "total_python_files": python_files_analyzed,
            "main_directories": ["src/bot", "src/services", "src/data", "src/models", "src/config", "tests"],
            "key_dependencies": ["telegram", "airtable", "pydantic", "rapidfuzz", "pytest"]
        }
        
        logger.info(f"✅ Проанализировано {python_files_analyzed} Python файлов")
        return updated_index

def main():
    """Основная функция обновления индекса."""
    if len(sys.argv) < 2:
        project_path = Path.cwd()
    else:
        project_path = Path(sys.argv[1])
    
    if not project_path.exists():
        logger.error(f"❌ Путь к проекту не существует: {project_path}")
        sys.exit(1)
    
    try:
        indexer = ProjectIndexer(str(project_path))
        updated_index = indexer.update_index()
        
        # Сохраняем обновленный индекс
        index_file = project_path / 'project_index.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(updated_index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Индекс успешно обновлен: {index_file}")
        print(f"🎉 Индекс проекта обновлен: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обновления индекса: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()