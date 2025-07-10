"""
GitHub Manager - управление взаимодействием с GitHub API
"""

import logging
from typing import List

from github import Github

from src.models import Task

logger = logging.getLogger(__name__)


class GitHubManager:
    """Менеджер для работы с GitHub API"""

    def __init__(self, github_token: str, repo_name: str):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
        logger.info(f"Подключен к репозиторию: {repo_name}")

    async def get_open_issues(self) -> List[Task]:
        """Получение открытых issues из репозитория"""
        try:
            issues = self.repo.get_issues(state="open")
            tasks = []

            for issue in issues:
                # Пропускаем pull requests
                if issue.pull_request is not None:
                    continue

                task = Task(
                    id=issue.number,
                    title=issue.title,
                    body=issue.body or "",
                    labels=[label.name for label in issue.labels],
                    assignee=issue.assignee.login if issue.assignee else None,
                    created_at=issue.created_at,
                    updated_at=issue.updated_at,
                    state=issue.state,
                    url=issue.html_url,
                )
                tasks.append(task)

            logger.info(f"Найдено {len(tasks)} открытых задач")
            return tasks

        except Exception as e:
            logger.error(f"Ошибка получения issues: {e}")
            return []

    async def create_comment(self, issue_number: int, comment: str) -> bool:
        """Создание комментария к issue"""
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            logger.info(f"Комментарий добавлен к issue #{issue_number}")
            return True
        except Exception as e:
            logger.warning(f"Не удалось создать комментарий к issue #{issue_number}: {e}")
            logger.info(f"Комментарий не создан, но продолжаем работу: {comment[:100]}...")
            return False

    def assign_issue(self, issue_number: int, assignee: str) -> bool:
        """Назначение исполнителя для issue"""
        try:
            issue = self.repo.get_issue(issue_number)
            issue.edit(assignee=assignee)
            logger.info(f"Issue #{issue_number} назначен на {assignee}")
            return True
        except Exception as e:
            logger.error(f"Ошибка назначения issue: {e}")
            return False
