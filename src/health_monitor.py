"""
Мониторинг здоровья агентов
"""

import logging
from datetime import datetime, timedelta
from typing import List

from src.agents import ClaudeAgentManager
from src.models import Agent, AgentStatus

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Монитор работоспособности агентов"""

    def __init__(self, check_interval: int = 300):  # 5 минут
        self.check_interval = check_interval
        self.last_check = datetime.now()
        self.running = False

    async def start(self):
        """Запуск мониторинга"""
        self.running = True
        logger.info("🔍 Запуск HealthMonitor")

    async def stop(self):
        """Остановка мониторинга"""
        self.running = False
        logger.info("⏹️ Остановка HealthMonitor")

    async def is_agent_healthy(
        self, agent: Agent, claude_manager: ClaudeAgentManager
    ) -> bool:
        """Проверка работоспособности агента"""
        now = datetime.now()

        # Агент считается неработающим если:
        # 1. Превышено максимальное количество ошибок
        # 2. Нет heartbeat более 10 минут
        # 3. Статус ERROR
        # 4. Claude Squad сессия неактивна (если используется)

        if agent.error_count >= agent.max_errors:
            return False

        if now - agent.last_heartbeat > timedelta(minutes=10):
            return False

        if agent.status == AgentStatus.ERROR:
            return False

        # Проверяем статус Claude Squad сессии
        if agent.squad_session_active:
            session_status = await claude_manager.squad_manager.check_session_status(
                agent.id
            )
            if session_status not in ["active"]:
                logger.warning(
                    f"Агент {agent.id}: Claude Squad сессия не активна ({session_status})"
                )
                return False

        return True

    async def get_unhealthy_agents(
        self, agents: List[Agent], claude_manager: ClaudeAgentManager
    ) -> List[Agent]:
        """Получение списка неработающих агентов"""
        unhealthy_agents = []
        for agent in agents:
            if not await self.is_agent_healthy(agent, claude_manager):
                unhealthy_agents.append(agent)
        return unhealthy_agents
