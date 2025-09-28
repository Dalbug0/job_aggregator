# Job Aggregator API

FastAPI приложение для агрегации вакансий с различных платформ.

## Возможности

- 🔍 Поиск вакансий через API HeadHunter
- 📊 REST API для управления вакансиями
- 🗄️ PostgreSQL база данных
- 🐳 Docker контейнеризация
- 📈 Автоматическое обновление данных
- 🧪 Полное тестовое покрытие

## Технологии

- **Backend**: FastAPI, Python 3.13
- **База данных**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Контейнеризация**: Docker, Docker Compose
- **Тестирование**: pytest, coverage
- **Планировщик**: APScheduler

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd job_aggregator
```

### 2. Настройка окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
.\venv\Scripts\Activate.ps1

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Запуск с Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 4. Запуск локально

```bash
# Запуск основной базы данных
docker-compose up -d db

# Применение миграций
alembic upgrade head

# Запуск приложения
uvicorn app.main:app --reload
```

## API Документация

После запуска приложения документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Тестирование

### Настройка тестовой среды

```bash
# Запуск тестовой базы данных
docker-compose -f docker-compose.test.yml up -d

# Проверка статуса
docker-compose -f docker-compose.test.yml ps
```

### Запуск тестов

```bash
# Простой запуск тестов
python scripts/test_runner.py test

# Тесты с покрытием кода
python scripts/test_runner.py coverage

# Полный цикл (БД + тесты)
python scripts/test_runner.py full
```

### Ручной запуск тестов

```bash
# Все тесты
python -m pytest tests/ -v

# Конкретный тест
python -m pytest tests/test_vacancies.py -v

# С покрытием
python -m pytest tests/ --cov=app --cov-report=html
```

## Структура проекта

```
job_aggregator/
├── app/                    # Основное приложение
│   ├── crud/              # CRUD операции
│   ├── models/            # SQLAlchemy модели
│   ├── routes/            # API маршруты
│   ├── schemas/           # Pydantic схемы
│   ├── services/          # Бизнес-логика
│   ├── config.py          # Конфигурация
│   ├── database.py        # Настройка БД
│   └── main.py            # Точка входа
├── tests/                 # Тесты
│   ├── conftest.py        # Конфигурация pytest
│   ├── test_settings.py   # Настройки для тестов
│   └── test_vacancies.py  # Тесты API
├── scripts/               # Вспомогательные скрипты
├── migrations/           # Alembic миграции
├── docker-compose.yml    # Основные сервисы
├── docker-compose.test.yml # Тестовая БД
└── requirements.txt       # Зависимости
```

## Конфигурация

### Переменные окружения

- `POSTGRES_USER` - пользователь БД
- `POSTGRES_PASSWORD` - пароль БД
- `POSTGRES_DB` - имя БД
- `POSTGRES_HOST` - хост БД
- `POSTGRES_PORT` - порт БД

### Тестовая среда

- **Порт**: 5433
- **База данных**: job_aggregator_test
- **Пользователь**: test_user
- **Пароль**: test_pass

## Разработка

### Миграции базы данных

```bash
# Создание миграции
alembic revision --autogenerate -m "description"

# Применение миграций
alembic upgrade head

# Откат миграций
alembic downgrade -1
```

### Добавление новых тестов

1. Создайте тест в директории `tests/`
2. Используйте фикстуры из `conftest.py`
3. Запустите тесты: `python scripts/test_runner.py test`

## Производительность

- **Покрытие тестами**: 93%
- **Время выполнения тестов**: ~6 секунд
- **API Response Time**: <100ms
- **Database Connection Pool**: 5-20 соединений

## Лицензия

MIT License
