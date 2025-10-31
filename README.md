# Проектная работа: диплом
Ссылка на проект github - https://github.com/tr-nikolai/graduate_work

### Возможности приложения:
- Пользователь может выбирать тарифный план 
- Пользователь может ввести карту и сохранить ее для дальнейшей подписки 
- Карта обязана храниться в зашифрованном виде 
- Пользователю гарантируется единоразовое списание
- Админ имеет возможность добавить или отменить подписку в SQLAdmin

### Гарантии безопасности
- Данные карт пользователей не хранятся в БД, на сервисе хранятся только платёжный токен и маска карты (соблюдение PCI DSS стандарта для нее не требуется);
- Хранение персональных данных регламентируется Приказом ФСТЭК России № 21 от 18.02.2013;
- Вход в SQLAdmin осуществляется через Auth_service;
- Каждое списание должно иметь уникальный идентификатор (idempotency key). Это дает защиту от повторов;
- Детальное логирование на случай споров и неучтенных ошибок;

## Микросервисная архитектура

Проект состоит из независимых микросервисов:
- **Infra** - общая инфраструктура (Kafka)
- **Auth API** - аутентификация и авторизация пользователей
- **Billing API** - биллинговая система
- **Admin Panel** - административная панель

## Быстрый старт

```bash
# 1. Сначала запустить инфраструктуру (Kafka)
cd infra
docker-compose up -d
cd ..

# 2. Запустить Auth сервис
make auth-up

# 3. Запустить Billing сервис
make billing-up
или вручную 
cd billing_api
docker-compose up -d
poetry run alembic upgrade head
cd ..

# 4. Запустить админ-панель
make admin-up

# 5. Запустить Payment сервис
или вручную 
cd payment_api
docker-compose up -d
poetry run alembic upgrade head
cd ..

# Просмотр логов
make auth-logs
make billing-logs
```

**Документация:**
- [DEPLOY.md](DEPLOY.md) - Подробная инструкция по развертыванию
- [MIGRATION.md](MIGRATION.md) - Инструкция по миграции на централизованную Kafka

## Сервисы будут доступны

- **Auth API**: http://localhost/api/v1/auth/docs (через Nginx)
- **Billing API**: http://localhost/api/v1/billing/docs (через Nginx)
- **Payment API**: http://localhost/api/v1/payment/docs (через Nginx)
- **Admin Panel**: http://localhost/admin/ (через Nginx)
- **Kafka UI**: http://localhost:8080 (мониторинг Kafka)
- **Admin**: http://localhost/admin/

## Структура проекта

```
├── infra/                 # Общая инфраструктура (Kafka, мониторинг)
├── auth_api/              # Auth микросервис (с docker-compose.yml, Dockerfile)
├── billing_api/           # Billing микросервис (с docker-compose.yml, Dockerfile)
├── payment_api/           # Payment микросервис (с docker-compose.yml, Dockerfile)
└── admin_pannel/          # Admin панель
```
