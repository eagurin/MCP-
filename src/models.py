"""
Модели данных для GitHub Agent Orchestrator
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

import anthropic


class AgentStatus(Enum):
    """Статусы агентов"""

    IDLE = "idle"
    WORKING = "working"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class Task:
    """Представление задачи из GitHub Issue"""

    id: int
    title: str
    body: str
    labels: List[str]
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime
    state: str
    url: str


@dataclass
class Agent:
    """Представление агента"""

    id: str
    task_id: int
    status: AgentStatus
    created_at: datetime
    last_heartbeat: datetime
    claude_client: Optional[anthropic.Anthropic]
    process: Optional[asyncio.subprocess.Process] = None
    error_count: int = 0
    max_errors: int = 3
    squad_session_active: bool = False
