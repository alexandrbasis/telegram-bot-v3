"""Test project structure validation."""
import importlib
import pytest
from pathlib import Path


class TestProjectStructure:
    """Validate the project structure meets requirements."""
    
    def test_src_packages_importable(self):
        """Test that all main src packages can be imported."""
        packages = [
            'src.bot',
            'src.services', 
            'src.data',
            'src.models',
            'src.config',
            'src.utils'
        ]
        
        for package in packages:
            try:
                importlib.import_module(package)
            except ImportError as e:
                pytest.fail(f"Failed to import {package}: {e}")
    
    def test_data_subdirectories_exist(self):
        """Test that data subdirectories are created."""
        base_path = Path(__file__).parent.parent
        data_dirs = [
            'src/data/repositories',
            'src/data/airtable',
        ]
        
        for dir_path in data_dirs:
            full_path = base_path / dir_path
            assert full_path.exists(), f"Directory {dir_path} does not exist"
            assert full_path.is_dir(), f"{dir_path} is not a directory"
    
    def test_test_structure_exists(self):
        """Test that test structure is properly created."""
        base_path = Path(__file__).parent.parent
        test_dirs = [
            'tests/unit/test_services',
            'tests/unit/test_data', 
            'tests/unit/test_models',
            'tests/integration/test_bot_handlers',
            'tests/fixtures'
        ]
        
        for dir_path in test_dirs:
            full_path = base_path / dir_path
            assert full_path.exists(), f"Test directory {dir_path} does not exist"
            assert full_path.is_dir(), f"{dir_path} is not a directory"
    
    def test_init_files_exist(self):
        """Test that __init__.py files exist in all Python packages."""
        base_path = Path(__file__).parent.parent
        init_files = [
            'src/__init__.py',
            'src/bot/__init__.py', 
            'src/bot/handlers/__init__.py',
            'src/services/__init__.py',
            'src/data/__init__.py',
            'src/data/repositories/__init__.py',
            'src/data/airtable/__init__.py',
            'src/models/__init__.py',
            'src/config/__init__.py',
            'src/utils/__init__.py',
            'tests/__init__.py',
            'tests/unit/__init__.py',
            'tests/integration/__init__.py',
            'tests/fixtures/__init__.py'
        ]
        
        for init_file in init_files:
            full_path = base_path / init_file
            assert full_path.exists(), f"__init__.py file {init_file} does not exist"
            assert full_path.is_file(), f"{init_file} is not a file"
    
    def test_project_config_files_exist(self):
        """Test that basic project configuration files exist."""
        base_path = Path(__file__).parent.parent
        config_files = [
            'README.md',
            '.gitignore', 
            '.env.example',
            'pyproject.toml'
        ]
        
        for config_file in config_files:
            full_path = base_path / config_file
            assert full_path.exists(), f"Config file {config_file} does not exist"
            assert full_path.is_file(), f"{config_file} is not a file"
    
    def test_requirements_files_exist(self):
        """Test that requirements files are created."""
        base_path = Path(__file__).parent.parent
        req_files = [
            'requirements/base.txt',
            'requirements/dev.txt',
            'requirements/test.txt'
        ]
        
        for req_file in req_files:
            full_path = base_path / req_file
            assert full_path.exists(), f"Requirements file {req_file} does not exist"
            assert full_path.is_file(), f"{req_file} is not a file"
    
    def test_supporting_directories_exist(self):
        """Test that supporting directories are created."""
        base_path = Path(__file__).parent.parent
        support_dirs = [
            'data/backups',
            'data/exports', 
            'data/cache',
            'scripts'
        ]
        
        for dir_path in support_dirs:
            full_path = base_path / dir_path
            assert full_path.exists(), f"Supporting directory {dir_path} does not exist"
            assert full_path.is_dir(), f"{dir_path} is not a directory"