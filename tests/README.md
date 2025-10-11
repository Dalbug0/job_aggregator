# Тестирование Job Aggregator

## Быстрый старт

### Автоматизированный запуск (рекомендуется)

```bash
# Полный цикл (запуск БД → тесты → остановка БД) - основная команда
python scripts/test_runner.py full

# Тесты с покрытием кода (требует предварительно запущенную БД)
python scripts/test_runner.py coverage

# Только тесты (требует предварительно запущенную БД)
python scripts/test_runner.py test
```

## Настройка тестовой среды

### 1. Запуск тестовой базы данных PostgreSQL

```bash
# Запуск тестовой базы данных
docker-compose -f docker-compose.test.yml up -d

# Проверка статуса
docker-compose -f docker-compose.test.yml ps

# Остановка тестовой базы данных
docker-compose -f docker-compose.test.yml down -v
```

### 2. Ручной запуск тестов

```bash
# Активация виртуального окружения
.\venv\Scripts\Activate.ps1

# Запуск всех тестов
python -m pytest tests/ -v

# Запуск конкретного теста
python -m pytest tests/test_vacancies.py -v

# Запуск с покрытием кода
python -m pytest tests/ --cov=app --cov-report=html
```

## Конфигурация тестов

- **База данных**: PostgreSQL 15 на порту 5433
- **Пользователь**: test_user
- **Пароль**: test_pass
- **База данных**: job_aggregator_test

## Структура тестов

- `tests/conftest.py` - конфигурация pytest с фикстурами
- `tests/test_settings.py` - настройки для тестовой среды
- `tests/test_vacancies.py` - тесты для API вакансий

## Производительность тестов

- **Покрытие тестами**: 93%
- **Время выполнения тестов**: ~6 секунд
- **Количество тестов**: 15+ тестовых случаев
- **Отчеты о покрытии**: генерируются в `htmlcov/`

## Добавление новых тестов

1. Создайте тест в директории `tests/`
2. Используйте фикстуры из `conftest.py`
3. Запустите тесты: `python scripts/test_runner.py test`
4. Проверьте покрытие: `python scripts/test_runner.py coverage`

