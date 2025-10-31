# Инструкция по развертыванию

## Архитектура деплоя

Проект состоит из независимых микросервисов и общей инфраструктуры:

```
infra/                        # Общая инфраструктура (Kafka)
├── docker-compose.yml
├── .env
└── README.md

auth_api/
├── docker-compose.yml
├── Dockerfile
└── nginx.conf

billing_api/
├── docker-compose.yml
├── Dockerfile
└── entrypoint.sh

admin_pannel/                # Admin панель
├── docker-compose.yml
├── Dockerfile
└── nginx.conf
```

**Принципы:**
- Общая инфраструктура (Kafka) деплоится отдельно и используется всеми сервисами
- Каждый сервис имеет свою изолированную Docker сеть
- Сервисы подключаются к общей сети Kafka для event-driven коммуникации
- Все файлы для деплоя (Dockerfile, docker-compose.yml) находятся в корне каждого проекта
- `.env` файлы находятся в корне соответствующего проекта

## Быстрый старт всех сервисов

```bash
# Запустить всю инфраструктуру и сервисы одной командой
make all-up

# Остановить все
make all-down
```

**После запуска доступны URL:**
- Auth API: http://localhost:8000
- Billing API: http://localhost:8001  
- Admin Panel (nginx): http://localhost:8015 ⭐ **рекомендуется**
- Admin Panel (direct): http://localhost:8003
- Kafka UI: http://localhost:8080

## Запуск отдельных сервисов

### 1. Infrastructure (Kafka) - обязательно запустить первым

```bash
# Через Makefile (рекомендуется)
make infra-up

# Или напрямую
cd infra
docker-compose up -d
```

**Что включает:**
- Kafka broker (KRaft mode, без Zookeeper)
- Kafka UI (порт 8080) - веб-интерфейс для мониторинга

**Сеть:** `shared_infra` - используется всеми микросервисами

### 2. Auth Service

```bash
# Через Makefile (рекомендуется)
make auth-up

# Или напрямую
cd auth_api
docker-compose up -d
```

**Что включает:**
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- Auth API (внутренний порт 8000)
- Nginx (порт 8000) - reverse proxy для Auth API
- Kafka Consumer (слушает события подписки/отписки)

**Зависимости:**
- Требуется запущенная инфраструктура (Kafka)

### 3. Billing Service

```bash
# Через Makefile (рекомендуется)
make billing-up

# Или напрямую
cd billing_api
docker-compose up -d
```

**Что включает:**
- PostgreSQL (порт 5433)
- Billing API (внутренний порт 8000)
- Nginx (порт 8001) - reverse proxy для Billing API

## Environment Variables

### Auth Service
Создайте `.env` файл в `auth_api/.env`:
```env
AUTH_POSTGRES_USER=auth_user
AUTH_POSTGRES_PASSWORD=auth_pass
AUTH_POSTGRES_DB=auth_db
```

### Billing Service
Создайте `.env` файл в `billing_api/.env`:
```env
POSTGRES_USER=billing_user
POSTGRES_PASSWORD=billing_pass
POSTGRES_DB=billing_db
```

### Admin Panel
Создайте `.env` файл в `admin_pannel/.env`:
```env
# Database settings  
POSTGRES_HOST=billing_postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=pg_db

# Auth database settings (for user info)
AUTH_POSTGRES_HOST=host.docker.internal
AUTH_POSTGRES_PORT=5435
AUTH_POSTGRES_USER=auth_user
AUTH_POSTGRES_PASSWORD=auth_pass
AUTH_POSTGRES_DB=auth_db

# Admin settings
ADMIN_SECRET_KEY=your-very-secret-key
ADMIN_TITLE=Billing Admin Panel
```

## Порты и взаимодействие

| Сервис | Порт | Описание |
|--------|------|----------|
| **Infrastructure** | | |
| Kafka | 9094 | External listener (localhost) |
| Kafka | - | Internal listener `kafka-0:9092` (внутри Docker) |
| Kafka UI | 8080 | Веб-интерфейс для мониторинга Kafka |
| **Auth Service** | | |
| Auth Nginx | 8000 | Reverse proxy для Auth API |
| Auth API | - | FastAPI приложение (только внутри docker сети) |
| Auth PostgreSQL | 5432 | База данных Auth |
| Auth Redis | 6379 | Кеш и сессии |
| **Billing Service** | | |
| Billing Nginx | 8001 | Reverse proxy для Billing API |
| Billing API | - | FastAPI приложение (только внутри docker сети) |
| Billing PostgreSQL | 5433 | База данных Billing |
| **Admin Panel** | | |
| Admin Nginx | 8015 | Reverse proxy для Admin Panel |
| Admin Panel | 8003 | FastAPI приложение (прямой доступ) |
| Admin Panel (internal) | 8002 | Внутренний порт приложения |

