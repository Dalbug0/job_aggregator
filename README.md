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

### 2. Настройка окружения (локальный запуск)

Если вы запускаете через Docker, этот шаг не нужен — контейнер сам установит зависимости из `requirements.txt` согласно `Dockerfile`.

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
.\venv\Scripts\Activate.ps1

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей (только для локального запуска без Docker)
pip install -r requirements.txt
```

### 3. Запуск с Docker

При запуске в Docker не требуется локально ставить зависимости и настраивать venv — всё выполнится внутри контейнера.

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

### Быстрый старт

```bash
# Полный цикл (запуск БД → тесты → остановка БД) - основная команда
python scripts/test_runner.py full

# Тесты с покрытием кода (требует предварительно запущенную БД)
python scripts/test_runner.py coverage
```

**Покрытие тестами**: 93%

📖 **Подробная информация о тестировании**: [tests/README.md](tests/README.md)

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

📖 **Подробная информация**: [tests/README.md](tests/README.md)

## Производительность

- **Покрытие тестами**: 93%
- **Время выполнения тестов**: ~6 секунд
- **API Response Time**: <100ms
- **Database Connection Pool**: 5-20 соединений

## Лицензия

MIT License
