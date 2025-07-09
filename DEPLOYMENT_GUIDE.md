# Руководство по развертыванию MCPИСЯ

## Содержание

1. [Требования к среде](#требования-к-среде)
2. [Локальное развертывание](#локальное-развертывание)
3. [Docker развертывание](#docker-развертывание)
4. [Производственное развертывание](#производственное-развертывание)
5. [Мониторинг и логирование](#мониторинг-и-логирование)
6. [Резервное копирование](#резервное-копирование)
7. [Обновление системы](#обновление-системы)

## Требования к среде

### Минимальные требования

- **CPU**: 1 ядро, 2.0 GHz
- **RAM**: 512 MB
- **Диск**: 1 GB свободного места
- **ОС**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows (10+)
- **Python**: 3.8+
- **Git**: 2.25+

### Рекомендуемые требования

- **CPU**: 2+ ядра, 2.5+ GHz
- **RAM**: 2+ GB
- **Диск**: 10+ GB свободного места (SSD предпочтительно)
- **Сеть**: Стабильное соединение для загрузки зависимостей

### Зависимости системы

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl build-essential
```

#### CentOS/RHEL

```bash
sudo yum update
sudo yum install -y python3 python3-pip git curl gcc gcc-c++ make
```

#### macOS

```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка зависимостей
brew install python3 git
```

#### Windows

```powershell
# Установка через Chocolatey
choco install python3 git

# Или загрузите и установите вручную:
# Python: https://www.python.org/downloads/
# Git: https://git-scm.com/downloads
```

## Локальное развертывание

### Быстрый старт

```bash
# 1. Клонирование репозитория
git clone <repository-url> mcpisia
cd mcpisia

# 2. Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Настройка переменных окружения
cp .env.example .env
vim .env  # Отредактируйте настройки

# 5. Инициализация базы данных (если требуется)
python src/init_db.py

# 6. Запуск сервера разработки
python src/server.py
```

### Настройка окружения разработки

#### 1. Установка дополнительных инструментов

```bash
# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Настройка pre-commit hooks
pre-commit install

# Настройка git hooks
./scripts/setup-git-hooks.sh
```

#### 2. Настройка IDE

**VS Code/Cursor (.vscode/settings.json):**

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

**PyCharm:**

1. Откройте проект в PyCharm
2. File → Settings → Project → Python Interpreter
3. Выберите интерпретатор из venv/bin/python
4. Настройте Code Style → Python → Black
5. Включите mypy в Tools → mypy

#### 3. Проверка установки

```bash
# Запуск тестов
pytest

# Проверка стиля кода
black --check src/ tests/
flake8 src/ tests/
mypy src/

# Проверка безопасности
bandit -r src/

# Проверка зависимостей
safety check
```

## Docker развертывание

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя приложения
RUN adduser --disabled-password --gecos '' mcpuser

# Установка рабочей директории
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY config/ ./config/

# Создание директорий для данных
RUN mkdir -p /app/data /app/logs && \
    chown -R mcpuser:mcpuser /app

# Переключение на пользователя приложения
USER mcpuser

# Переменные окружения
ENV PYTHONPATH=/app/src
ENV MCP_DATA_DIR=/app/data
ENV MCP_LOG_DIR=/app/logs

# Порт приложения
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска
CMD ["python", "src/server.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mcpisia:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - MCP_DEBUG=false
      - FS_ROOT_PATH=/app/data/filesystem
      - MEMORY_MAX_SIZE=134217728
    volumes:
      - mcpisia_data:/app/data
      - mcpisia_logs:/app/logs
      - ./config:/app/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - mcpisia_network

  # Nginx для reverse proxy (опционально)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - mcpisia
    restart: unless-stopped
    networks:
      - mcpisia_network

  # Prometheus для мониторинга (опционально)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - mcpisia_network

volumes:
  mcpisia_data:
  mcpisia_logs:
  prometheus_data:

networks:
  mcpisia_network:
    driver: bridge
```

### Запуск через Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f mcpisia

# Остановка
docker-compose down

# Обновление
docker-compose pull
docker-compose up -d --force-recreate
```

## Производственное развертывание

### Подготовка сервера

#### 1. Настройка операционной системы

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y \
    python3 python3-pip python3-venv \
    nginx supervisor \
    git curl wget \
    htop tree \
    fail2ban ufw

# Настройка файрвола
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Настройка fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 2. Создание пользователя приложения

```bash
# Создание пользователя
sudo adduser --system --group --home /opt/mcpisia mcpusia

# Создание SSH ключей для деплоя
sudo -u mcpusia ssh-keygen -t rsa -b 4096 -C "mcpusia@server"
```

#### 3. Подготовка директорий

```bash
# Создание структуры директорий
sudo mkdir -p /opt/mcpisia/{app,data,logs,config}
sudo mkdir -p /var/log/mcpisia
sudo chown -R mcpusia:mcpusia /opt/mcpisia /var/log/mcpisia

# Создание символических ссылок
sudo ln -s /opt/mcpisia/logs /var/log/mcpisia/app
```

### Деплой приложения

#### 1. Клонирование и установка

```bash
# Переключение на пользователя приложения
sudo -u mcpusia -i

# Клонирование репозитория
cd /opt/mcpisia
git clone <repository-url> app
cd app

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install gunicorn  # WSGI сервер для продакшена
```

#### 2. Настройка конфигурации

```bash
# Копирование конфигурации
cp .env.example /opt/mcpisia/config/.env
vim /opt/mcpisia/config/.env
```

**Пример продакшен конфигурации:**

```bash
# /opt/mcpisia/config/.env
MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_DEBUG=false
MCP_SECRET_KEY=your-super-secret-key-here

FS_ROOT_PATH=/opt/mcpisia/data/filesystem
FS_MAX_FILE_SIZE=52428800  # 50MB

MEMORY_MAX_SIZE=268435456  # 256MB
MEMORY_TTL=7200

LOG_LEVEL=INFO
LOG_FILE=/var/log/mcpisia/app.log

SECURITY_SANDBOX_MODE=true
SECURITY_MAX_REQUESTS_PER_MINUTE=200
```

#### 3. Настройка Supervisor

```bash
# /etc/supervisor/conf.d/mcpisia.conf
sudo tee /etc/supervisor/conf.d/mcpisia.conf << EOF
[program:mcpisia]
command=/opt/mcpisia/app/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 src.server:app
directory=/opt/mcpisia/app
user=mcpusia
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/mcpisia/gunicorn.log
environment=PATH="/opt/mcpisia/app/venv/bin",PYTHONPATH="/opt/mcpisia/app/src",ENV_FILE="/opt/mcpisia/config/.env"
EOF

# Обновление конфигурации Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mcpisia
```

#### 4. Настройка Nginx

```nginx
# /etc/nginx/sites-available/mcpisia
server {
    listen 80;
    server_name your-domain.com;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL настройки
    ssl_certificate /etc/ssl/certs/mcpisia.crt;
    ssl_certificate_key /etc/ssl/private/mcpisia.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Безопасность
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Логирование
    access_log /var/log/nginx/mcpisia_access.log;
    error_log /var/log/nginx/mcpisia_error.log;
    
    # Основное проксирование
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Статические файлы (если есть)
    location /static/ {
        alias /opt/mcpisia/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

```bash
# Активация сайта
sudo ln -s /etc/nginx/sites-available/mcpisia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL сертификат (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Мониторинг и логирование

### Настройка логирования

#### 1. Logrotate

```bash
# /etc/logrotate.d/mcpisia
/var/log/mcpisia/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    postrotate
        supervisorctl restart mcpisia
    endscript
}
```

#### 2. Centralized logging с ELK Stack

**Filebeat конфигурация:**

```yaml
# /etc/filebeat/filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/mcpisia/*.log
  fields:
    service: mcpisia
    environment: production
  fields_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "mcpisia-%{+yyyy.MM.dd}"

setup.template.name: "mcpisia"
setup.template.pattern: "mcpisia-*"
```

### Мониторинг системы

#### 1. Prometheus metrics

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Метрики
request_count = Counter('mcpisia_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('mcpisia_request_duration_seconds', 'Request duration')
memory_usage = Gauge('mcpisia_memory_usage_bytes', 'Memory usage')
filesystem_operations = Counter('mcpisia_filesystem_operations_total', 'Filesystem operations', ['operation'])

def get_metrics():
    """Возвращает метрики в формате Prometheus."""
    return generate_latest()
```

#### 2. Health checks

```python
# src/health.py
from typing import Dict, Any
import psutil
import time

class HealthChecker:
    def __init__(self):
        self.start_time = time.time()
    
    def check_health(self) -> Dict[str, Any]:
        """Комплексная проверка здоровья системы."""
        return {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'checks': {
                'filesystem': self._check_filesystem(),
                'memory': self._check_memory(),
                'disk_space': self._check_disk_space(),
                'cpu_usage': self._check_cpu()
            }
        }
    
    def _check_filesystem(self) -> Dict[str, Any]:
        # Проверка доступности файловой системы
        pass
    
    def _check_memory(self) -> Dict[str, Any]:
        # Проверка использования памяти
        pass
```

#### 3. Alerting

**Prometheus Alertmanager rules:**

```yaml
# alerts.yml
groups:
- name: mcpisia
  rules:
  - alert: MCPISIADown
    expr: up{job="mcpisia"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "MCPISIA service is down"
      
  - alert: HighMemoryUsage
    expr: mcpisia_memory_usage_bytes / (256 * 1024 * 1024) > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage in MCPISIA"
      
  - alert: HighErrorRate
    expr: rate(mcpisia_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate in MCPISIA"
```

## Резервное копирование

### Автоматическое резервное копирование

```bash
#!/bin/bash
# /opt/mcpisia/scripts/backup.sh

BACKUP_DIR="/opt/backups/mcpisia"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mcpisia_backup_$DATE"

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Остановка сервиса для консистентности данных
supervisorctl stop mcpisia

# Создание архива данных
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    -C /opt/mcpisia \
    data config app/src

# Запуск сервиса
supervisorctl start mcpisia

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_NAME.tar.gz"
```

### Настройка cron для автоматических бэкапов

```bash
# Ежедневные бэкапы в 2:00
sudo crontab -e
0 2 * * * /opt/mcpisia/scripts/backup.sh

# Еженедельные бэкапы в облако
0 3 * * 0 /opt/mcpisia/scripts/backup_to_cloud.sh
```

### Восстановление из бэкапа

```bash
#!/bin/bash
# /opt/mcpisia/scripts/restore.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1

# Остановка сервиса
supervisorctl stop mcpisia

# Создание бэкапа текущего состояния
/opt/mcpisia/scripts/backup.sh

# Восстановление данных
tar -xzf "$BACKUP_FILE" -C /opt/mcpisia

# Установка правильных прав доступа
chown -R mcpusia:mcpusia /opt/mcpisia/data /opt/mcpisia/config

# Запуск сервиса
supervisorctl start mcpisia

echo "Restore completed from: $BACKUP_FILE"
```

## Обновление системы

### Процедура обновления

#### 1. Подготовка к обновлению

```bash
# Создание бэкапа перед обновлением
/opt/mcpisia/scripts/backup.sh

# Проверка текущей версии
cd /opt/mcpisia/app
git log --oneline -1

# Проверка доступных обновлений
git fetch origin
git log --oneline HEAD..origin/main
```

#### 2. Blue-Green деплоймент

```bash
#!/bin/bash
# /opt/mcpisia/scripts/deploy.sh

# Создание нового окружения
sudo -u mcpusia -i
cd /opt/mcpisia
git clone <repository-url> app_new
cd app_new

# Установка зависимостей в новом окружении
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск тестов
pytest tests/

# Переключение символических ссылок
sudo supervisorctl stop mcpisia
sudo mv /opt/mcpisia/app /opt/mcpisia/app_old
sudo mv /opt/mcpisia/app_new /opt/mcpisia/app
sudo supervisorctl start mcpisia

# Проверка работоспособности
sleep 10
curl -f http://localhost:8000/health

if [ $? -eq 0 ]; then
    echo "Deployment successful"
    rm -rf /opt/mcpisia/app_old
else
    echo "Deployment failed, rolling back"
    sudo supervisorctl stop mcpisia
    sudo mv /opt/mcpisia/app /opt/mcpisia/app_failed
    sudo mv /opt/mcpisia/app_old /opt/mcpisia/app
    sudo supervisorctl start mcpisia
    exit 1
fi
```

#### 3. Rolling update с нулевым даунтаймом

```bash
# Для множественных инстансов за load balancer
for instance in web1 web2 web3; do
    echo "Updating $instance"
    
    # Удаление из load balancer
    curl -X DELETE "http://loadbalancer/api/backends/$instance"
    
    # Ожидание завершения текущих запросов
    sleep 30
    
    # Обновление инстанса
    ssh $instance "/opt/mcpisia/scripts/deploy.sh"
    
    # Проверка здоровья
    if curl -f "http://$instance:8000/health"; then
        # Возвращение в load balancer
        curl -X POST "http://loadbalancer/api/backends/$instance"
        echo "$instance updated successfully"
    else
        echo "Update failed for $instance"
        exit 1
    fi
done
```

### Rollback процедура

```bash
#!/bin/bash
# /opt/mcpisia/scripts/rollback.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <git_commit_hash>"
    exit 1
fi

COMMIT_HASH=$1

# Остановка сервиса
supervisorctl stop mcpisia

# Переход к указанному коммиту
cd /opt/mcpisia/app
git checkout $COMMIT_HASH

# Обновление зависимостей (если необходимо)
source venv/bin/activate
pip install -r requirements.txt

# Запуск сервиса
supervisorctl start mcpisia

# Проверка работоспособности
sleep 10
if curl -f http://localhost:8000/health; then
    echo "Rollback to $COMMIT_HASH successful"
else
    echo "Rollback failed"
    exit 1
fi
```

---

Данное руководство покрывает все основные аспекты развертывания MCPИСЯ от локальной разработки до производственной среды с мониторингом и процедурами обновления.
