#!/usr/bin/env python3
"""
Скрипт для управления тестовой базой данных PostgreSQL
"""
import subprocess
import sys
import time
import os

def start_test_db():
    """Запускает тестовую базу данных"""
    print("🚀 Запуск тестовой базы данных PostgreSQL...")
    try:
        result = subprocess.run([
            "docker-compose", "-f", "docker-compose.test.yml", "up", "-d"
        ], check=True, capture_output=True, text=True)
        print("✅ Тестовая база данных запущена")
        print("📊 База данных доступна на localhost:5433")
        print("🔗 Подключение: postgresql://test_user:test_pass@localhost:5433/job_aggregator_test")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске базы данных: {e}")
        print(f"Вывод: {e.stderr}")
        return False
    return True

def stop_test_db():
    """Останавливает тестовую базу данных"""
    print("🛑 Остановка тестовой базы данных...")
    try:
        subprocess.run([
            "docker-compose", "-f", "docker-compose.test.yml", "down", "-v"
        ], check=True, capture_output=True, text=True)
        print("✅ Тестовая база данных остановлена")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при остановке базы данных: {e}")
        return False
    return True

def check_db_status():
    """Проверяет статус тестовой базы данных"""
    try:
        result = subprocess.run([
            "docker-compose", "-f", "docker-compose.test.yml", "ps"
        ], capture_output=True, text=True)
        print("📊 Статус тестовой базы данных:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при проверке статуса: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python scripts/test_db.py start   - запустить тестовую БД")
        print("  python scripts/test_db.py stop    - остановить тестовую БД")
        print("  python scripts/test_db.py status  - проверить статус БД")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_test_db()
    elif command == "stop":
        stop_test_db()
    elif command == "status":
        check_db_status()
    else:
        print(f"❌ Неизвестная команда: {command}")
        sys.exit(1)
