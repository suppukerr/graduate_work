FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Конфигурация Poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --only=main

# Копирование исходного кода
COPY . .

# Копирование и настройка entrypoint скрипта
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Создание пользователя для запуска приложения
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Entrypoint для миграций и запуска
ENTRYPOINT ["/entrypoint.sh"]

# Команда запуска
CMD ["python", "main.py"]