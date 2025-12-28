#!/usr/bin/env python3
"""
Скрипт для управления тестами Job Aggregator
"""
import subprocess
import sys


def run_tests():
    """Запускает все тесты"""
    print("Запуск тестов...")
    try:
        _ = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"], check=True
        )
        print("Все тесты прошли успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Тесты не прошли: {e}")
        return False


def run_auth_tests():
    """Запускает только тесты аутентификации"""
    print("Запуск тестов аутентификации...")
    try:
        _ = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_auth.py", "-v"],
            check=True,
        )
        print("Тесты аутентификации прошли успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Тесты аутентификации не прошли: {e}")
        return False


def run_vacancy_tests():
    """Запускает только тесты вакансий"""
    print("Запуск тестов вакансий...")
    try:
        _ = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_vacancies.py", "-v"],
            check=True,
        )
        print("Тесты вакансий прошли успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Тесты вакансий не прошли: {e}")
        return False


def run_tests_with_coverage():
    """Запускает тесты с покрытием кода"""
    print("Запуск тестов с покрытием кода...")
    try:
        _ = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--cov=app",
                "--cov-report=term-missing",
            ],
            check=True,
        )
        print("Тесты с покрытием завершены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Тесты не прошли: {e}")
        return False


def check_test_db():
    """Проверяет статус тестовой базы данных"""
    print("Проверка статуса тестовой базы данных...")
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "ps"],
            capture_output=True,
            text=True,
        )
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "ps"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при проверке статуса БД: {e}")
        return False


def start_test_db():
    """Запускает тестовую базу данных"""
    print("Запуск тестовой базы данных...")
    try:
        _ = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Тестовая база данных запущена")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске БД: {e}")
        return False


def stop_test_db():
    """Останавливает тестовую базу данных"""
    print("Остановка тестовой базы данных...")
    try:
        _ = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Тестовая база данных остановлена")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при остановке БД: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print(
            "  python scripts/test_runner.py test           "
            "- запустить все тесты"
        )
        print(
            "  python scripts/test_runner.py auth           "
            "- запустить тесты аутентификации"
        )
        print(
            "  python scripts/test_runner.py vacancies      "
            "- запустить тесты вакансий"
        )
        print(
            "  python scripts/test_runner.py coverage       "
            "- запустить тесты с покрытием"
        )
        print(
            "  python scripts/test_runner.py db-status      "
            "- проверить статус БД"
        )
        print(
            "  python scripts/test_runner.py db-start       "
            "- запустить тестовую БД"
        )
        print(
            "  python scripts/test_runner.py db-stop        "
            "- остановить тестовую БД"
        )
        print(
            "  python scripts/test_runner.py full           "
            "- запустить БД, тесты и остановить БД"
        )
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "test":
        run_tests()
    elif command == "auth":
        run_auth_tests()
    elif command == "vacancies":
        run_vacancy_tests()
    elif command == "coverage":
        run_tests_with_coverage()
    elif command == "db-status":
        check_test_db()
    elif command == "db-start":
        start_test_db()
    elif command == "db-stop":
        stop_test_db()
    elif command == "full":
        if start_test_db():
            try:
                run_tests()
            finally:
                # Всегда останавливаем БД после тестов
                stop_test_db()
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)
