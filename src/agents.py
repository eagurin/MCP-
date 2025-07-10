"""
Управление агентами Claude и Claude Squad
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, Optional

import anthropic

from src.models import Agent, AgentStatus, Task

# Попытка импорта Claude Code SDK
try:
    from claude_code_sdk import query, ClaudeCodeOptions
    CLAUDE_CODE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_CODE_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)


class ClaudeSquadManager:
    """Менеджер для работы с Claude Squad v1.0.8+"""

    def __init__(self):
        self.squad_available = self._check_claude_squad_availability()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.daemon_started = False

        if self.squad_available:
            logger.info("Claude Squad v1.0.8+ доступен")
            # Новая версия работает через daemon и tmux, 
            # поэтому используем прямое API взаимодействие
            logger.info("Используется прямое API взаимодействие с Claude")
        else:
            logger.warning(
                "Claude Squad не найден - агенты будут работать через прямое API"
            )

    def _check_claude_squad_availability(self) -> bool:
        """Проверка доступности Claude Squad"""
        try:
            result = subprocess.run(["cs", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"Найден Claude Squad: {version_info}")
                return True
            return False
        except Exception:
            return False

    async def create_squad_session(self, task: Task, agent_id: str) -> bool:
        """Создание логической сессии для задачи (совместимость с v1.0.8+)"""
        if not self.squad_available:
            return False

        try:
            # В новой версии Claude Squad мы создаем логическую сессию
            # но не используем физические tmux сессии для автоматизации
            session_name = f"github-task-{task.id}"
            
            self.active_sessions[agent_id] = {
                "session_name": session_name,
                "task_id": task.id,
                "created_at": datetime.now(),
                "status": "active",
                "prompt": self._generate_squad_prompt(task, agent_id),
                "squad_version": "1.0.8+",
            }
            
            logger.info(
                f"Создана логическая Claude Squad сессия {session_name} для задачи #{task.id}"
            )
            logger.info(f"Сессия готова для интерактивной работы через 'cs' command")
            return True

        except Exception as e:
            logger.error(f"Исключение при создании Claude Squad сессии: {e}")
            return False

    def _generate_squad_prompt(self, task: Task, agent_id: str) -> str:
        """Генерация промпта для Claude Squad"""
        return f"""Ты - специализированный агент разработки GitHub (ID: {agent_id}).

ЗАДАЧА: {task.title}

ОПИСАНИЕ:
{task.body}

МЕТКИ: {', '.join(task.labels)}
URL: {task.url}

ТВОЯ РОЛЬ:
1. Проанализируй требования задачи
2. Создай детальный план реализации
3. Реализуй необходимые изменения в коде
4. Протестируй решение
5. Создай pull request
6. Обновляй статус задачи комментариями

ВАЖНЫЕ ПРАВИЛА:
- Работай автономно, но систематически
- Используй существующие паттерны и стиль кода
- Всегда тестируй изменения перед commit
- Документируй сложные решения
- Сообщай о блокерах и проблемах

ОТЧЕТНОСТЬ:
- Оставляй комментарии в GitHub issue о прогрессе
- Используй эмодзи для статусов: 🔄 работа, ✅ готово, ❌ проблема
- Обновляй статус каждые 30 минут работы

Начни с анализа задачи и создания плана выполнения."""

    async def check_session_status(self, agent_id: str) -> str:
        """Проверка статуса логической сессии"""
        if agent_id not in self.active_sessions:
            return "not_found"

        session_info = self.active_sessions[agent_id]
        
        try:
            # Проверяем что логическая сессия активна
            if session_info.get("status") == "active":
                # В новой версии Claude Squad сессии управляются интерактивно
                # Поэтому считаем сессию активной если она в нашем списке
                return "active"
            else:
                return "inactive"

        except Exception as e:
            logger.error(f"Ошибка проверки статуса сессии {agent_id}: {e}")
            return "error"

    async def restart_session(self, agent_id: str, task: Task) -> bool:
        """Перезапуск сессии агента"""
        if agent_id in self.active_sessions:
            await self.terminate_session(agent_id)

        return await self.create_squad_session(task, agent_id)

    async def terminate_session(self, agent_id: str) -> bool:
        """Завершение логической сессии"""
        if agent_id not in self.active_sessions:
            return True

        session_info = self.active_sessions[agent_id]
        session_name = session_info["session_name"]

        try:
            # Помечаем логическую сессию как завершенную
            del self.active_sessions[agent_id]
            logger.info(f"Логическая сессия {session_name} завершена")
            logger.info(f"Для интерактивного завершения используйте: cs reset")
            return True

        except Exception as e:
            logger.error(f"Исключение при завершении сессии {agent_id}: {e}")
            return False

    async def send_message_to_session(self, agent_id: str, message: str) -> bool:
        """Логирование сообщения для интерактивной сессии"""
        if agent_id not in self.active_sessions:
            return False

        session_info = self.active_sessions[agent_id]
        session_name = session_info["session_name"]

        try:
            # В новой версии Claude Squad сообщения отправляются интерактивно
            # Поэтому просто логируем сообщение для дальнейшего использования
            logger.info(f"Сообщение для сессии {session_name}: {message[:100]}...")
            logger.info(f"Для интерактивной отправки используйте: cs")
            return True

        except Exception as e:
            logger.error(f"Ошибка подготовки сообщения для сессии {agent_id}: {e}")
            return False

    def get_session_prompt(self, agent_id: str) -> Optional[str]:
        """Получение промпта для интерактивной работы"""
        if agent_id not in self.active_sessions:
            return None
        
        session_info = self.active_sessions[agent_id]
        return session_info.get("prompt")

    def list_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Получение списка активных логических сессий"""
        return self.active_sessions.copy()


