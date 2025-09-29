# Тестирование Job Aggregator

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

### 2. Запуск тестов

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

