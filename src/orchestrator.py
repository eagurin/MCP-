#!/usr/bin/env python3
"""
GitHub Agent Orchestrator - Основной класс оркестратора
"""

import asyncio
import logging
from typing import Optional

from src.agents import ClaudeSquadManager
from src.github_manager import GitHubManager  
from src.health_monitor import HealthMonitor
from src.models import Agent, Task

logger = logging.getLogger(__name__)


class GitHubAgentOrchestrator:
    """Основной класс оркестратора GitHub агентов"""
    
    def __init__(
        self,
        github_token: str,
        repo_name: str,
        anthropic_api_key: Optional[str] = None,
        check_interval: int = 300,
    ):
        """
        Инициализация оркестратора
        
        Args:
            github_token: GitHub токен для доступа к API
            repo_name: Имя репозитория в формате "owner/repo"
            anthropic_api_key: API ключ Anthropic (опционально)
            check_interval: Интервал проверки в секундах
        """
        self.github_token = github_token
        self.repo_name = repo_name
        self.anthropic_api_key = anthropic_api_key
        self.check_interval = check_interval
        
        # Компоненты системы
        self.github_manager = GitHubManager(github_token, repo_name)
        self.claude_manager = ClaudeSquadManager()
        self.health_monitor = HealthMonitor()
        
        # Состояние
        self.running = False
        self.agents = {}
        
    async def start(self):
        """Запуск оркестратора"""
        logger.info("🚀 Запуск GitHub Agent Orchestrator")
        logger.info(f"📁 Репозиторий: {self.repo_name}")
        logger.info(f"⏰ Интервал проверки: {self.check_interval}с")
        
        self.running = True
        
        # Запускаем основной цикл
        await asyncio.gather(
            self._main_loop(),
            self.health_monitor.start(),
            return_exceptions=True
        )
        
    async def stop(self):
        """Остановка оркестратора"""
        logger.info("⏹️ Остановка оркестратора")
        self.running = False
        
        # Останавливаем все агенты
        for agent_id, agent in self.agents.items():
            logger.info(f"🛑 Остановка агента {agent_id}")
            await self.claude_manager.stop_agent(agent_id)
            
        await self.health_monitor.stop()
        
    async def _main_loop(self):
        """Основной цикл оркестратора"""
        while self.running:
            try:
                # Получаем открытые issues
                tasks = await self.github_manager.get_open_issues()
                logger.info(f"📋 Найдено {len(tasks)} открытых задач")
                
                # Обрабатываем каждую задачу
                for task in tasks:
                    await self._process_task(task)
                    
                # Ждем до следующей проверки
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                await asyncio.sleep(60)  # Короткая пауза при ошибке
                
    async def _process_task(self, task: Task):
        """Обработка отдельной задачи - только мониторинг"""
        agent_id = f"agent_{task.id}"
        
        # Проверяем есть ли уже агент для этой задачи
        if agent_id in self.agents:
            logger.debug(f"🤖 Агент {agent_id} мониторится для задачи #{task.id}")
            # Здесь можно добавить проверку здоровья агента
            return
            
        # Просто логируем что задача без агента
        logger.debug(f"📋 Задача #{task.id} доступна для назначения: {task.title}")
    
    async def assign_agent_to_task(self, task_id: int) -> bool:
        """Назначение агента на задачу по запросу из CLI"""
        # Получаем задачу
        tasks = await self.github_manager.get_open_issues()
        task = next((t for t in tasks if t.id == task_id), None)
        
        if not task:
            logger.error(f"❌ Задача #{task_id} не найдена")
            return False
            
        agent_id = f"agent_{task.id}"
        
        # Проверяем нет ли уже агента
        if agent_id in self.agents:
            logger.warning(f"⚠️ Агент {agent_id} уже назначен на задачу #{task.id}")
            return False
        
        logger.info(f"👥 Создание агента {agent_id} для задачи #{task.id}: {task.title}")
        
        try:
            # Создаем НАСТОЯЩИЙ Claude Squad процесс
            success = await self._create_real_claude_squad_agent(task, agent_id)
            
            if success:
                self.agents[agent_id] = {
                    "task_id": task.id,
                    "task_title": task.title,
                    "status": "working",
                    "created_at": asyncio.get_event_loop().time()
                }
                logger.info(f"✅ Агент {agent_id} успешно создан и работает")
                
                # Создаем комментарий в GitHub
                comment = f"🤖 Агент {agent_id} назначен на задачу и начал работу.\n\n🔄 Статус: Анализирую требования..."
                await self.github_manager.create_comment(task.id, comment)
                return True
            else:
                logger.warning(f"⚠️ Не удалось создать агента для задачи #{task.id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания агента для задачи #{task.id}: {e}")
            return False
    
    async def remove_agent_from_task(self, task_id: int) -> bool:
        """Удаление агента с задачи"""
        agent_id = f"agent_{task_id}"
        
        if agent_id not in self.agents:
            logger.error(f"❌ Агент для задачи #{task_id} не найден")
            return False
            
        agent_info = self.agents[agent_id]
        
        # Завершаем процесс Claude Squad если он есть
        if "process" in agent_info:
            process = agent_info["process"]
            try:
                process.terminate()
                await process.wait()
                logger.info(f"🛑 Процесс агента {agent_id} завершен")
            except Exception as e:
                logger.error(f"❌ Ошибка завершения процесса: {e}")
        
        # Удаляем временный файл если есть
        if "prompt_file" in agent_info:
            try:
                os.unlink(agent_info["prompt_file"])
            except:
                pass
                
        # Удаляем агента из списка
        del self.agents[agent_id]
        
        # Комментарий в GitHub
        comment = f"🛑 Агент {agent_id} снят с задачи"
        await self.github_manager.create_comment(task_id, comment)
        
        logger.info(f"✅ Агент {agent_id} удален с задачи #{task_id}")
        return True
            
    async def _create_real_claude_squad_agent(self, task: Task, agent_id: str) -> bool:
        """Создание НАСТОЯЩЕГО Claude Squad агента"""
        import subprocess
        import tempfile
        import os
        
        try:
            # Создаем временный файл с промптом
            prompt = f"""Ты - специализированный GitHub агент разработки (ID: {agent_id}).

ЗАДАЧА #{task.id}: {task.title}

ОПИСАНИЕ:
{task.body}

МЕТКИ: {', '.join(task.labels)}
URL: {task.url}

ТВОЯ РОЛЬ:
1. Проанализируй требования задачи детально
2. Создай план реализации 
3. Начни выполнение - изучи код репозитория
4. Реализуй необходимые изменения
5. Протестируй решение
6. Создай pull request
7. Обновляй статус в GitHub комментариями каждые 30 минут

ВАЖНЫЕ ПРАВИЛА:
- Работай автономно и систематически
- Используй существующий стиль кода
- Тестируй все изменения
- Документируй сложные решения
- Сообщай о проблемах в комментариях GitHub

НАЧНИ РАБОТУ:
Сначала изучи структуру репозитория и создай план выполнения задачи. 
Отправь первый статус-комментарий в GitHub issue.
"""
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Запускаем Claude Squad с промптом
            cmd = [
                'cs', 
                '--program', 
                f'claude --prompt-file {prompt_file}',
                '--autoyes'
            ]
            
            logger.info(f"🚀 Запуск Claude Squad: {' '.join(cmd)}")
            
            # Запускаем процесс в фоне
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Сохраняем процесс для контроля
            self.agents[agent_id] = {
                "process": process,
                "prompt_file": prompt_file,
                "task_id": task.id,
                "status": "starting"
            }
            
            logger.info(f"✅ Claude Squad процесс запущен для {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Claude Squad: {e}")
            return False