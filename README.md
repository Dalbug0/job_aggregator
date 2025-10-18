# Job Aggregator API

FastAPI приложение для агрегации вакансий с различных платформ.

## Возможности

- 🔍 Поиск вакансий через API HeadHunter
- 📊 Полный CRUD API для управления вакансиями
- 🔧 Фильтрация и сортировка вакансий
- 🗄️ PostgreSQL база данных
- 🐳 Docker контейнеризация
- 📈 Автоматическое обновление данных
- 🧪 Полное тестовое покрытие (93%)

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

### API Endpoints

#### Вакансии
- `GET /vacancies` - Получить список вакансий с фильтрацией
  - Параметры: `company`, `location`, `skip`, `limit`, `sort_by`
- `POST /vacancies` - Создать новую вакансию
- `PUT /vacancies/{id}` - Обновить вакансию
- `DELETE /vacancies/{id}` - Удалить вакансию

#### Системные
- `GET /health` - Проверка состояния приложения
- `GET /health/db` - Проверка состояния базы данных

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
│   ├── crud/              # CRUD операции (создание, чтение, обновление, удаление)
│   ├── models/            # SQLAlchemy модели
│   ├── routes/            # API маршруты (REST endpoints)
│   ├── schemas/           # Pydantic схемы (валидация данных)
│   ├── services/          # Бизнес-логика (HH API интеграция)
│   ├── config.py          # Конфигурация приложения
│   ├── database.py        # Настройка БД и сессий
│   ├── main.py            # Точка входа FastAPI
│   ├── scheduler.py       # Планировщик задач
│   └── exceptions.py      # Обработка ошибок
├── tests/                 # Тесты
│   ├── conftest.py        # Конфигурация pytest и фикстуры
│   ├── test_settings.py   # Настройки для тестовой среды
│   └── test_vacancies.py  # Тесты API (CRUD операции)
├── scripts/               # Вспомогательные скрипты
│   ├── test_runner.py     # Автоматизированный запуск тестов
│   └── test_db.py         # Тестирование БД
├── migrations/           # Alembic миграции БД
├── docker-compose.yml    # Основные сервисы
├── docker-compose.test.yml # Тестовая БД
└── requirements.txt       # Зависимости Python
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
