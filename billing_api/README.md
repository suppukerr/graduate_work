# Billing API

Сервис биллинга для управления подписками и платежами.

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Gunicorn
- Docker, Docker Compose

## Запуск

1. Перейдите в директорию `billing_api`:
```bash
cd billing_api
```

2. Создайте `.env` файл на основе `.env.example`:
```bash
cp .env.example .env
```

3. Запустите в терминале или через докер

## Локальный запуск через Docker (будет доступен только внутри докер-сети - для других сервисов проекта)

```bash
docker-compose up --build
```

## Локальный запуск в терминале

```bash
poetry install
```

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## API Endpoints

| Метод | URL | Назначение |
|-------|-----|------------|
| GET | `/api/v1/billing/health/service` | Проверка состояния сервиса |
| GET | `/api/v1/billing/health/db` | Проверка подключения к БД |
| POST | `/api/v1/billing/events/` | Отправка события биллинга в Kafka |

### Пример отправки события биллинга

```bash
curl -X POST "http://localhost:8001/api/v1/billing/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "event_type": "SUBSCRIBE"
  }'
```

Ответ:
```json
{
  "status": "accepted",
  "event_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Event queued for processing"
}
```

## Структура проекта

```
billing_api/
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── heath.py          # Health check endpoints
│   ├── core/
│   │   ├── config.py             # Конфигурация приложения
│   │   ├── gunicorn_conf.py      # Настройки Gunicorn
│   │   └── logger_config.py      # Настройки логирования
│   ├── db/
│   │   └── postgres.py           # PostgreSQL подключение
│   ├── models/
│   │   └── example_model.py      # Модели данных
│   └── services/
│       └── example_service.py    # Бизнес-логика
├── main.py                       # Точка входа приложения
└── pyproject.toml               # Poetry зависимости
```


## Environment Variables

- `POSTGRES_HOST` - хост PostgreSQL (по умолчанию: billing-postgres)
- `POSTGRES_PORT` - порт PostgreSQL (по умолчанию: 5432)
- `POSTGRES_USER` - пользователь PostgreSQL (по умолчанию: postgres)
- `POSTGRES_PASSWORD` - пароль PostgreSQL (по умолчанию: postgres)
- `POSTGRES_DB` - название базы данных (по умолчанию: pg_db)
- `SERVER_HOST` - хост сервера (по умолчанию: 0.0.0.0)
- `SERVER_PORT` - порт сервера (по умолчанию: 8000)
- `KAFKA_BOOTSTRAP_SERVERS` - адреса брокеров Kafka (по умолчанию: kafka-0:9092)
- `KAFKA_TOPIC_BILLING_EVENTS` - топик для событий биллинга (по умолчанию: user-billing-events)
- `KAFKA_REQUEST_TIMEOUT_MS` - таймаут запроса к Kafka в мс (по умолчанию: 30000)
- `KAFKA_ENABLE_IDEMPOTENCE` - идемпотентность продюсера (по умолчанию: true)
- `KAFKA_ACKS` - уровень подтверждения записи (по умолчанию: all)

