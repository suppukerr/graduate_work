# Admin Panel README

## Описание

Админ-панель для управления биллинговой системой, построенная на FastAPI и SQLAdmin.

## Возможности

- Управление подписками (Subscriptions)
- Управление пользовательскими подписками (User Subscriptions)
- Управление платежами (Payments)
- Управление возвратами (Refunds)
- Веб-интерфейс с аутентификацией
- Поиск и фильтрация данных
- Экспорт данных
- Собственная PostgreSQL база данных

## Быстрый старт

### Через Docker (рекомендуется)

1. Скопируйте файл с переменными окружения:
```bash
cp .env.example .env
```

2. Настройте переменные в `.env` файле

3. Запустите через docker-compose:
```bash
docker-compose up -d
```

4. Откройте браузер: http://localhost:8003

### Локально

1. Установите зависимости:
```bash
poetry install
```

2. Скопируйте и настройте `.env`:
```bash
cp .env.example .env
```

3. Запустите приложение:
```bash
poetry run python main.py
```

## Аутентификация

Админ-панель интегрирована с Auth API для аутентификации пользователей.

### Как это работает

1. При входе в админку логин/пароль отправляются в Auth API
2. Auth API проверяет учетные данные и возвращает JWT токен
3. Токен сохраняется в сессии и используется для последующих запросов
4. Только пользователи с флагом `is_superuser=True` могут получить доступ к админке

### Требования

- Auth API должен быть запущен и доступен
- Пользователь должен существовать в Auth API
- Пользователь должен иметь права superuser

### Создание superuser

Для создания superuser используйте CLI в Auth API:

```bash
# Войдите в контейнер auth-api
docker exec -it auth_api bash

# Создайте superuser (потребуется CLI секрет из настроек auth_api)
python -m src.cli.cli create-superuser
# Введите:
# - secret_code: секрет из переменной CLI__SECRET в auth_api
# - username: admin
# - email: admin@example.com
# - password: ваш_сильный_пароль
```

Или без интерактивного режима:
```bash
python -m src.cli.cli create-superuser \
  --secret-code YOUR_CLI_SECRET \
  --username admin \
  --email admin@example.com \
  --password admin123
```

**ВАЖНО**: 
- Измените пароль в production!
- Только один superuser может существовать в системе

## Структура

```
admin_pannel/
├── src/
│   ├── admin/           # Админские представления
│   ├── core/            # Конфигурация и база данных
│   └── models/          # Модели данных
├── alembic/             # Миграции базы данных
├── main.py              # Точка входа
├── docker-compose.yml   # Docker конфигурация (с PostgreSQL)
├── Dockerfile          # Docker образ
├── nginx.conf          # Nginx конфигурация
├── init.sql            # Инициализация БД
└── admin.sh            # Скрипт управления
```

## API Endpoints

- `/` - Перенаправление на админку
- `/admin` - Главная страница админки
- `/health` - Проверка здоровья сервиса

## Конфигурация

Основные переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| POSTGRES_HOST | Хост PostgreSQL | localhost |
| POSTGRES_PORT | Порт PostgreSQL | 5433 |
| POSTGRES_USER | Пользователь БД | billing_user |
| POSTGRES_PASSWORD | Пароль БД | billing_pass |
| POSTGRES_DB | Имя БД | billing_db |
| ADMIN_SECRET_KEY | Секретный ключ для сессий | (изменить!) |
| AUTH_API_URL | URL Auth API | http://localhost:8000 |
| HOST | Хост приложения | 0.0.0.0 |
| PORT | Порт приложения | 8002 |

## Безопасность

В production:

1. Измените `ADMIN_SECRET_KEY` на криптографически стойкий ключ
2. Используйте HTTPS для всех соединений
3. Ограничьте доступ к админке через firewall/VPN
4. Настройте мониторинг и алертинг
5. Регулярно обновляйте зависимости
6. Используйте сильные пароли для superuser аккаунтов
7. Настройте rate limiting на уровне NGINX

## Разработка

Для разработки с автоперезагрузкой:

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

## База данных

Админка использует собственную PostgreSQL базу данных:

- **Порт**: 5434 (чтобы не конфликтовать с другими сервисами)
- **Миграции**: Автоматически применяются при запуске
- **Инициализация**: Через init.sql файл
- **Доступ**: `docker-compose exec postgres psql -U billing_user -d billing_db`

### Миграции

```bash
# Создать новую миграцию
poetry run alembic revision --autogenerate -m "описание"

# Применить миграции
poetry run alembic upgrade head

# Откатить миграцию
poetry run alembic downgrade -1
```

## Мониторинг

Проверка здоровья:
```bash
curl http://localhost:8002/health
```

Логи контейнера:
```bash
docker logs -f admin_panel
```