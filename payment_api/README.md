# Payment API

Сервис управления платежами.

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Gunicorn
- Docker, Docker Compose
- Youkassa SDK

## Запуск

1. Перейдите в директорию `payment_api`:
```bash
cd payment_api
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
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

## Проксирование API для получения вебхуков при локальном запуске

- установить Ngrok
- выполнить в терминале ngrok http 80
- прописать в настройках yookassa путь к публичной ручке https://yookassa.ru/my/merchant/integration/http-notifications (для этого нужен тест-аккаунт, и прописать в енв его SHOP_ID и SECRET_KEY)