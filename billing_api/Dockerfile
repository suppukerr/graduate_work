FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry==1.7.1

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

EXPOSE 8000

# Команда ожидает PostgreSQL и запускает приложение
CMD while ! nc -z ${POSTGRES_HOST:-billing-postgres} ${POSTGRES_PORT:-5432}; do sleep 1; done && \
    echo "PostgreSQL is ready!" && \
    exec gunicorn main:app --config ./src/core/gunicorn_conf.py

