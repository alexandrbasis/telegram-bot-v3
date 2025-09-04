#!/usr/bin/env python3
"""
Project Index Updater for telegram-bot-v3

Keep a simple, reliable map of the project with short descriptions of
where to find key components. This implementation favors clarity over
deep static analysis.
"""

import os
import json
import ast
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import fnmatch
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('indexer')

class ProjectIndexer:
    """Builds a lightweight, meaningful project index."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.gitignore_patterns = self._load_gitignore()
        self.src_path = self.project_path / 'src'
        # Only show these top-level directories and files in the tree
        self.whitelisted_top_dirs = ['src', 'tests', 'docs', '.claude']
        self.whitelisted_top_files = [
            'README.md', 'CLAUDE.md', 'pyproject.toml', 'project_index.json',
            'start_bot.sh', '.env.example'
        ]
        
    def _load_gitignore(self) -> List[str]:
        """Load .gitignore patterns and normalize for matching.

        We normalize trailing slashes and add directory-name variants so that
        patterns like "logs/" also match the directory name "logs".
        """
        gitignore_path = self.project_path / '.gitignore'
        default_patterns = [
            '__pycache__', '*.pyc', '*.pyo', '*.pyd',
            '.git', '.hg', '.svn',
            'venv', 'env', '.env', '.venv',
            '*.egg-info', 'dist', 'build',
            '.DS_Store', '.pytest_cache', '.mypy_cache', '.coverage', 'htmlcov',
        ]

        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for raw in f:
                        line = raw.strip()
                        if not line or line.startswith('#'):
                            continue
                        norm = line.rstrip('/')
                        default_patterns.append(norm)
                        # Ensure directory patterns also match nested paths
                        if line.endswith('/') or '/' not in norm:
                            default_patterns.append(f"**/{norm}")
                            default_patterns.append(f"**/{norm}/**")
            except Exception as e:
                logger.warning(f"Ошибка чтения .gitignore: {e}")

        return default_patterns
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Return True if a path should be ignored.

        - Honor normalized .gitignore patterns
        - Ignore hidden directories by default, except allow ".claude"
        - Ignore common build/cache folders
        """
        try:
            relative_path = file_path.relative_to(self.project_path)

            # Ignore hidden directories except .claude
            for part in relative_path.parts:
                if part.startswith('.') and part not in {'.', '..', '.claude'}:
                    return True

            for pattern in self.gitignore_patterns:
                if fnmatch.fnmatch(str(relative_path), pattern):
                    return True
                if fnmatch.fnmatch(relative_path.name, pattern):
                    return True

        except ValueError:
            # Outside project
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
        """Generate a compact, curated tree for key areas only."""
        root = self.project_path

        def list_dir(path: Path) -> Tuple[List[Path], List[Path]]:
            try:
                items = [p for p in sorted(path.iterdir()) if not self._should_ignore(p)]
            except Exception:
                items = []
            dirs = [p for p in items if p.is_dir()]
            files = [p for p in items if p.is_file()]
            return dirs, files

        lines: List[str] = [f"{root.name}/"]

        # Top-level: selected files and whitelisted dirs only
        top_dirs, top_files = list_dir(root)
        top_dirs = [d for d in top_dirs if d.name in self.whitelisted_top_dirs]
        top_files = [f for f in top_files if f.name in self.whitelisted_top_files]

        def add(prefix: str, name: str):
            lines.append(f"{prefix}{name}")

        # Helper to draw a directory with one level of children
        def draw_dir(dir_path: Path, is_last: bool):
            prefix = "└── " if is_last else "├── "
            add(prefix, f"{dir_path.name}/")
            child_dirs, child_files = list_dir(dir_path)
            # Only show a shallow view (1 level)
            child_dirs = [d for d in child_dirs if not d.name.startswith('__')]
            child_files = [f for f in child_files if self._is_important_file(f)]

            for i, d in enumerate(child_dirs):
                sub_last = (i == len(child_dirs) - 1) and not child_files
                add(f"    {'└── ' if sub_last else '├── '}", f"{d.name}/")
            for j, f in enumerate(child_files):
                is_last_file = (j == len(child_files) - 1)
                name = f.name
                desc = self._get_file_description(f)
                display = f"{name} ({desc})" if desc else name
                add("    └── " if is_last_file else "    ├── ", display)

        # Render top-level dirs
        for i, d in enumerate(top_dirs):
            draw_dir(d, is_last=(i == len(top_dirs) - 1 and not top_files))

        # Render top-level files after dirs
        for j, f in enumerate(top_files):
            is_last = (j == len(top_files) - 1)
            name = f.name
            desc = self._get_file_description(f)
            display = f"{name} ({desc})" if desc else name
            add("└── " if is_last else "├── ", display)

        return "\n".join(lines)
    
    def _is_important_file(self, file_path: Path) -> bool:
        """Return True if the file is worth showing in the tree."""
        important_files = {
            'main.py', 'settings.py', 'conftest.py',
            'README.md', 'CLAUDE.md', 'requirements.txt',
            'pyproject.toml', 'start_bot.sh', 'project_index.json',
            '.env.example'
        }

        if file_path.name in important_files:
            return True

        if file_path.suffix in {'.py', '.md', '.toml', '.sh'}:
            if file_path.name.startswith('__'):
                return False
            return True

        return False
    
    def _get_file_description(self, file_path: Path) -> str:
        """Return a short description for known key files."""
        descriptions = {
            'main.py': 'application entry point',
            'settings.py': 'centralized app configuration',
            'conftest.py': 'pytest configuration',
            'participant.py': 'participant data model with enums',
            'search_service.py': 'fuzzy search utilities',
            'search_conversation.py': 'search conversation flow',
            'airtable_client.py': 'Airtable API client',
            'airtable_participant_repo.py': 'participant repository',
            'field_mappings.py': 'Airtable field mappings',
            'CLAUDE.md': 'Claude Code project guidance',
            'start_bot.sh': 'bot startup script',
            'README.md': 'project overview',
            '.env.example': 'sample environment variables',
        }
        return descriptions.get(file_path.name, '')
    
    def _dir_description(self, rel_path: str) -> str:
        mapping = {
            'src': 'application source code',
            'src/bot': 'Telegram bot handlers and keyboards',
            'src/bot/handlers': 'bot command and conversation handlers',
            'src/bot/keyboards': 'bot inline/reply keyboards',
            'src/services': 'business services and domain logic',
            'src/data': 'data access layer and integrations',
            'src/data/airtable': 'Airtable client and repository',
            'src/data/repositories': 'domain repositories',
            'src/models': 'data models and enums',
            'src/config': 'configuration and settings',
            'src/utils': 'utility helpers',
            'tests': 'test suite (unit and integration)',
            'docs': 'documentation and guides',
            '.claude': 'Claude Code configuration and hooks',
            '.claude/commands': 'custom Claude commands',
            '.claude/hooks': 'automation hooks (index, notifications)',
        }
        return mapping.get(rel_path, '')

    def _collect_locations(self) -> Dict[str, str]:
        locations: Dict[str, str] = {}
        candidates = [
            'src/main.py', 'src/bot', 'src/bot/handlers', 'src/bot/keyboards',
            'src/services', 'src/data', 'src/data/airtable', 'src/models',
            'src/config', 'src/utils', 'tests', 'docs', '.claude',
            '.claude/hooks', '.claude/commands', 'README.md', 'CLAUDE.md',
            'pyproject.toml', 'start_bot.sh', '.env.example'
        ]
        for rel in candidates:
            p = self.project_path / rel
            if p.exists():
                desc = self._dir_description(rel) if p.is_dir() else self._get_file_description(p)
                locations[rel] = desc
        return locations

    def _read_readme_description(self) -> str:
        readme = self.project_path / 'README.md'
        if not readme.exists():
            return ''
        try:
            with open(readme, 'r', encoding='utf-8') as f:
                for line in f:
                    clean = line.strip()
                    if clean and not clean.startswith('#'):
                        return clean
        except Exception:
            pass
        return ''

    def update_index(self) -> Dict[str, Any]:
        """Build a simplified, meaningful index of the project."""
        logger.info("🔍 Updating simplified project index...")

        index_file = self.project_path / 'project_index.json'
        existing_index: Dict[str, Any] = {}
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
            except Exception as e:
                logger.warning(f"Ошибка загрузки существующего индекса: {e}")

        overview_description = self._read_readme_description() or (
            "Telegram bot for participant management with Airtable integration"
        )

        updated_index: Dict[str, Any] = {
            "index_version": 2,
            "project_overview": {
                "name": self.project_path.name,
                "description": overview_description,
                "main_language": "python",
                "last_updated": datetime.now().isoformat(),
            },
            "project_structure": {
                "tree": self._generate_project_tree(),
                "locations": self._collect_locations(),
            },
        }

        # Preserve optional user-authored sections if present
        for section in [
            "architecture_patterns",
            "key_features",
            "current_development_context",
            "testing_approach",
            "environment_requirements",
        ]:
            if section in existing_index and section not in updated_index:
                updated_index[section] = existing_index[section]

        # Lightweight stats
        py_count = 0
        if self.src_path.exists():
            for py_file in self.src_path.rglob('*.py'):
                if not self._should_ignore(py_file):
                    py_count += 1
        updated_index["project_statistics"] = {
            "total_python_files": py_count,
            "main_directories": [d for d in self.whitelisted_top_dirs if (self.project_path / d).exists()],
        }

        logger.info(f"✅ Index prepared. Python files counted: {py_count}")
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
