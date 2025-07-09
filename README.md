# MCPИСЯ - MCP Implementation

> **MCPИСЯ** = filesystem + memory

Реализация Model Context Protocol (MCP), объединяющая возможности файловой системы и управления памятью в единой системе.

## 🚀 Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url> mcpisia
cd mcpisia

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python src/server.py
```

## 📋 Содержание

- [О проекте](#о-проекте)
- [Функциональность](#функциональность)
- [Архитектура](#архитектура)
- [Установка](#установка)
- [Использование](#использование)
- [Документация](#документация)
- [Разработка](#разработка)
- [Лицензия](#лицензия)

## 🎯 О проекте

**MCPИСЯ** - это современная реализация MCP (Model Context Protocol), которая предоставляет:

- 📁 **Безопасную работу с файловой системой**
- 🧠 **Эффективное управление памятью**
- 🔧 **MCP-совместимые инструменты**
- 🛡️ **Встроенную систему безопасности**
- 📊 **Мониторинг и метрики**

### Ключевые особенности

- ✅ Полная поддержка спецификации MCP
- ✅ Модульная архитектура
- ✅ Типизация с Python type hints
- ✅ Комплексная система тестирования
- ✅ Docker поддержка
- ✅ Готовность к продакшену

## ⚡ Функциональность

### Компонент файловой системы

- Чтение и запись файлов
- Создание и управление директориями
- Валидация путей и безопасность
- Ограничения по размеру и типу файлов

### Компонент памяти

- Хранение данных в памяти с TTL
- Кэширование с различными стратегиями
- Управление состоянием приложения
- Метрики использования памяти

### MCP инструменты

- `filesystem_read` - чтение файлов
- `filesystem_write` - запись файлов
- `memory_store` - сохранение в памяти
- `memory_retrieve` - получение из памяти

## 🏗️ Архитектура

```
MCPИСЯ
├── 📁 Filesystem Component
│   ├── File Operations
│   ├── Security Layer
│   └── Path Validation
├── 🧠 Memory Component
│   ├── State Management
│   ├── Caching System
│   └── TTL Management
└── 🔌 MCP Server
    ├── Tool Registry
    ├── Request Handler
    └── Response Formatter
```

## 📦 Установка

### Системные требования

- Python 3.8+
- Git
- 512MB RAM (минимум)
- 1GB свободного места

### Локальная установка

```bash
# 1. Клонирование
git clone <repository-url> mcpisia
cd mcpisia

# 2. Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Зависимости
pip install -r requirements.txt

# 4. Настройка
cp .env.example .env
vim .env

# 5. Запуск
python src/server.py
```

### Docker установка

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f mcpisia
```

## 🛠️ Использование

### API примеры

#### Чтение файла

```bash
curl -X GET "http://localhost:8000/api/v1/filesystem/files/example.txt" \
  -H "Authorization: Bearer your-token"
```

#### Запись файла

```bash
curl -X POST "http://localhost:8000/api/v1/filesystem/files/new_file.txt" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"content": "Содержимое файла"}'
```

#### Сохранение в памяти

```bash
curl -X POST "http://localhost:8000/api/v1/memory/keys/my_key" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"value": "значение", "ttl": 3600}'
```

### Python клиент

```python
from mcpisia_client import MCPClient

client = MCPClient('http://localhost:8000/api/v1', 'your-token')

# Работа с файлами
content = client.read_file('/path/to/file.txt')
client.write_file('/path/to/new_file.txt', 'Новое содержимое')

# Работа с памятью
client.store_memory('key', 'value', ttl=3600)
value = client.retrieve_memory('key')
```

## 📚 Документация

- [**DOCUMENTATION.md**](DOCUMENTATION.md) - Полная документация проекта
- [**API_REFERENCE.md**](API_REFERENCE.md) - Справочник по API
- [**DEPLOYMENT_GUIDE.md**](DEPLOYMENT_GUIDE.md) - Руководство по развертыванию
- [**CLAUDE.md**](CLAUDE.md) - Руководство для разработки с Claude

### Структура проекта

```
MCP-/
├── src/                    # Исходный код
│   ├── filesystem/         # Компоненты файловой системы
│   ├── memory/            # Компоненты памяти
│   ├── server.py          # MCP сервер
│   └── tools.py           # Определения инструментов
├── tests/                 # Тесты
├── config/                # Конфигурация
├── docs/                  # Документация
├── requirements.txt       # Зависимости
└── pyproject.toml        # Настройки проекта
```

## 🔧 Разработка

### Настройка окружения разработки

```bash
# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Настройка pre-commit hooks
pre-commit install

# Проверка кода
black src/ tests/
flake8 src/ tests/
mypy src/

# Запуск тестов
pytest --cov=src
```

### Стандарты кодирования

- **Стиль**: PEP 8 + Black formatter
- **Типизация**: Обязательные type hints
- **Тестирование**: Покрытие минимум 80%
- **Документация**: Docstrings для всех публичных API

### Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 🚀 Производственное развертывание

### Быстрое развертывание с Docker

```bash
# Клонирование
git clone <repository-url> mcpisia
cd mcpisia

# Настройка окружения
cp .env.example .env
vim .env  # Настройте продакшен параметры

# Запуск
docker-compose -f docker-compose.prod.yml up -d
```

### Ручное развертывание

Подробные инструкции см. в [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 📊 Мониторинг

Система включает встроенный мониторинг:

- **Health checks**: `/health` endpoint
- **Метрики**: Prometheus-совместимые метрики
- **Логирование**: Структурированные логи
- **Алерты**: Настраиваемые уведомления

## 🛡️ Безопасность

- **Sandbox режим**: Изоляция файловых операций
- **Валидация**: Проверка всех входных данных
- **Rate limiting**: Ограничение скорости запросов
- **Аудит**: Логирование всех операций

## 🐛 Устранение неполадок

### Частые проблемы

1. **Ошибка импорта модулей**

   ```bash
   pip install -e .
   ```

2. **Проблемы с правами доступа**

   ```bash
   chmod 755 /path/to/directory
   ```

3. **Превышение лимита памяти**

   ```bash
   # Увеличьте MEMORY_MAX_SIZE в .env
   MEMORY_MAX_SIZE=268435456
   ```

## 📄 Лицензия

Проект распространяется под лицензией [GNU General Public License v2.0](LICENSE).

```
MCPИСЯ - MCP implementation combining filesystem and memory components
Copyright (C) 2024 MCP Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
```

## 📞 Поддержка

- 📧 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **Документация**: [docs/](docs/)
- 🤝 **Сообщество**: [Discussions](https://github.com/your-repo/discussions)

---

**Статус проекта**: 🚧 В разработке  
**Версия**: 0.1.0-dev  
**Последнее обновление**: $(date)

<div align="center">

**[⬆ Наверх](#mcpися---mcp-implementation)**

</div>
