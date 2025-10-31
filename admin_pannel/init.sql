-- Инициализация базы данных для админ-панели
-- Создается автоматически при первом запуске PostgreSQL

-- Создание дополнительных пользователей (если нужно)
-- CREATE USER admin_readonly WITH PASSWORD 'readonly_pass';

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Настройки производительности
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Применить настройки
SELECT pg_reload_conf();