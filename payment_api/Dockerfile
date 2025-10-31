FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir "poetry>=1.8.2"

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Настраиваем Poetry для работы в Docker
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --without dev --no-interaction --no-ansi

# Копируем код приложения
COPY . .

COPY alembic/ ./alembic/
COPY alembic.ini ./

# EXPOSE 8002

# Команда ожидает PostgreSQL и запускает приложение
CMD while ! nc -z ${POSTGRES_HOST:-payment-postgres} ${POSTGRES_PORT:-5432}; do sleep 1; done && \
    echo "PostgreSQL is ready!" && \
    exec gunicorn main:app --config ./src/core/gunicorn_conf.py

#     exec uvicorn main:app --host 0.0.0.0 --port 8002 --reload --log-level info
# # Запуск напрямую через Uvicorn, print() и logging будут сразу в stdout
