#!/bin/bash
set -e

echo "🔄 Ожидание готовности PostgreSQL..."

# Ждем готовности PostgreSQL
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    echo "⏳ PostgreSQL недоступен - ожидание..."
    sleep 2
done

echo "✅ PostgreSQL готов!"

echo "🗃️ Запуск миграций..."
alembic upgrade head

echo "🚀 Запуск приложения..."
exec "$@"