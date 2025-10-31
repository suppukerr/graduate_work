# Ссылка на репозиторий:

## https://github.com/tr-nikolai/Auth_sprint_1

# Auth API — Сервис авторизации и управления ролями

Асинхронный сервис авторизации, регистрации пользователей и управления ролями, реализованный с использованием FastAPI, PostgreSQL, Alembic и Docker.
Проект разработан в рамках шестого спринта курса Яндекс.Практикум.

## Функциональность
- Регистрация и вход пользователя
- Смена пароля и логина
- Выход пользователя
- Проверка JWT-токена
- Управление ролями (создание, удаление, обновление)
- Назначение и удаление ролей у пользователей
- Получение всех ролей пользователя и всех пользователей с определённой ролью
- Асинхронная работа через async SQLAlchemy
- Документация в формате OpenAPI (Swagger)

## Технологии
- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- Docker, Docker Compose
- Pydantic
- Typer — для CLI-управления
- Uvicorn — ASGI-сервер

# Как запустить

## Клонируйте репозиторий
git clone https://github.com/tr-nikolai/Auth_sprint_1.git
cd Auth_sprint_1

## Запустите проект
docker-compose up --build
## Проект будет доступен по адресу:

http://localhost/docs#/ — Swagger UI

http://localhost/redoc — ReDoc

# Команды CLI (Typer)

## Создание суперпользователя:

docker-compose exec auth_api python cli.py create-superuser

## Примеры эндпоинтов

| Метод  | URL                                       | Назначение                                  |
| ------ | ----------------------------------------- | ------------------------------------------- |
| POST   | `/api/v1/auth/register`                   | Регистрация                                 |
| POST   | `/api/v1/auth/login`                      | Вход и получение JWT                        |
| POST   | `/api/v1/auth/logout`                     | Выход                                       |
| GET    | `/api/v1/auth/users/me`                   | Получить текущего пользователя              |
| POST   | `/api/v1/auth/change-password`            | Смена пароля                                |
| POST   | `/api/v1/auth/change-login`               | Смена логина                                |
| POST   | `/api/v1/roles/`                          | Создать роль                                |
| GET    | `/api/v1/roles/`                          | Получить все роли                           |
| DELETE | `/api/v1/roles/{role_id}`                 | Удалить роль                                |
| POST   | `/api/v1/user-roles/assign`               | Назначить роль пользователю                 |
| DELETE | `/api/v1/user-roles/remove`               | Удалить роль у пользователя                 |
| GET    | `/api/v1/user-roles/user/{user_id}/roles` | Получить роли пользователя                  |
| GET    | `/api/v1/user-roles/role/{role_id}/users` | Получить пользователей с определённой ролью |

## Стандартизация

Все сообщения и ошибки на русском языке

Коды ответов указаны с использованием status.HTTP_...

Ответы оформлены с помощью response_model

Все маршруты снабжены описаниями для Swagger

## Участники
- @lost-znahid
- @tr-nikolai
- @find-y

## Как создать суперпользователя через CLI

Для создания суперпользователя выполните команду:

```bash
python -m src.cli.cli create-superuser
```

Вас попросят ввести secret, username, email и пароль. Пользователь будет создан с максимальными правами и ролью 'superuser'.


