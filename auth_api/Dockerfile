FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Задаём рабочую директорию
WORKDIR /app

# Копируем только pyproject.toml и poetry.lock для кэширования слоёв
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости в отдельный слой
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with test

# Копируем остальной проект
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH="/app/src"

# Открываем порт
EXPOSE 8000

# Команда применяет миграции на бд и потом запускает приложение
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000

