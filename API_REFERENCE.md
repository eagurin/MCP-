# API Справочник MCPИСЯ

## Обзор API

MCPИСЯ предоставляет REST API для взаимодействия с компонентами файловой системы и памяти через протокол MCP.

## Базовый URL

```
http://localhost:8000/api/v1
```

## Аутентификация

API использует токен-базированную аутентификацию:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Файловая система

#### GET /filesystem/files/{path}

Получение содержимого файла.

**Параметры:**

- `path` (string, path): Путь к файлу

**Ответ:**

```json
{
  "success": true,
  "data": {
    "content": "содержимое файла",
    "size": 1024,
    "modified": "2024-01-01T12:00:00Z",
    "encoding": "utf-8"
  }
}
```

#### POST /filesystem/files/{path}

Создание или обновление файла.

**Параметры:**

- `path` (string, path): Путь к файлу

**Тело запроса:**

```json
{
  "content": "новое содержимое",
  "encoding": "utf-8"
}
```

**Ответ:**

```json
{
  "success": true,
  "data": {
    "path": "/path/to/file.txt",
    "size": 1024,
    "created": true
  }
}
```

#### DELETE /filesystem/files/{path}

Удаление файла.

**Параметры:**

- `path` (string, path): Путь к файлу

**Ответ:**

```json
{
  "success": true,
  "message": "Файл успешно удален"
}
```

#### GET /filesystem/directories/{path}

Получение содержимого директории.

**Параметры:**

- `path` (string, path): Путь к директории
- `recursive` (boolean, query): Рекурсивный обход (по умолчанию: false)

**Ответ:**

```json
{
  "success": true,
  "data": {
    "path": "/path/to/directory",
    "items": [
      {
        "name": "file.txt",
        "type": "file",
        "size": 1024,
        "modified": "2024-01-01T12:00:00Z"
      },
      {
        "name": "subdirectory",
        "type": "directory",
        "items_count": 5,
        "modified": "2024-01-01T12:00:00Z"
      }
    ]
  }
}
```

### Память

#### GET /memory/keys

Получение списка всех ключей в памяти.

**Ответ:**

```json
{
  "success": true,
  "data": {
    "keys": ["key1", "key2", "key3"],
    "total_count": 3
  }
}
```

#### GET /memory/keys/{key}

Получение значения по ключу.

**Параметры:**

- `key` (string, path): Ключ для получения

**Ответ:**

```json
{
  "success": true,
  "data": {
    "key": "example_key",
    "value": "example_value",
    "type": "string",
    "created": "2024-01-01T12:00:00Z",
    "ttl": 3600
  }
}
```

#### POST /memory/keys/{key}

Сохранение значения по ключу.

**Параметры:**

- `key` (string, path): Ключ для сохранения

**Тело запроса:**

```json
{
  "value": "значение для сохранения",
  "ttl": 3600
}
```

**Ответ:**

```json
{
  "success": true,
  "data": {
    "key": "example_key",
    "stored": true,
    "ttl": 3600
  }
}
```

#### DELETE /memory/keys/{key}

Удаление значения по ключу.

**Параметры:**

- `key` (string, path): Ключ для удаления

**Ответ:**

```json
{
  "success": true,
  "message": "Ключ успешно удален"
}
```

#### POST /memory/clear

Очистка всей памяти.

**Ответ:**

```json
{
  "success": true,
  "message": "Память очищена",
  "cleared_keys_count": 15
}
```

### Система

#### GET /system/health

Проверка состояния системы.

