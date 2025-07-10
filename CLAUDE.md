# Claude Development Guide for MCPISIA

This file contains important information for Claude when working on the MCPISIA project.

## Project Overview

MCPISIA is an MCP (Model Context Protocol) implementation that combines filesystem and memory components. The project provides:

- **Filesystem Component**: Secure file operations with validation and sandboxing
- **Memory Component**: In-memory storage with TTL support and Redis fallback
- **MCP Server**: Standard MCP-compliant server exposing filesystem and memory tools

## Project Structure

```
MCP-/
├── src/                    # Source code
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── tools.py           # Tool definitions
│   ├── filesystem/        # Filesystem component
│   │   ├── __init__.py
│   │   └── component.py
│   └── memory/            # Memory component
│       ├── __init__.py
│       └── component.py
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── .env.example          # Environment template
└── documentation files
```

## Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use type hints for all functions
- Maintain async/await patterns throughout
- Add docstrings for all public methods

### Security Considerations
- All filesystem operations are sandboxed to the configured base path
- File extensions are validated against allowed list
- File sizes are limited to prevent resource exhaustion
- Memory usage is tracked and limited

### Testing
- Use pytest with async support
- Test both success and error cases
- Mock external dependencies (Redis) for unit tests
- Maintain test coverage above 80%

## Common Tasks

### Running the Server
```bash
python src/server.py
```

### Running Tests
```bash
pytest tests/
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

The server uses environment variables for configuration. See `.env.example` for all available options.

Key settings:
- `FILESYSTEM_BASE_PATH`: Base directory for file operations
- `FILESYSTEM_MAX_FILE_SIZE`: Maximum file size in bytes
- `MEMORY_MAX_SIZE`: Maximum memory usage in bytes
- `REDIS_URL`: Redis connection string (optional)

## Implementation Status

✅ **Completed:**
- Basic project structure
- Core MCP server implementation
- Filesystem component with security
- Memory component with TTL support
- Basic test suite
- Configuration management

🚧 **Future Enhancements:**
- Docker containerization
- Production monitoring
- Advanced caching strategies
- Performance optimizations
- Comprehensive logging

## Claude Agent Efficiency Configuration

### Maximum Performance Settings
- **Инструменты разработки**: pytest, black, flake8, mypy, isort, coverage
- **Языковая поддержка**: Используй русские docstrings и комментарии
- **Фокус безопасности**: Приоритет на валидацию входных данных и sandboxing
- **Покрытие тестами**: Минимум 80% для всех новых компонентов

### MCP Protocol Requirements
- Все tool definitions должны соответствовать MCP specification
- Обязательная валидация schema для входящих запросов
- Proper error codes и human-readable сообщения
- Async/await паттерны для всех I/O операций

### Security & Performance Guidelines
- **Filesystem operations**: 
  - Обязательный sandboxing к FILESYSTEM_BASE_PATH
  - Валидация расширений файлов
  - Ограничение размера файлов (FILESYSTEM_MAX_FILE_SIZE)
- **Memory operations**:
  - TTL управление для предотвращения memory leaks
  - Redis fallback для persistence
  - Мониторинг MEMORY_MAX_SIZE

### Development Workflow
- **Commits**: Используй conventional commits на русском языке
- **Testing**: Обязательное покрытие edge cases и error scenarios
- **Documentation**: Все публичные API документируются на русском
- **Code Style**: Строгое соблюдение PEP 8 + type hints

## Notes for Claude

- The project follows the MCP specification for tool definitions and server behavior
- Error handling should be comprehensive but user-friendly
- Always validate inputs and sanitize paths
- Prefer composition over inheritance in component design
- Keep the codebase modular and testable
- Use Russian language for user-facing documentation and comments
- Focus on defensive programming and security-first approach