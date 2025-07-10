#!/usr/bin/env python3
"""
GitHub Agent Orchestrator - Interactive CLI
Интерактивное управление агентами через терминал

Usage: uv run agent_cli.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import ClaudeAgentManager
from src.github_manager import GitHubManager
from src.health_monitor import HealthMonitor
from src.models import Agent, AgentStatus, Task

# Load environment variables
env_file = Path(".env")
if env_file.exists():
    from dotenv import load_dotenv

    load_dotenv()

console = Console()
STATE_FILE = Path("agent_state.json")


class AgentController:
    """Контроллер для управления агентами"""

    def __init__(self):
        # Проверяем переменные окружения
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.repo_name = os.getenv("GITHUB_REPO")

        if not all([self.github_token, self.repo_name]):
            console.print(
                "❌ [red]Ошибка: Не установлены GITHUB_TOKEN или GITHUB_REPO[/red]"
            )
            sys.exit(1)

        # Инициализируем менеджеры
        self.github_manager = GitHubManager(self.github_token, self.repo_name)
        self.claude_manager = ClaudeAgentManager(self.anthropic_api_key)
        self.health_monitor = HealthMonitor()

        # Показываем статус подключения Claude
        if self.claude_manager.enabled:
            console.print(
                f"🤖 [green]Claude подключен через {self.claude_manager.get_connection_info()}[/green]"
            )
        else:
            console.print(
                "⚠️  [yellow]Claude недоступен - не настроен способ подключения[/yellow]"
            )

        # Хранилище агентов
        self.agents: Dict[str, Agent] = {}
        self.task_assignments: Dict[int, str] = {}  # task_id -> agent_id

        # Флаг для мониторинга в фоне
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_enabled = False

        # Загружаем сохраненное состояние
        self.load_state()

    def save_state(self):
        """Сохранение состояния в файл"""
        try:
            state = {
                "task_assignments": self.task_assignments,
                "agents": {},
                "timestamp": datetime.now().isoformat(),
            }

            # Сериализуем агентов
            for agent_id, agent in self.agents.items():
                state["agents"][agent_id] = {
                    "id": agent.id,
                    "task_id": agent.task_id,
                    "status": agent.status.value,
                    "created_at": agent.created_at.isoformat(),
                    "last_heartbeat": agent.last_heartbeat.isoformat(),
                    "error_count": agent.error_count,
                    "max_errors": agent.max_errors,
                }

            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            console.print(f"⚠️  [yellow]Не удалось сохранить состояние: {e}[/yellow]")

    def load_state(self):
        """Загрузка состояния из файла"""
        try:
            if not STATE_FILE.exists():
                return

            with open(STATE_FILE, encoding="utf-8") as f:
                state = json.load(f)

            self.task_assignments = state.get("task_assignments", {})
            # Конвертируем ключи обратно в int
            self.task_assignments = {
                int(k): v for k, v in self.task_assignments.items()
            }

            # Восстанавливаем агентов
            agents_data = state.get("agents", {})
            for agent_id, agent_data in agents_data.items():
                try:
                    agent = Agent(
                        id=agent_data["id"],
                        task_id=agent_data["task_id"],
                        status=AgentStatus(agent_data["status"]),
                        created_at=datetime.fromisoformat(agent_data["created_at"]),
                        last_heartbeat=datetime.fromisoformat(
                            agent_data["last_heartbeat"]
                        ),
                        claude_client=self.claude_manager.claude_client,
                        error_count=agent_data.get("error_count", 0),
                        max_errors=agent_data.get("max_errors", 3),
                    )
                    self.agents[agent_id] = agent
                except Exception as e:
                    console.print(
                        f"⚠️  [yellow]Не удалось восстановить агента {agent_id}: {e}[/yellow]"
                    )

            if self.agents or self.task_assignments:
                console.print(
                    f"📂 [dim]Загружено состояние: {len(self.agents)} агентов, {len(self.task_assignments)} назначений[/dim]"
                )

        except Exception as e:
            console.print(f"⚠️  [yellow]Не удалось загрузить состояние: {e}[/yellow]")

    async def load_tasks(self) -> List[Task]:
        """Загрузка актуальных задач из GitHub"""
        return await self.github_manager.get_open_issues()

    def display_tasks(self, tasks: List[Task], show_assigned=True):
        """Отображение списка задач"""
        table = Table(title="📋 GitHub Issues")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Заголовок", style="white")
        table.add_column("Метки", style="yellow")
        table.add_column("Агент", style="green")
        table.add_column("Создано", style="dim")

        for task in tasks:
            agent_info = "—"
            if task.id in self.task_assignments:
                agent_id = self.task_assignments[task.id]
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    status_color = {
                        AgentStatus.IDLE: "blue",
                        AgentStatus.WORKING: "green",
                        AgentStatus.ERROR: "red",
                        AgentStatus.COMPLETED: "bright_green",
                        AgentStatus.STOPPED: "dim",
                    }.get(agent.status, "white")
                    agent_info = f"[{status_color}]{agent.id}[/{status_color}]"

            # Фильтрация
            if not show_assigned and task.id in self.task_assignments:
                continue

            labels = ", ".join(task.labels[:3]) if task.labels else "—"
            if len(task.labels) > 3:
                labels += "..."

            table.add_row(
                str(task.id),
                task.title[:50] + ("..." if len(task.title) > 50 else ""),
                labels,
                agent_info,
                task.created_at.strftime("%d.%m"),
            )

        console.print(table)

    def display_agents(self):
        """Отображение списка агентов"""
        if not self.agents:
            console.print("📭 [dim]Нет активных агентов[/dim]")
            return

        table = Table(title="🤖 Активные агенты")
        table.add_column("ID агента", style="cyan", no_wrap=True)
        table.add_column("Задача", style="white")
        table.add_column("Статус", style="white")
        table.add_column("Ошибки", style="red")
        table.add_column("Последний heartbeat", style="dim")

        for agent in self.agents.values():
            status_color = {
                AgentStatus.IDLE: "blue",
                AgentStatus.WORKING: "green",
                AgentStatus.ERROR: "red",
                AgentStatus.COMPLETED: "bright_green",
                AgentStatus.STOPPED: "dim",
            }.get(agent.status, "white")

            health = "❤️"  # Упрощаем для CLI

            table.add_row(
                agent.id,
                f"#{agent.task_id}",
                f"[{status_color}]{agent.status.value}[/{status_color}] {health}",
                str(agent.error_count),
                agent.last_heartbeat.strftime("%H:%M:%S"),
            )

        console.print(table)

    async def assign_agent_to_task(self, task_id: int) -> bool:
        """Назначение агента на задачу"""
        # Проверяем, есть ли уже агент на этой задаче
        if task_id in self.task_assignments:
            console.print(
                f"❌ [red]На задачу #{task_id} уже назначен агент {self.task_assignments[task_id]}[/red]"
            )
            return False

        # Получаем задачу
        tasks = await self.load_tasks()
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            console.print(f"❌ [red]Задача #{task_id} не найдена[/red]")
            return False

        try:
            # Создаем агента
            agent = await self.claude_manager.create_agent_for_task(task)
            self.agents[agent.id] = agent
            self.task_assignments[task_id] = agent.id

            # Анализируем задачу
            if self.claude_manager.enabled:
                with console.status(f"🧠 Анализирую задачу #{task_id}..."):
                    analysis = await self.claude_manager.analyze_task(agent, task)

                console.print(
                    f"✅ [green]Агент {agent.id} назначен на задачу #{task_id}[/green]"
                )

                # Показываем анализ
                analysis_panel = Panel(
                    f"**Тип:** {analysis.get('type', 'unknown')}\n"
                    f"**Приоритет:** {analysis.get('priority', 'medium')}\n"
                    f"**Время:** {analysis.get('estimated_time', 'unknown')}\n"
                    f"**Навыки:** {', '.join(analysis.get('skills', []))[:50]}",
                    title="🧠 Анализ задачи",
                    border_style="green",
                )
                console.print(analysis_panel)
            else:
                console.print(
                    f"✅ [green]Агент {agent.id} назначен на задачу #{task_id}[/green]"
                )
                console.print(
                    "ℹ️  [blue]Анализ задачи недоступен (Claude не подключен)[/blue]"
                )

            # Сохраняем состояние
            self.save_state()
            return True

        except Exception as e:
            console.print(f"❌ [red]Ошибка создания агента: {e}[/red]")
            return False

    async def remove_agent_from_task(self, task_id: int) -> bool:
        """Удаление агента с задачи"""
        if task_id not in self.task_assignments:
            console.print(f"❌ [red]На задаче #{task_id} нет назначенного агента[/red]")
            return False

        agent_id = self.task_assignments[task_id]

        if agent_id in self.agents:
            agent = self.agents[agent_id]
            # Уведомляем в GitHub
            try:
                comment = (
                    f"🛑 Агент {agent_id} был снят с задачи по команде пользователя."
                )
                self.github_manager.create_comment(task_id, comment)
            except Exception:
                pass  # Игнорируем ошибки комментариев

            del self.agents[agent_id]

        del self.task_assignments[task_id]
        console.print(f"✅ [green]Агент снят с задачи #{task_id}[/green]")

        # Сохраняем состояние
        self.save_state()
        return True

    async def restart_agent(self, agent_id: str) -> bool:
        """Перезапуск агента"""
        if agent_id not in self.agents:
            console.print(f"❌ [red]Агент {agent_id} не найден[/red]")
            return False

        agent = self.agents[agent_id]
        agent.error_count = 0
        agent.status = AgentStatus.IDLE
        agent.last_heartbeat = datetime.now()

        console.print(f"🔄 [yellow]Агент {agent_id} перезапущен[/yellow]")

        # Сохраняем состояние
        self.save_state()
        return True

    async def start_monitoring(self):
        """Запуск фонового мониторинга"""
        if self.monitoring_enabled:
            console.print("❌ [red]Мониторинг уже запущен[/red]")
            return

        self.monitoring_enabled = True

        async def monitor_loop():
            while self.monitoring_enabled:
                try:
                    # Проверяем здоровье агентов
                    unhealthy_agents = await self.health_monitor.get_unhealthy_agents(
                        list(self.agents.values()), self.claude_manager
                    )

                    for agent in unhealthy_agents:
                        console.print(
                            f"🩺 [yellow]Обнаружен неработающий агент {agent.id}, перезапускаю...[/yellow]"
                        )
                        await self.restart_agent(agent.id)

                        # Уведомляем в GitHub
                        try:
                            comment = f"🔄 Агент {agent.id} был автоматически перезапущен из-за проблем с работоспособностью."
                            self.github_manager.create_comment(agent.task_id, comment)
                        except Exception:
                            pass

                    await asyncio.sleep(300)  # 5 минут
                except Exception as e:
                    console.print(f"❌ [red]Ошибка мониторинга: {e}[/red]")
                    await asyncio.sleep(30)

        self.monitoring_task = asyncio.create_task(monitor_loop())
        console.print(
            "🟢 [green]Фоновый мониторинг запущен (проверка каждые 5 минут)[/green]"
        )

    async def stop_monitoring(self):
        """Остановка фонового мониторинга"""
        if not self.monitoring_enabled:
            console.print("❌ [red]Мониторинг не запущен[/red]")
            return

        self.monitoring_enabled = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        console.print("🔴 [red]Фоновый мониторинг остановлен[/red]")


controller = AgentController()


@click.group()
def cli():
    """🤖 GitHub Agent Orchestrator - Интерактивное управление агентами"""
    pass


@cli.command()
def tasks():
    """📋 Показать все задачи"""

    async def _show_tasks():
        tasks = await controller.load_tasks()
        controller.display_tasks(tasks)

    asyncio.run(_show_tasks())


@cli.command()
def agents():
    """🤖 Показать активных агентов"""
    controller.display_agents()


@cli.command()
@click.argument("task_id", type=int)
def assign(task_id):
    """👥 Назначить агента на задачу"""

    async def _assign():
        await controller.assign_agent_to_task(task_id)

    asyncio.run(_assign())


@cli.command()
@click.argument("task_id", type=int)
def remove(task_id):
    """🗑️ Снять агента с задачи"""

    async def _remove():
        await controller.remove_agent_from_task(task_id)

    asyncio.run(_remove())


@cli.command()
@click.argument("agent_id")
def restart(agent_id):
    """🔄 Перезапустить агента"""

    async def _restart():
        await controller.restart_agent(agent_id)

    asyncio.run(_restart())


@cli.command()
def monitor():
    """👁️ Запустить фоновый мониторинг"""

    async def _monitor():
        await controller.start_monitoring()
        try:
            while controller.monitoring_enabled:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await controller.stop_monitoring()

    asyncio.run(_monitor())


@cli.command()
def interactive():
    """🎮 Интерактивный режим"""

    async def _interactive():
        console.print(
            Panel(
                "🤖 [bold cyan]GitHub Agent Orchestrator[/bold cyan]\n"
                "Интерактивное управление агентами",
                border_style="cyan",
            )
        )

        while True:
            console.print("\n" + "=" * 50)
            console.print("[bold]Доступные команды:[/bold]")
            console.print("1. 📋 Показать задачи")
            console.print("2. 🤖 Показать агентов")
            console.print("3. 👥 Назначить агента")
            console.print("4. 🗑️  Снять агента")
            console.print("5. 🔄 Перезапустить агента")
            console.print("6. 👁️  Управление мониторингом")
            console.print("0. 🚪 Выход")

            try:
                choice = Prompt.ask(
                    "Выберите действие", choices=["0", "1", "2", "3", "4", "5", "6"]
                )

                if choice == "0":
                    if controller.monitoring_enabled:
                        await controller.stop_monitoring()
                    console.print("👋 [yellow]До свидания![/yellow]")
                    break

                elif choice == "1":
                    tasks = await controller.load_tasks()
                    controller.display_tasks(tasks)

                elif choice == "2":
                    controller.display_agents()

                elif choice == "3":
                    tasks = await controller.load_tasks()
                    unassigned_tasks = [
                        t for t in tasks if t.id not in controller.task_assignments
                    ]

                    if not unassigned_tasks:
                        console.print(
                            "📭 [dim]Нет доступных задач для назначения[/dim]"
                        )
                        continue

                    controller.display_tasks(unassigned_tasks, show_assigned=False)
                    task_id = click.prompt("Введите ID задачи", type=int)
                    await controller.assign_agent_to_task(task_id)

                elif choice == "4":
                    if not controller.task_assignments:
                        console.print("📭 [dim]Нет назначенных агентов[/dim]")
                        continue

                    console.print("Назначенные агенты:")
                    for task_id, agent_id in controller.task_assignments.items():
                        console.print(f"  • Задача #{task_id} → {agent_id}")

                    task_id = click.prompt("Введите ID задачи", type=int)
                    await controller.remove_agent_from_task(task_id)

                elif choice == "5":
                    if not controller.agents:
                        console.print("📭 [dim]Нет активных агентов[/dim]")
                        continue

                    controller.display_agents()
                    agent_id = click.prompt("Введите ID агента")
                    await controller.restart_agent(agent_id)

                elif choice == "6":
                    if controller.monitoring_enabled:
                        if Confirm.ask("🔴 Остановить мониторинг?"):
                            await controller.stop_monitoring()
                    else:
                        if Confirm.ask("🟢 Запустить фоновый мониторинг?"):
                            await controller.start_monitoring()

            except KeyboardInterrupt:
                if controller.monitoring_enabled:
                    await controller.stop_monitoring()
                console.print("\n👋 [yellow]Выход по Ctrl+C[/yellow]")
                break
            except Exception as e:
                console.print(f"❌ [red]Ошибка: {e}[/red]")

    asyncio.run(_interactive())


if __name__ == "__main__":
    cli()
