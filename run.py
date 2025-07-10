#!/usr/bin/env python3
"""
GitHub Agent Orchestrator - Quick Start Script

Usage:
    uv run run.py                    # Запуск в обычном режиме
    uv run run.py --status           # Проверка статуса
    uv run run.py --dry-run          # Проверка конфигурации без запуска
    uv run run.py --install-deps     # Установка зависимостей

Requirements in .env file:
    GITHUB_TOKEN=your_github_token
    ANTHROPIC_API_KEY=your_anthropic_api_key
    GITHUB_REPO=owner/repo_name
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file if it exists
env_file = Path(".env")
if env_file.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv не установлен, используйте --install-deps")


def check_claude_squad() -> bool:
    """Проверка доступности Claude Squad"""
    try:
        result = subprocess.run(
            ["which", "cs"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Claude Squad доступен")
            return True
        else:
            print("⚠️  Claude Squad не найден")
            print("   Установите Claude Squad:")
            print("   https://github.com/smtg-ai/claude-squad")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки Claude Squad: {e}")
        return False


def check_dependencies() -> bool:
    """Проверка установленных зависимостей"""
    required_packages = ["anthropic", "github", "aiohttp", "dotenv", "click", "rich"]

    missing_packages: List[str] = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        packages_str = ", ".join(missing_packages)
        print(f"❌ Отсутствуют пакеты: {packages_str}")
        print("   Установите зависимости: uv run run.py --install-deps")
        return False

    print("✅ Все зависимости установлены")
    return True


def install_dependencies() -> None:
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.run(["uv", "sync"], check=True)
        print("✅ Зависимости успешно установлены")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        sys.exit(1)


def check_environment() -> bool:
    """Check if all required environment variables are set"""
    required_vars = ["GITHUB_TOKEN", "GITHUB_REPO"]
    missing_vars: List[str] = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Create a .env file with the following content:")
        print("GITHUB_TOKEN=your_github_token_here")
        print("GITHUB_REPO=owner/repo_name")
        print("ANTHROPIC_API_KEY=your_anthropic_api_key  # optional")
        print("CHECK_INTERVAL=300  # optional")
        return False

    print("✅ Environment variables are set")
    print(f"   GitHub Repo: {os.getenv('GITHUB_REPO')}")
    
    # Safely handle None from os.getenv
    github_token = os.getenv('GITHUB_TOKEN') or ""
    print(f"   GitHub Token: {github_token[:10]}...")

    # Проверяем способы подключения к Claude
    claude_connection = "Claude Code (автоматически)"
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        claude_connection = f"Anthropic API ({anthropic_key[:15]}...)"
    elif os.getenv("CLAUDE_CODE_USE_BEDROCK") == "1":
        claude_connection = "Amazon Bedrock"
    elif os.getenv("CLAUDE_CODE_USE_VERTEX") == "1":
        claude_connection = "Google Vertex AI"

    print(f"   Claude подключение: {claude_connection}")
    return True


def check_status() -> bool:
    """Проверка статуса системы"""
    print("🔍 Проверка статуса системы...")
    print("=" * 50)

    # Проверяем зависимости
    deps_ok = check_dependencies()

    # Проверяем переменные окружения
    env_ok = check_environment()

    # Проверяем Claude Squad
    squad_ok = check_claude_squad()

    print("\n📊 Результат проверки:")
    print(f"   Зависимости: {'✅' if deps_ok else '❌'}")
    print(f"   Конфигурация: {'✅' if env_ok else '❌'}")
    print(f"   Claude Squad: {'✅' if squad_ok else '⚠️'}")

    if deps_ok and env_ok:
        print("\n🎉 Система готова к запуску!")
    else:
        print("\n⚠️  Система не готова к запуску")

    return deps_ok and env_ok


def main() -> None:
    """Основная функция с поддержкой аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="GitHub Agent Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--status", action="store_true", help="Проверить статус системы"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Проверить конфигурацию без запуска"
    )

    parser.add_argument(
        "--install-deps", action="store_true", help="Установить зависимости"
    )

    args = parser.parse_args()

    print("🚀 GitHub Agent Orchestrator")
    print("=" * 50)

    if args.install_deps:
        install_dependencies()
        return

    if args.status:
        check_status()
        return

    if args.dry_run:
        print("🧪 Проверка конфигурации (dry run)...")
        if check_status():
            print("✅ Конфигурация корректна, готов к запуску")
        else:
            print("❌ Конфигурация содержит ошибки")
        return

    # Обычный запуск
    if not check_dependencies():
        print("💡 Используйте --install-deps для установки зависимостей")
        sys.exit(1)

    if not check_environment():
        sys.exit(1)

    check_claude_squad()

    print("\n📦 Starting orchestrator...")

    # Import and run the main function from src/main.py
    try:
        # Import and run the main function from src/main.py
        from src.main import main as src_main
        asyncio.run(src_main())
    except KeyboardInterrupt:
        print("\n⏹️  Orchestrator stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
