#!/usr/bin/env python3
"""
GitHub Agent Orchestrator - Главный запускатор
Система автоматического управления GitHub разработкой с помощью Claude агентов

Использование:
    python orchestrator.py                 # Запуск оркестратора
    python orchestrator.py --status        # Проверка статуса  
    python orchestrator.py --help-claude   # Работа с Claude Squad
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Добавляем текущую директорию в PATH
sys.path.insert(0, str(Path(__file__).parent))

# Загружаем переменные окружения
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        print("⚠️  python-dotenv не установлен")

def check_status():
    """Проверка статуса системы"""
    # Import check_status from the root run.py
    import sys
    from pathlib import Path
    
    # Add root directory to path
    root_path = Path(__file__).parent
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
    
    from run import check_status as run_check_status
    return run_check_status()

def help_claude():
    """Помощь по работе с Claude Squad"""
    print("🎯 Claude Squad Helper")
    print("=" * 50)
    
    # Проверяем активные сессии
    try:
        result = subprocess.run([
            sys.executable, "src/claude_squad_helper.py", "--sessions"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Ошибка получения сессий")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n💡 Доступные команды:")
    print("  python src/claude_squad_helper.py --sessions    # Активные сессии")
    print("  python src/claude_squad_helper.py --prompt 11   # Промпт для задачи")
    print("  python src/claude_squad_helper.py --launch      # Запуск Claude Squad")
    print("  cs                                              # Прямой запуск")

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="GitHub Agent Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python orchestrator.py                 # Запуск системы
  python orchestrator.py --status        # Проверка готовности
  python orchestrator.py --help-claude   # Помощь по Claude Squad
        """
    )
    
    parser.add_argument(
        "--status", action="store_true",
        help="Проверить статус и готовность системы"
    )
    
    parser.add_argument(
        "--help-claude", action="store_true", 
        help="Показать помощь по работе с Claude Squad"
    )
    
    args = parser.parse_args()
    
    print("🚀 GitHub Agent Orchestrator")
    print("=" * 50)
    
    if args.status:
        check_status()
        return
        
    if args.help_claude:
        help_claude()
        return
    
    # Основной запуск
    print("📦 Запуск системы...")
    print("💡 Для остановки нажмите Ctrl+C")
    print("💡 Для работы с Claude Squad: python orchestrator.py --help-claude")
    print("=" * 50)
    
    try:
        # Запускаем из src директории
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        import main
        asyncio.run(main.main())
    except KeyboardInterrupt:
        print("\n⏹️  Оркестратор остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()