**Ответ:**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "uptime": 3600,
    "version": "0.1.0",
    "components": {
      "filesystem": {
        "status": "ok",
        "root_path": "/tmp/mcpisia",
        "available_space": 1073741824
      },
      "memory": {
        "status": "ok",
        "used_memory": 67108864,
        "max_memory": 134217728,
        "keys_count": 42
      }
    }
  }
}
```

#### GET /system/stats

Получение статистики системы.

**Ответ:**

```json
{
  "success": true,
  "data": {
    "requests_total": 1000,
    "requests_per_minute": 25,
    "filesystem_operations": 500,
    "memory_operations": 500,
    "errors_count": 5,
    "average_response_time": 0.125
  }
}
```

## MCP Tools

### filesystem_read

**Описание**: Чтение содержимого файла

**Схема:**

```json
{
  "name": "filesystem_read",
  "description": "Чтение содержимого файла",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Путь к файлу для чтения"
      }
    },
    "required": ["path"]
  }
}
```

**Пример использования:**

```json
{
  "method": "call_tool",
  "params": {
    "name": "filesystem_read",
    "arguments": {
      "path": "/path/to/file.txt"
    }
  }
}
```

### filesystem_write

**Описание**: Запись содержимого в файл

**Схема:**

```json
{
  "name": "filesystem_write",
  "description": "Запись содержимого в файл",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Путь к файлу для записи"
      },
      "content": {
        "type": "string",
        "description": "Содержимое для записи"
      }
    },
    "required": ["path", "content"]
  }
}
```

### memory_store

**Описание**: Сохранение данных в памяти

**Схема:**

```json
{
  "name": "memory_store",
  "description": "Сохранение данных в памяти",
  "inputSchema": {
    "type": "object",
    "properties": {
      "key": {
        "type": "string",
        "description": "Ключ для сохранения"
      },
      "value": {
        "description": "Значение для сохранения"
      },
      "ttl": {
        "type": "integer",
        "description": "Время жизни в секундах (опционально)",
        "default": 3600
      }
    },
    "required": ["key", "value"]
  }
}
```

### memory_retrieve

**Описание**: Получение данных из памяти

**Схема:**

```json
{
  "name": "memory_retrieve",
  "description": "Получение данных из памяти",
  "inputSchema": {
    "type": "object",
    "properties": {
      "key": {
        "type": "string",
        "description": "Ключ для получения"
      }
    },
    "required": ["key"]
  }
}
```

## Коды ошибок

### HTTP Status Codes

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс успешно создан
- `400 Bad Request` - Некорректный запрос
- `401 Unauthorized` - Отсутствует аутентификация
- `403 Forbidden` - Недостаточно прав доступа
- `404 Not Found` - Ресурс не найден
- `409 Conflict` - Конфликт при создании ресурса
- `413 Payload Too Large` - Слишком большой размер файла
- `422 Unprocessable Entity` - Ошибка валидации
- `429 Too Many Requests` - Превышен лимит запросов
- `500 Internal Server Error` - Внутренняя ошибка сервера

### Коды ошибок приложения

- `FS001` - Файл не найден
- `FS002` - Недопустимый путь
- `FS003` - Недостаточно прав доступа к файлу
- `FS004` - Превышен максимальный размер файла
- `FS005` - Недопустимое расширение файла

- `MEM001` - Ключ не найден в памяти
- `MEM002` - Превышен лимит памяти
- `MEM003` - Недопустимый ключ
- `MEM004` - Срок действия ключа истек

- `SYS001` - Общая системная ошибка
- `SYS002` - Превышен лимит запросов
- `SYS003` - Сервис временно недоступен

### Формат ошибки

```json
{
  "success": false,
  "error": {
    "code": "FS001",
    "message": "Файл не найден",
    "details": {
      "path": "/path/to/nonexistent/file.txt"
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Rate Limiting

API использует ограничение скорости запросов:

- **Лимит**: 100 запросов в минуту на IP-адрес
- **Заголовки ответа**:
  - `X-RateLimit-Limit`: Максимальное количество запросов
  - `X-RateLimit-Remaining`: Оставшиеся запросы
  - `X-RateLimit-Reset`: Время сброса лимита (Unix timestamp)

При превышении лимита возвращается код 429 с сообщением:

```json
{
  "success": false,
  "error": {
    "code": "SYS002",
    "message": "Превышен лимит запросов",
    "details": {
      "limit": 100,
      "reset_time": "2024-01-01T12:01:00Z"
    }
  }
}
```

## Примеры использования

### Python Client

```python
import requests
import json

class MCPClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def read_file(self, path: str) -> str:
        """Чтение файла через API."""
        response = requests.get(
            f"{self.base_url}/filesystem/files/{path}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()['data']['content']
    
    def write_file(self, path: str, content: str) -> bool:
        """Запись файла через API."""
        data = {'content': content}
        response = requests.post(
            f"{self.base_url}/filesystem/files/{path}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()['success']

# Использование
client = MCPClient('http://localhost:8000/api/v1', 'your-token')
content = client.read_file('/path/to/file.txt')
client.write_file('/path/to/new_file.txt', 'Новое содержимое')
```

### JavaScript Client

```javascript
class MCPClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async readFile(path) {
        const response = await fetch(
            `${this.baseUrl}/filesystem/files/${path}`,
            { headers: this.headers }
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.data.content;
    }

    async writeFile(path, content) {
        const response = await fetch(
            `${this.baseUrl}/filesystem/files/${path}`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({ content })
            }
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.success;
    }
}

// Использование
const client = new MCPClient('http://localhost:8000/api/v1', 'your-token');
const content = await client.readFile('/path/to/file.txt');
await client.writeFile('/path/to/new_file.txt', 'Новое содержимое');
```

## Версионирование API

API использует семантическое версионирование:

- **Мажорная версия**: Несовместимые изменения
- **Минорная версия**: Обратно совместимые новые функции
- **Патч версия**: Обратно совместимые исправления

Текущая версия: **v1.0.0**

Поддерживаемые версии API:

- `/api/v1` - Текущая стабильная версия
- `/api/v1beta` - Бета-версия с новыми функциями
