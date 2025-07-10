#!/usr/bin/env python3
"""
Claude Squad Helper - удобный интерфейс для работы с Claude Squad v1.0.8+
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

def get_active_sessions() -> List[Dict]:
    """Получение списка активных сессий из оркестратора"""
    try:
        # Читаем состояние из лог файла оркестратора
        log_file = Path("orchestrator.log")
        if not log_file.exists():
            return []
        
        sessions = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "Создана логическая Claude Squad сессия" in line:
                    # Парсим сессию из лога
                    if "github-task-" in line:
                        task_id = line.split("github-task-")[1].split()[0]
                        sessions.append({
                            "task_id": task_id,
                            "session_name": f"github-task-{task_id}",
                            "status": "active"
                        })
        
        return sessions
    except Exception as e:
        print(f"Ошибка получения сессий: {e}")
        return []

def show_session_prompt(task_id: str):
    """Показать промпт для задачи"""
    try:
        # Читаем промпт из логов
        log_file = Path("orchestrator.log")
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"\n🤖 Промпт для задачи #{task_id}:")
            print("=" * 60)
            print(f"""Ты - специализированный агент разработки GitHub (ID: agent_{task_id}).

Найди issue #{task_id} в репозитории и проанализируй задачу.

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

Начни с анализа задачи и создания плана выполнения.""")
            print("=" * 60)
            
    except Exception as e:
        print(f"Ошибка показа промпта: {e}")

def launch_claude_squad():
    """Запуск Claude Squad для интерактивной работы"""
    try:
        print("🚀 Запуск Claude Squad...")
        print("💡 Используйте клавиши:")
        print("   n - создать новую сессию")
        print("   N - создать сессию с промптом")
        print("   ↑/↓ - навигация по сессиям")
        print("   Enter - подключиться к сессии")
        print("   ctrl-q - отключиться от сессии")
        print("   D - удалить сессию")
        print("=" * 50)
        
        # Запускаем Claude Squad
        subprocess.run(["cs"], check=False)
        
    except Exception as e:
        print(f"Ошибка запуска Claude Squad: {e}")

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Claude Squad Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--sessions", action="store_true", 
        help="Показать активные сессии оркестратора"
    )
    
    parser.add_argument(
        "--prompt", type=str, metavar="TASK_ID",
        help="Показать промпт для задачи"
    )
    
    parser.add_argument(
        "--launch", action="store_true",
        help="Запустить Claude Squad интерактивно"
    )
    
    args = parser.parse_args()
    
    if args.sessions:
        sessions = get_active_sessions()
        if sessions:
            print("📋 Активные сессии оркестратора:")
            for session in sessions:
                print(f"  • Задача #{session['task_id']} - {session['session_name']}")
            print(f"\n💡 Используйте: python claude_squad_helper.py --prompt TASK_ID")
        else:
            print("❌ Активных сессий не найдено")
            
    elif args.prompt:
        show_session_prompt(args.prompt)
        
    elif args.launch:
        launch_claude_squad()
        
    else:
        parser.print_help()
        print("\n🔍 Примеры использования:")
        print("  python claude_squad_helper.py --sessions")
        print("  python claude_squad_helper.py --prompt 11")
        print("  python claude_squad_helper.py --launch")

if __name__ == "__main__":
    main()