class ClaudeAgentManager:
    """Менеджер для работы с Claude агентами"""

    def __init__(self, api_key: Optional[str] = None):
        self.anthropic_api_key = api_key
        self.claude_client = None
        self.enabled = False
        self.connection_type = "none"
        self.squad_manager = ClaudeSquadManager()

        # Проверяем различные способы подключения к Claude
        if CLAUDE_CODE_SDK_AVAILABLE:
            try:
                # Тестируем подключение через Claude Code SDK
                self.enabled = True
                self.connection_type = "claude_code_sdk"
                logger.info("Claude подключен через Claude Code SDK")
            except Exception as e:
                logger.debug(f"Claude Code SDK тест не удался: {e}")
        
        if not self.enabled:
            try:
                # Пытаемся подключиться через стандартный Anthropic API
                if api_key:
                    self.claude_client = anthropic.Anthropic(api_key=api_key)
                    self.enabled = True
                    self.connection_type = "anthropic_api"
                    logger.info("Claude подключен через Anthropic API")
                else:
                    self.claude_client = anthropic.Anthropic()
                    self.enabled = True
                    self.connection_type = "claude_code"
                    logger.info("Claude подключен через Claude Code")
            except Exception as e:
                logger.debug(f"Подключение через Anthropic API не удалось: {e}")

                # Fallback на специальные провайдеры
                if os.getenv("CLAUDE_CODE_USE_BEDROCK") == "1":
                    # Подключение через Amazon Bedrock
                    try:
                        self.claude_client = anthropic.Anthropic()
                        self.enabled = True
                        self.connection_type = "bedrock"
                        logger.info("Claude подключен через Amazon Bedrock")
                    except Exception as e:
                        logger.warning(f"Не удалось подключиться через Bedrock: {e}")
                elif os.getenv("CLAUDE_CODE_USE_VERTEX") == "1":
                    # Подключение через Google Vertex AI
                    try:
                        self.claude_client = anthropic.Anthropic()
                        self.enabled = True
                        self.connection_type = "vertex_ai"
                        logger.info("Claude подключен через Google Vertex AI")
                    except Exception as e:
                        logger.warning(f"Не удалось подключиться через Vertex AI: {e}")

            if not self.enabled:
                logger.info(
                    "Claude недоступен - используется Claude Squad для управления агентами"
                )
                logger.info("Доступные способы подключения:")
                logger.info("  1. Claude Code SDK (pip install claude-code-sdk)")
                logger.info("  2. Claude Code CLI (стандартный)")
                logger.info("  3. ANTHROPIC_API_KEY=your_key")
                logger.info(
                    "  4. CLAUDE_CODE_USE_BEDROCK=1 (с настройкой AWS credentials)"
                )
                logger.info(
                    "  5. CLAUDE_CODE_USE_VERTEX=1 (с настройкой Google Cloud credentials)"
                )

    def get_connection_info(self) -> str:
        """Возвращает информацию о типе подключения"""
        if not self.enabled:
            return "не подключен"

        return {
            "claude_code_sdk": "Claude Code SDK",
            "claude_code": "Claude Code (автоматически)",
            "anthropic_api": "Anthropic API",
            "bedrock": "Amazon Bedrock",
            "vertex_ai": "Google Vertex AI",
            "none": "не подключен",
        }.get(self.connection_type, "неизвестный")

    async def create_agent_for_task(self, task: Task) -> Agent:
        """Создание агента для конкретной задачи"""
        agent_id = f"agent_{task.id}_{int(time.time())}"

        agent = Agent(
            id=agent_id,
            task_id=task.id,
            status=AgentStatus.IDLE,
            created_at=datetime.now(),
            last_heartbeat=datetime.now(),
            claude_client=self.claude_client,
            squad_session_active=False,
        )

        # Пытаемся создать Claude Squad сессию
        if self.squad_manager.squad_available:
            squad_success = await self.squad_manager.create_squad_session(
                task, agent_id
            )
            if squad_success:
                agent.squad_session_active = True
                logger.info(f"Агент {agent_id} создан с Claude Squad сессией")
            else:
                logger.warning(
                    f"Не удалось создать Claude Squad сессию для агента {agent_id}"
                )

        logger.info(f"Создан агент {agent_id} для задачи #{task.id}")
        return agent

    async def analyze_task(self, agent: Agent, task: Task) -> Dict[str, Any]:
        """Анализ задачи с помощью Claude"""
        if not self.enabled or not self.claude_client:
            logger.warning("Claude недоступен, используется базовый анализ")
            return {
                "type": "unknown",
                "priority": "medium", 
                "estimated_time": "unknown",
                "skills": [],
                "dependencies": [],
                "plan": [
                    "Анализ задачи",
                    "Планирование", 
                    "Реализация",
                    "Тестирование"
                ]
            }

        try:
            prompt = f"""
            Проанализируй следующую задачу разработки:

            Заголовок: {task.title}
            Описание: {task.body}
            Метки: {', '.join(task.labels)}
            URL: {task.url}

            Определи:
            1. Тип задачи (bug, feature, documentation, refactoring, etc.)
            2. Приоритет (high, medium, low)
            3. Примерное время выполнения
            4. Необходимые навыки и технологии
            5. Зависимости от других задач
            6. План выполнения (список шагов)

            Ответь в формате JSON.
            """

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Парсим ответ Claude
            response_text = message.content[0].text

            # Пытаемся извлечь JSON из ответа
            try:
                # Ищем JSON в ответе
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                else:
                    # Если JSON не найден, создаем базовый анализ
                    analysis = {
                        "type": "unknown",
                        "priority": "medium",
                        "estimated_time": "unknown",
                        "skills": [],
                        "dependencies": [],
                        "plan": [
                            "Анализ задачи",
                            "Планирование",
                            "Реализация",
                            "Тестирование",
                        ],
                    }
            except json.JSONDecodeError:
                analysis = {
                    "type": "unknown",
                    "priority": "medium",
                    "estimated_time": "unknown",
                    "skills": [],
                    "dependencies": [],
                    "plan": [
                        "Анализ задачи",
                        "Планирование",
                        "Реализация",
                        "Тестирование",
                    ],
                    "raw_response": response_text,
                }

            agent.last_heartbeat = datetime.now()
            logger.info(f"Агент {agent.id} проанализировал задачу #{task.id}")
            return analysis

        except Exception as e:
            logger.error(f"Ошибка анализа задачи агентом {agent.id}: {e}")
            agent.error_count += 1
            agent.status = AgentStatus.ERROR
            return {"error": str(e)}

    async def execute_task_step(
        self, agent: Agent, task: Task, step: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение шага задачи"""
        if not self.enabled or not self.claude_client:
            logger.warning("Claude недоступен, используется базовое выполнение")
            agent.last_heartbeat = datetime.now()
            agent.status = AgentStatus.WORKING
            return {
                "status": "in_progress",
                "result": f"Базовое выполнение шага '{step}' для задачи {task.title}",
                "next_actions": ["Продолжить работу"],
                "issues": ["Claude API недоступен"],
                "completion_percentage": 25
            }

        try:
            prompt = f"""
            Ты - специализированный агент разработки, работающий над задачей GitHub.

            Задача: {task.title}
            Описание: {task.body}
            Текущий шаг: {step}
            Контекст: {json.dumps(context, ensure_ascii=False, indent=2)}

            Выполни этот шаг и предоставь:
            1. Статус выполнения (completed, in_progress, blocked, failed)
            2. Результат выполнения
            3. Следующие действия
            4. Любые проблемы или препятствия
            5. Процент готовности всей задачи

            Ответь в формате JSON.
            """

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Парсим результат
            try:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = {
                        "status": "in_progress",
                        "result": response_text,
                        "next_actions": ["Продолжить работу"],
                        "issues": [],
                        "completion_percentage": 50,
                    }
            except json.JSONDecodeError:
                result = {
                    "status": "in_progress",
                    "result": response_text,
                    "next_actions": ["Продолжить работу"],
                    "issues": [],
                    "completion_percentage": 50,
                    "raw_response": response_text,
                }

            agent.last_heartbeat = datetime.now()
            agent.status = AgentStatus.WORKING

            logger.info(f"Агент {agent.id} выполнил шаг '{step}' для задачи #{task.id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка выполнения шага агентом {agent.id}: {e}")
            agent.error_count += 1
            agent.status = AgentStatus.ERROR
            return {"status": "failed", "error": str(e)}
