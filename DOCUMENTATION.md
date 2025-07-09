# ПОЛНАЯ ДОКУМЕНТАЦИЯ ПРОЕКТА MCPИСЯ

## Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Структура проекта](#структура-проекта)
4. [Установка и настройка](#установка-и-настройка)
5. [API Документация](#api-документация)
6. [Разработка](#разработка)
7. [Тестирование](#тестирование)
8. [Конфигурация](#конфигурация)
9. [Безопасность](#безопасность)
10. [Лицензирование](#лицензирование)
11. [Устранение неполадок](#устранение-неполадок)

## Обзор проекта

**MCPИСЯ** - это реализация MCP (Model Context Protocol), объединяющая возможности файловой системы и управления памятью. Название проекта представляет собой игру слов, сочетающую аббревиатуру MCP с элементами русского языка.

### Цели проекта

- Предоставление единого интерфейса для работы с файловой системой и памятью
- Реализация спецификации Model Context Protocol
- Обеспечение безопасного и эффективного доступа к системным ресурсам
- Создание масштабируемой архитектуры для интеграции с различными AI-системами

### Ключевые особенности

- **Файловая система**: Безопасные операции с файлами и директориями
- **Управление памятью**: Эффективная работа с состоянием и кэшированием
- **MCP-совместимость**: Полная поддержка спецификации Model Context Protocol
- **Модульная архитектура**: Четкое разделение компонентов
- **Типизация**: Полная поддержка Python type hints

## Архитектура системы

### Основные компоненты

```
MCPИСЯ
├── Filesystem Component
│   ├── File Operations
│   ├── Directory Management
│   ├── Security Layer
│   └── Path Validation
├── Memory Component
│   ├── State Management
│   ├── Caching System
│   ├── Memory Allocation
│   └── Garbage Collection
└── MCP Server
    ├── Protocol Handler
    ├── Tool Registry
    ├── Request Router
    └── Response Formatter
```

### Принципы архитектуры

1. **Разделение ответственности**: Каждый компонент отвечает за свою область
2. **Слабая связанность**: Минимальные зависимости между модулями
3. **Высокая когезия**: Логически связанные функции объединены
4. **Расширяемость**: Возможность добавления новых компонентов
5. **Безопасность**: Валидация на каждом уровне

## Структура проекта

### Текущая структура

```
MCP-/
├── .git/                    # Git репозиторий
├── .claude/                 # Настройки Claude
│   └── settings.local.json  # Локальные разрешения
├── CLAUDE.md               # Руководство для разработки с Claude
├── LICENSE                 # GPL v2 лицензия
├── README.md              # Базовое описание
├── .gitignore             # Исключения Git
└── DOCUMENTATION.md       # Данная документация
```

### Планируемая структура

```
MCP-/
├── src/                    # Исходный код
│   ├── __init__.py
│   ├── filesystem/         # Компоненты файловой системы
│   │   ├── __init__.py
│   │   ├── operations.py   # Основные операции
│   │   ├── security.py     # Безопасность
│   │   └── validation.py   # Валидация путей
│   ├── memory/            # Компоненты памяти
│   │   ├── __init__.py
│   │   ├── manager.py     # Менеджер памяти
│   │   ├── cache.py       # Кэширование
│   │   └── state.py       # Управление состоянием
│   ├── server.py          # Главный MCP сервер
│   ├── tools.py           # Определения инструментов
│   └── utils.py           # Вспомогательные функции
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── test_filesystem.py
│   ├── test_memory.py
│   ├── test_server.py
│   └── fixtures/          # Тестовые данные
├── docs/                  # Дополнительная документация
│   ├── api.md
│   ├── examples/
│   └── guides/
├── config/                # Конфигурационные файлы
├── requirements.txt       # Python зависимости
├── pyproject.toml        # Конфигурация проекта
├── setup.py              # Установочный скрипт
└── Makefile              # Автоматизация задач
```

## Установка и настройка

### Системные требования

- Python 3.8+
- Git
- Операционная система: macOS, Linux, Windows
- Минимум 512MB RAM
- 100MB свободного места на диске

### Установка

#### 1. Клонирование репозитория

```bash
git clone <repository-url> MCP-
cd MCP-
```

#### 2. Создание виртуального окружения

```bash
# Создание окружения
python -m venv venv

# Активация (Unix/macOS)
source venv/bin/activate

# Активация (Windows)
venv\Scripts\activate
```

#### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 4. Настройка переменных окружения

```bash
# Создание .env файла
cp .env.example .env

# Редактирование настроек
vim .env
```

### Настройка разработки

#### Установка инструментов разработки

```bash
pip install -e .[dev]
```

#### Настройка pre-commit hooks

```bash
pre-commit install
```

#### Настройка IDE (VS Code / Cursor)

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black"
}
```

## API Документация

### Основные интерфейсы

#### FilesystemComponent

```python
class FilesystemComponent:
    """Компонент для работы с файловой системой."""
    
    def read_file(self, path: str) -> str:
        """Чтение содержимого файла."""
        
    def write_file(self, path: str, content: str) -> bool:
        """Запись содержимого в файл."""
        
    def list_directory(self, path: str) -> List[str]:
        """Получение списка файлов в директории."""
        
    def create_directory(self, path: str) -> bool:
        """Создание директории."""
        
    def delete_file(self, path: str) -> bool:
        """Удаление файла."""
        
    def file_exists(self, path: str) -> bool:
        """Проверка существования файла."""
```

#### MemoryComponent

```python
class MemoryComponent:
    """Компонент для управления памятью."""
    
    def store(self, key: str, value: Any) -> bool:
        """Сохранение значения в памяти."""
        
    def retrieve(self, key: str) -> Optional[Any]:
        """Получение значения из памяти."""
        
    def delete(self, key: str) -> bool:
        """Удаление значения из памяти."""
        
    def clear(self) -> bool:
        """Очистка всей памяти."""
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики использования памяти."""
```

#### MCPServer

```python
class MCPServer:
    """Основной MCP сервер."""
    
    def start(self, host: str = "localhost", port: int = 8000) -> None:
        """Запуск сервера."""
        
    def stop(self) -> None:
        """Остановка сервера."""
        
    def register_tool(self, tool: Tool) -> None:
        """Регистрация нового инструмента."""
        
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Обработка MCP запроса."""
```

### Инструменты MCP

#### filesystem_read

Чтение содержимого файла.

**Параметры:**

- `path` (string): Путь к файлу

**Возврат:**

- `content` (string): Содержимое файла

#### filesystem_write

Запись содержимого в файл.

**Параметры:**

- `path` (string): Путь к файлу
- `content` (string): Содержимое для записи

**Возврат:**

- `success` (boolean): Результат операции

#### memory_store

Сохранение данных в памяти.

**Параметры:**

- `key` (string): Ключ для сохранения
- `value` (any): Значение для сохранения

**Возврат:**

- `success` (boolean): Результат операции

#### memory_retrieve

Получение данных из памяти.

**Параметры:**

- `key` (string): Ключ для получения

**Возврат:**

- `value` (any): Сохраненное значение

## Разработка

### Стандарты кодирования

#### Python Style Guide

- Следуйте PEP 8
- Используйте type hints для всех функций
- Документируйте все публичные API с помощью docstrings
- Максимальная длина строки: 88 символов (Black)

#### Примеры кода

```python
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExampleClass:
    """Пример класса с правильным оформлением."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Инициализация класса.
        
        Args:
            name: Имя экземпляра
            config: Опциональная конфигурация
        """
        self.name = name
        self.config = config or {}
        self._private_data: List[str] = []
    
    def process_data(self, data: List[str]) -> Dict[str, int]:
        """Обработка данных.
        
        Args:
            data: Список строк для обработки
            
        Returns:
            Словарь с результатами обработки
            
        Raises:
            ValueError: При некорректных входных данных
        """
        if not data:
            raise ValueError("Данные не могут быть пустыми")
        
        result = {}
        for item in data:
            result[item] = len(item)
            
        logger.info(f"Обработано {len(data)} элементов")
        return result
```

### Инструменты разработки

#### Форматирование кода

```bash
# Black для форматирования
black src/ tests/

# isort для сортировки импортов
isort src/ tests/
```

#### Проверка типов

```bash
# mypy для проверки типов
mypy src/
```

#### Линтинг

```bash
# flake8 для проверки стиля
flake8 src/ tests/

# pylint для углубленного анализа
pylint src/
```

### Git Workflow

#### Именование веток

- `feature/название-функции` - новые функции
- `bugfix/описание-бага` - исправления ошибок
- `hotfix/критическое-исправление` - критические исправления
- `refactor/область-рефакторинга` - рефакторинг кода

#### Коммиты

Используйте Conventional Commits:

```
feat: добавление новой функции
fix: исправление ошибки
docs: обновление документации
style: изменения в стиле кода
refactor: рефакторинг без изменения функциональности
test: добавление или изменение тестов
chore: изменения в инфраструктуре
```

## Тестирование

### Структура тестов

#### Unit Tests

```python
import pytest
from src.filesystem.operations import FilesystemOperations

class TestFilesystemOperations:
    """Тесты для операций с файловой системой."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.fs_ops = FilesystemOperations()
    
    def test_read_existing_file(self, tmp_path):
        """Тест чтения существующего файла."""
        test_file = tmp_path / "test.txt"
        test_content = "Тестовое содержимое"
        test_file.write_text(test_content)
        
        result = self.fs_ops.read_file(str(test_file))
        assert result == test_content
    
    def test_read_nonexistent_file(self):
        """Тест чтения несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            self.fs_ops.read_file("/path/to/nonexistent/file")
```

#### Integration Tests

```python
import pytest
from src.server import MCPServer
from src.filesystem import FilesystemComponent
from src.memory import MemoryComponent

class TestMCPIntegration:
    """Интеграционные тесты MCP сервера."""
    
    @pytest.fixture
    def server(self):
        """Фикстура для создания тестового сервера."""
        fs_component = FilesystemComponent()
        memory_component = MemoryComponent()
        return MCPServer(fs_component, memory_component)
    
    def test_full_workflow(self, server, tmp_path):
        """Тест полного рабочего процесса."""
        # Тест создания файла через MCP
        request = {
            "method": "call_tool",
            "params": {
                "name": "filesystem_write",
                "arguments": {
                    "path": str(tmp_path / "test.txt"),
                    "content": "Тест"
                }
            }
        }
        
        response = server.handle_request(request)
        assert response["result"]["success"] is True
```

### Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src --cov-report=html

# Запуск определенного файла тестов
pytest tests/test_filesystem.py

# Запуск с детальным выводом
pytest -v

# Запуск только быстрых тестов
pytest -m "not slow"
```

### Покрытие кода

Цель: поддержание покрытия кода на уровне минимум 80%.

```bash
# Генерация отчета о покрытии
coverage run -m pytest
coverage report
coverage html
```

## Конфигурация

### Файлы конфигурации

#### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "mcpisia"
description = "MCP implementation combining filesystem and memory components"
authors = [{name = "MCP Team"}]
license = {text = "GPL-2.0"}
requires-python = ">=3.8"
dependencies = [
    "pydantic>=1.8.0",
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.12",
    "black>=21.6b0",
    "isort>=5.9.0",
    "mypy>=0.910",
    "flake8>=3.9.0",
    "pre-commit>=2.15.0",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

#### .env.example

```bash
# Основные настройки
MCP_HOST=localhost
MCP_PORT=8000
MCP_DEBUG=true

# Файловая система
FS_ROOT_PATH=/tmp/mcpisia
FS_MAX_FILE_SIZE=10485760  # 10MB
FS_ALLOWED_EXTENSIONS=.txt,.json,.md,.py

# Память
MEMORY_MAX_SIZE=134217728  # 128MB
MEMORY_TTL=3600  # 1 час

# Логирование
LOG_LEVEL=INFO
LOG_FILE=mcpisia.log

# Безопасность
SECURITY_SANDBOX_MODE=true
SECURITY_MAX_REQUESTS_PER_MINUTE=100
```

### Claude настройки (.claude/settings.local.json)

```json
{
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(find:*)",
      "Bash(gh issue create:*)",
      "Bash(pytest:*)",
      "Bash(python:*)"
    ],
    "deny": [
      "Bash(rm:*)",
      "Bash(sudo:*)"
    ]
  },
  "project_settings": {
    "python_version": "3.8+",
    "code_style": "black",
    "type_checking": true,
    "documentation_language": "ru"
  }
}
```

## Безопасность

### Принципы безопасности

1. **Принцип минимальных привилегий**: Предоставление только необходимых разрешений
2. **Валидация входных данных**: Проверка всех пользовательских входов
3. **Sandboxing**: Изоляция операций с файловой системой
4. **Аудит**: Логирование всех критических операций
5. **Шифрование**: Защита чувствительных данных

### Реализация безопасности

#### Валидация путей

```python
import os
from pathlib import Path
from typing import Union

class PathValidator:
    """Валидатор путей для обеспечения безопасности."""
    
    def __init__(self, allowed_root: str):
        self.allowed_root = Path(allowed_root).resolve()
    
    def validate_path(self, path: Union[str, Path]) -> Path:
        """Валидация пути.
        
        Args:
            path: Путь для валидации
            
        Returns:
            Нормализованный безопасный путь
            
        Raises:
            SecurityError: При небезопасном пути
        """
        normalized_path = Path(path).resolve()
        
        # Проверка на path traversal
        if not str(normalized_path).startswith(str(self.allowed_root)):
            raise SecurityError(f"Путь вне разрешенной области: {path}")
        
        return normalized_path
```

#### Ограничения доступа

```python
class SecurityManager:
    """Менеджер безопасности."""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.txt', '.json', '.md', '.py'}
        self.rate_limiter = RateLimiter()
    
    def check_file_access(self, path: Path, operation: str) -> bool:
        """Проверка разрешения на операцию с файлом."""
        # Проверка расширения
        if path.suffix not in self.allowed_extensions:
            return False
        
        # Проверка размера для записи
        if operation == 'write' and path.stat().st_size > self.max_file_size:
            return False
        
        # Проверка rate limiting
        if not self.rate_limiter.check_limit():
            return False
        
        return True
```

### Аудит и логирование

```python
import logging
from typing import Any, Dict

class SecurityLogger:
    """Логгер событий безопасности."""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_access(self, operation: str, path: str, success: bool, 
                   metadata: Dict[str, Any] = None) -> None:
        """Логирование операции доступа."""
        metadata = metadata or {}
        self.logger.info(
            f"Access {operation} on {path}: {'SUCCESS' if success else 'FAILED'} "
            f"- {metadata}"
        )
```

## Лицензирование

Проект распространяется под лицензией **GNU General Public License v2.0**.

### Ключевые моменты лицензии

1. **Свободное использование**: Можно использовать программу для любых целей
2. **Изучение и модификация**: Доступ к исходному коду и право изменения
3. **Распространение**: Право распространения копий программы
4. **Copyleft**: Производные работы должны распространяться под той же лицензией
5. **Отсутствие гарантий**: Программа предоставляется "как есть"

### Обязательства при использовании

- При распространении необходимо включать лицензию
- Изменения должны быть помечены
- Исходный код должен быть доступен получателям
- Производные работы должны использовать GPL v2

### Файл COPYRIGHT

```
MCPИСЯ - MCP implementation combining filesystem and memory components
Copyright (C) 2024 MCP Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```

## Устранение неполадок

### Частые проблемы и решения

#### 1. Ошибки импорта модулей

**Проблема**: `ModuleNotFoundError: No module named 'src'`

**Решение**:

```bash
# Установка в режиме разработки
pip install -e .

# Или добавление в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### 2. Проблемы с правами доступа

**Проблема**: `PermissionError: [Errno 13] Permission denied`

**Решение**:

```bash
# Проверка прав на директорию
ls -la /path/to/directory

# Изменение прав (осторожно!)
chmod 755 /path/to/directory
```

#### 3. Ошибки валидации путей

**Проблема**: `SecurityError: Путь вне разрешенной области`

**Решение**:

```python
# Настройка корневой директории в конфигурации
FS_ROOT_PATH=/safe/directory/path

# Проверка абсолютных путей
import os
print(os.path.abspath('relative/path'))
```

#### 4. Проблемы с памятью

**Проблема**: `MemoryError: Превышен лимит памяти`

**Решение**:

```bash
# Увеличение лимита в конфигурации
MEMORY_MAX_SIZE=268435456  # 256MB

# Очистка кэша
curl -X POST http://localhost:8000/memory/clear
```

### Диагностика

#### Проверка состояния системы

```python
def system_health_check():
    """Проверка состояния системы."""
    checks = {
        'filesystem_writable': check_filesystem_access(),
        'memory_available': check_memory_usage(),
        'dependencies_installed': check_dependencies(),
        'configuration_valid': validate_configuration()
    }
    
    for check, status in checks.items():
        print(f"{check}: {'OK' if status else 'FAIL'}")
    
    return all(checks.values())
```

#### Логирование отладки

```python
import logging

# Включение отладочного логирования
logging.basicConfig(level=logging.DEBUG)

# Логирование в файл
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Получение помощи

1. **Документация**: Проверьте эту документацию и файл CLAUDE.md
2. **Issues**: Создайте issue в репозитории GitHub
3. **Debugging**: Включите отладочное логирование
4. **Тесты**: Запустите тесты для проверки базовой функциональности

```bash
# Быстрая проверка системы
make health-check

# Запуск диагностических тестов
pytest tests/test_diagnostics.py -v

# Генерация отчета о системе
python -m src.diagnostics.system_report
```

---

**Дата создания документации**: $(date)
**Версия проекта**: 0.1.0-dev
**Статус**: В разработке

Эта документация является живым документом и будет обновляться по мере развития проекта.
