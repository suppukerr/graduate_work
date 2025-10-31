import logging
import sys

import httpx
from fastapi import FastAPI
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from src.core.database import engine
from src.core.config import settings

# Настройка логирования для вывода в stdout (для Docker)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    """Аутентификация для админки через Auth API"""

    async def login(self, request: Request) -> bool:
        """
        Авторизация пользователя через Auth API.
        Отправляет логин/пароль в auth_api и сохраняет access_token в сессии.
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        try:
            # Отправка запроса на авторизацию в auth_api
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.auth_api_url}/api/v1/auth/login",
                    json={"username": username, "password": password}
                )

                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("access_token")
                    refresh_token = data.get("refresh_token")

                    if access_token and refresh_token:
                        # Проверяем, что пользователь является superuser
                        user_info = await self._get_user_info(access_token)
                        if user_info and user_info.get("is_superuser"):
                            request.session.update({
                                "access_token": access_token,
                                "refresh_token": refresh_token,
                                "username": username
                            })
                            logger.info(f"Успешный вход в админку для пользователя: {username}")
                            return True
                        else:
                            logger.warning(f"Пользователь {username} не является суперпользователем")
                            return False

                logger.warning(f"Неудачная попытка входа для пользователя: {username}")
                return False
        except httpx.RequestError as e:
            logger.error(f"Ошибка подключения к auth API: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при входе: {e}")
            return False

    async def logout(self, request: Request) -> bool:
        """
        Выход пользователя.
        Вызывает logout в auth_api для корректного завершения сессии,
        затем очищает локальную сессию.
        """
        access_token = request.session.get("access_token")
        refresh_token = request.session.get("refresh_token")

        if access_token and refresh_token:
            try:
                # Вызываем logout в auth_api с refresh_token в теле запроса
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{settings.auth_api_url}/api/v1/auth/logout",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json={"refresh_token": refresh_token}
                    )

                    if response.status_code == 200:
                        logger.info("Успешный выход из auth API")
                    else:
                        logger.warning(f"Ошибка при выходе из auth API: статус {response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Ошибка при вызове logout в auth API: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при выходе: {e}")

        # Очищаем локальную сессию в любом случае
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Проверка аутентификации пользователя.
        Проверяет access_token через auth_api эндпоинт /me.
        """
        access_token = request.session.get("access_token")

        if not access_token:
            return False

        user_info = await self._get_user_info(access_token)

        # Проверяем что пользователь активен и является superuser
        if user_info and user_info.get("is_active") and user_info.get("is_superuser"):
            return True

        # Если токен невалиден или пользователь не superuser - очищаем сессию
        request.session.clear()
        return False

    async def _get_user_info(self, access_token: str) -> dict | None:
        """
        Получение информации о пользователе из auth_api.
        Возвращает данные пользователя или None при ошибке.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{settings.auth_api_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Не удалось получить информацию о пользователе: {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"Ошибка подключения к auth API: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении информации о пользователе: {e}")
            return None


def create_app() -> FastAPI:
    """Создать FastAPI приложение с админкой"""

    app = FastAPI(
        title=settings.admin_title,
        description="Admin panel for billing system management",
        version="1.0.0"
    )

    # Добавляем SessionMiddleware для работы с сессиями
    app.add_middleware(SessionMiddleware, secret_key=settings.admin_secret_key)

    # Настройка SQLAdmin с аутентификацией
    authentication_backend = AdminAuth(secret_key=settings.admin_secret_key)

    # Создание и настройка админки
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title=settings.admin_title,
    )

    # Регистрация админских представлений
    from src.admin.billing_admin import (
        SubscriptionAdmin,
        UserSubscriptionAdmin,
        PaymentAdmin,
        RefundAdmin
    )

    admin.add_view(SubscriptionAdmin)
    admin.add_view(UserSubscriptionAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(RefundAdmin)

    @app.get("/")
    async def root():
        """Перенаправление на админку"""
        return RedirectResponse(url="/admin")

    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервиса"""
        return {"status": "healthy", "service": "admin-panel"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