**Взаимодействие между сервисами:**
- Billing может обращаться к Auth по `http://host.docker.internal:8000` (через nginx) или напрямую к API по имени сервиса внутри сети
- Auth может обращаться к Billing по `http://host.docker.internal:8001` (через nginx) или напрямую к API по имени сервиса внутри сети
- Внутри docker сети сервисы доступны по именам: `auth-api:8000` и `billing-api:8000`

## Команды управления через Makefile

### Все сервисы
```bash
make all-up       # Запустить инфраструктуру + все сервисы
make all-down     # Остановить все
```

### Infrastructure
```bash
make infra-up       # Запустить Kafka
make infra-down     # Остановить Kafka
make infra-logs     # Логи Kafka
make infra-clean    # Удалить контейнеры и volumes
```

### Auth Service
```bash
make auth-up        # Запустить
make auth-down      # Остановить
make auth-logs      # Логи
make auth-build     # Пересобрать и запустить
make auth-clean     # Удалить контейнеры и volumes
```

### Billing Service
```bash
make billing-up     # Запустить
make billing-down   # Остановить
make billing-logs   # Логи
make billing-build  # Пересобрать и запустить
make billing-clean  # Удалить контейнеры и volumes
```

### Admin Panel
```bash
make admin-up       # Запустить
make admin-down     # Остановить
make admin-logs     # Логи
make admin-build    # Пересобрать и запустить
make admin-clean    # Удалить контейнеры и volumes
```

## Структура файлов

```
project/
├── infra/                 # Общая инфраструктура
│   ├── docker-compose.yml # Kafka конфигурация
│   ├── .env              # Переменные окружения
│   ├── Makefile          # Утилиты для работы с Kafka
│   └── README.md         # Документация
├── auth_api/              # Auth сервис
│   ├── src/               # Исходный код
│   ├── docker-compose.yml # Docker конфигурация
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── pyproject.toml
│   └── .env              # Переменные окружения
├── billing_api/          # Billing сервис
│   ├── src/               # Исходный код
│   ├── docker-compose.yml # Docker конфигурация
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── pyproject.toml
│   └── .env              # Переменные окружения
├── admin_pannel/         # Admin панель
│   ├── src/               # Исходный код
│   ├── docker-compose.yml # Docker конфигурация
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── pyproject.toml
│   └── .env              # Переменные окружения
```

## Troubleshooting

### Проверка статуса контейнеров
```bash
docker ps -a | grep kafka
docker ps -a | grep auth
docker ps -a | grep billing
docker ps -a | grep admin
```

### Просмотр логов
```bash
# Infrastructure
docker logs -f kafka_broker
docker logs -f kafka_ui

# Services
docker logs -f auth_api
docker logs -f billing_api
docker logs -f admin_panel
docker logs -f auth_postgres
docker logs -f billing_postgres
```

### Проверка Kafka
```bash
# Список топиков
cd infra && make topic-list

# Чтение сообщений из топика
cd infra && make topic-consume TOPIC=user-billing-events

# Мониторинг через UI
open http://localhost:8080
```

### Конфликт портов
Если порты заняты, измените их в соответствующих docker-compose файлах:
- `auth_api/docker-compose.yml`
- `billing_api/docker-compose.yml`
- `admin_pannel/docker-compose.yml`

### Пересоздание контейнеров
```bash
# Infrastructure
make infra-clean
make infra-up

# Auth
make auth-clean
make auth-up

# Billing
make billing-clean
make billing-up
```

## Production Ready

Для production окружения:

1. **Секреты**: Используйте `.env` файлы с настоящими секретами (не коммитьте!)
2. **Kafka**: 
   - Увеличьте replication factor до 3
   - Настройте Kafka в режиме кластера (3+ брокера)
   - Включите SSL/TLS для коммуникации
3. **Nginx**: Настроен для Auth и Billing, добавьте SSL сертификаты
4. **Мониторинг**: 
   - Prometheus/Grafana для метрик
   - Kafka UI для мониторинга топиков
5. **Backup**: Настройте автоматический backup для PostgreSQL
6. **SSL**: Настройте SSL сертификаты для nginx
7. **Логирование**: Централизованное логирование (ELK, Loki)
8. **Kafka Topics**: Предсоздайте топики с правильными настройками партиций и retention

## Порядок запуска в production

```bash
# 1. Запустить инфраструктуру
make infra-up

# 2. Проверить Kafka
docker logs kafka_broker
curl http://localhost:8080  # Kafka UI

# 3. Запустить сервисы
make auth-up
make billing-up
make admin-up

# 4. Проверить работоспособность
curl http://localhost:8000/api/v1/auth/docs
curl http://localhost:8001/api/v1/billing/docs
curl http://localhost:8003/health  # Admin Panel (direct)
curl http://localhost:8015/health  # Admin Panel (nginx)
```
