#!/usr/bin/env python3
"""
Главный файл запуска GitHub Agent Orchestrator
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в PATH
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import GitHubAgentOrchestrator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("orchestrator.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    # Загружаем конфигурацию из переменных окружения
    github_token = os.getenv("GITHUB_TOKEN")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    repo_name = os.getenv("GITHUB_REPO")  # Формат: "owner/repo"

    if not all([github_token, repo_name]):
        logger.error(
            "Необходимо установить переменные окружения: GITHUB_TOKEN, GITHUB_REPO"
        )
        logger.info("Пример:")
        logger.info("  export GITHUB_TOKEN=your_github_token")
        logger.info("  export GITHUB_REPO=owner/repo_name")
        logger.info("  export ANTHROPIC_API_KEY=your_anthropic_key  # опционально")
        return

    # Создаем и запускаем оркестратор
    orchestrator = GitHubAgentOrchestrator(
        github_token=github_token,
        repo_name=repo_name,
        anthropic_api_key=anthropic_api_key,
    )

    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
