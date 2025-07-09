# Примеры использования MCPИСЯ

## Содержание

- [Python SDK](#python-sdk)
- [REST API](#rest-api)
- [MCP Protocol](#mcp-protocol)
- [Интеграции](#интеграции)

## Python SDK

### Базовое использование

```python
from mcpisia import MCPClient

# Инициализация клиента
client = MCPClient(
    base_url="http://localhost:8000",
    token="your-api-token"
)

# Работа с файлами
content = client.filesystem.read_file("/path/to/file.txt")
client.filesystem.write_file("/path/to/output.txt", "Новое содержимое")

# Работа с памятью
client.memory.store("user_session", {"id": 123, "name": "John"})
session = client.memory.retrieve("user_session")
```

### Асинхронное использование

```python
import asyncio
from mcpisia import AsyncMCPClient

async def main():
    async with AsyncMCPClient("http://localhost:8000", "token") as client:
        # Параллельное выполнение операций
        tasks = [
            client.filesystem.read_file(f"/data/file_{i}.txt")
            for i in range(10)
        ]
        contents = await asyncio.gather(*tasks)
        
        # Обработка результатов
        for i, content in enumerate(contents):
            await client.memory.store(f"cache_{i}", content, ttl=3600)

asyncio.run(main())
```

## REST API

### Работа с файловой системой

```bash
# Чтение файла
curl -X GET "http://localhost:8000/api/v1/filesystem/files/example.txt" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Создание файла
curl -X POST "http://localhost:8000/api/v1/filesystem/files/new.txt" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, World!"}'

# Получение списка файлов в директории
curl -X GET "http://localhost:8000/api/v1/filesystem/directories/uploads" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Работа с памятью

```bash
# Сохранение данных
curl -X POST "http://localhost:8000/api/v1/memory/keys/user_123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": {"name": "Alice", "role": "admin"}, "ttl": 7200}'

# Получение данных
curl -X GET "http://localhost:8000/api/v1/memory/keys/user_123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Очистка памяти
curl -X POST "http://localhost:8000/api/v1/memory/clear" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## MCP Protocol

### Прямое использование MCP

```python
import json
from mcpisia.mcp import MCPConnection

# Подключение к MCP серверу
conn = MCPConnection("http://localhost:8000/mcp")

# Вызов инструмента
request = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "call_tool",
    "params": {
        "name": "filesystem_read",
        "arguments": {
            "path": "/data/config.json"
        }
    }
}

response = conn.send(request)
print(response["result"]["content"])
```

### Регистрация собственных инструментов

```python
from mcpisia.mcp import MCPServer, Tool

class CustomTool(Tool):
    name = "custom_processor"
    description = "Обработка пользовательских данных"
    
    def execute(self, data: str) -> dict:
        # Ваша логика обработки
        processed = data.upper()
        return {"result": processed}

# Добавление в сервер
server = MCPServer()
server.register_tool(CustomTool())
```

## Интеграции

### Интеграция с FastAPI

```python
from fastapi import FastAPI, Depends
from mcpisia import MCPClient

app = FastAPI()

def get_mcp_client():
    return MCPClient("http://localhost:8000", "token")

@app.post("/upload-and-store")
async def upload_and_store(
    file_path: str,
    content: str,
    client: MCPClient = Depends(get_mcp_client)
):
    # Сохранение файла
    await client.filesystem.write_file(file_path, content)
    
    # Кэширование в памяти
    await client.memory.store(f"file_cache_{file_path}", content, ttl=3600)
    
    return {"status": "success", "path": file_path}
```

### Интеграция с Django

```python
# settings.py
MCPISIA_CONFIG = {
    'BASE_URL': 'http://localhost:8000',
    'TOKEN': 'your-token',
    'TIMEOUT': 30
}

# services.py
from django.conf import settings
from mcpisia import MCPClient

class FileService:
    def __init__(self):
        config = settings.MCPISIA_CONFIG
        self.client = MCPClient(config['BASE_URL'], config['TOKEN'])
    
    def save_user_file(self, user_id: int, filename: str, content: str):
        path = f"/users/{user_id}/{filename}"
        return self.client.filesystem.write_file(path, content)
    
    def get_user_files(self, user_id: int):
        path = f"/users/{user_id}"
        return self.client.filesystem.list_directory(path)
```

### Интеграция с Celery

```python
from celery import Celery
from mcpisia import MCPClient

app = Celery('tasks')

@app.task
def process_large_file(file_path: str):
    client = MCPClient("http://localhost:8000", "token")
    
    # Чтение большого файла
    content = client.filesystem.read_file(file_path)
    
    # Обработка данных
    processed_content = process_data(content)
    
    # Сохранение результата
    output_path = file_path.replace('.input', '.output')
    client.filesystem.write_file(output_path, processed_content)
    
    # Кэширование результата
    cache_key = f"processed_{file_path}"
    client.memory.store(cache_key, processed_content, ttl=86400)
    
    return {"status": "completed", "output_path": output_path}
```

### Мониторинг и метрики

```python
from prometheus_client import Counter, Histogram
from mcpisia import MCPClient

# Метрики
file_operations = Counter('mcpisia_file_operations_total', 'File operations', ['operation'])
memory_operations = Counter('mcpisia_memory_operations_total', 'Memory operations', ['operation'])
request_duration = Histogram('mcpisia_request_duration_seconds', 'Request duration')

class MonitoredMCPClient:
    def __init__(self, base_url: str, token: str):
        self.client = MCPClient(base_url, token)
    
    def read_file(self, path: str) -> str:
        with request_duration.time():
            file_operations.labels(operation='read').inc()
            return self.client.filesystem.read_file(path)
    
    def store_memory(self, key: str, value: any, ttl: int = None):
        with request_duration.time():
            memory_operations.labels(operation='store').inc()
            return self.client.memory.store(key, value, ttl)
```

### Обработка ошибок

```python
from mcpisia import MCPClient, MCPError, FileNotFoundError, MemoryError

client = MCPClient("http://localhost:8000", "token")

try:
    content = client.filesystem.read_file("/nonexistent/file.txt")
except FileNotFoundError:
    print("Файл не найден")
except MCPError as e:
    print(f"Ошибка MCP: {e.code} - {e.message}")

# Retry логика
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except MCPError as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def robust_file_operation(path: str, content: str):
    return client.filesystem.write_file(path, content)
```

### Пакетные операции

```python
from mcpisia import MCPClient

client = MCPClient("http://localhost:8000", "token")

# Пакетная загрузка файлов
files_to_upload = [
    ("/data/file1.txt", "Содержимое 1"),
    ("/data/file2.txt", "Содержимое 2"),
    ("/data/file3.txt", "Содержимое 3"),
]

# Последовательная загрузка
for path, content in files_to_upload:
    client.filesystem.write_file(path, content)

# Параллельная загрузка
import concurrent.futures

def upload_file(path_content):
    path, content = path_content
    return client.filesystem.write_file(path, content)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(upload_file, pc) for pc in files_to_upload]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]
```

### Кэширование с TTL

```python
import time
from typing import Optional

class CachedMCPClient:
    def __init__(self, base_url: str, token: str):
        self.client = MCPClient(base_url, token)
        self.local_cache = {}
    
    def get_with_cache(self, key: str, ttl: int = 300) -> Optional[any]:
        # Проверка локального кэша
        if key in self.local_cache:
            cached_data, timestamp = self.local_cache[key]
            if time.time() - timestamp < ttl:
                return cached_data
        
        # Получение из удаленной памяти
        try:
            value = self.client.memory.retrieve(key)
            self.local_cache[key] = (value, time.time())
            return value
        except MemoryError:
            return None
    
    def set_with_cache(self, key: str, value: any, ttl: int = 300):
        # Сохранение в удаленную память
        self.client.memory.store(key, value, ttl)
        
        # Обновление локального кэша
        self.local_cache[key] = (value, time.time())
```

---

Эти примеры демонстрируют различные способы использования MCPИСЯ в реальных проектах. Для получения более подробной информации см. [API_REFERENCE.md](API_REFERENCE.md) и [DOCUMENTATION.md](DOCUMENTATION.md).
