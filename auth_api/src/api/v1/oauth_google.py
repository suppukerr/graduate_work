import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from httpx import HTTPStatusError
from sqlalchemy.exc import SQLAlchemyError

from src.core.security import (
    create_access_token,
    create_refresh_token,
)
from src.schemas.user import UserCreate
from src.schemas.token import Token

from src.services.role_service import RoleService, get_role_service
from src.services.user_role_service import (UserRoleService,
                                            get_user_role_service)
from src.services.user_service import UserService, get_user_service
from src.services.oauth_google import GoogleOAuthService, get_oauth_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/redirect")
def redirect_to_google_oauth(
    oauth_service: GoogleOAuthService = Depends(get_oauth_service),
) -> RedirectResponse:
    """
    Генерация и редирект на OAuth-ссылку Google
    """
    uri = oauth_service.generate_redirect_uri()
    return RedirectResponse(url=uri, status_code=302)


@router.get("/callback")
async def handle_google_oauth_callback(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
    oauth_service: GoogleOAuthService = Depends(get_oauth_service),
) -> Token:
    """
    Обработка callback-а после авторизации через Google:
    - получение access token
    - получение email
    - создание пользователя (если его нет)
    - логин и возврат JWT
    """

    try:
        # 1. Получаем код из квера урла
        error = request.query_params.get("error")
        code = request.query_params.get("code")

        if error:
            logger.error("Ошибка авторизации:", error)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ошибка авторизации")
        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ошибка авторизации.")

        # 2. Получаем по код гугл аксесс токен
        google_access_token = await oauth_service.get_access_token(code)

        # 3. Получаем по гугл аксесс токену данные юзера
        user_info = await oauth_service.get_user_info(google_access_token)
        user_email = user_info["email"]

        # 4. Запрос в бд. Проверяем, есть ли юзер с такой почтой
        user = await user_service.get_by_email(user_email)

        # 5. Если нет - создаем юзера. передаем почту и рандомный пароль.
        if not user:
            password = user_service.generate_password()
            user_data = UserCreate(
                username=user_email.split("@")[0],
                email=user_email,
                password=password
            )
            user = await user_service.create_user_with_base_role(
                                                    user_data,
                                                    role_service,
                                                    user_role_service,
                                                    )

        # 6. Записываем вход в логин хистори
        user_agent = request.headers.get("User-Agent") or "unknown"
        ip = request.client.host or "unknown"

        await user_service.create_login_history(
            user_id=user.id,
            ip_address=ip,
            user_agent=user_agent,
        )

        # 5. Логиним, получаем токены. Отдаем юзеру.
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token(
            {"sub": user.username,
             "user_agent": user_agent,
             "ip": ip,
             })

        return Token(access_token=access_token, refresh_token=refresh_token)

    except HTTPStatusError as e:
        logger.error("Ошибка при обращении к Google API: %s - %s",
                     e.response.status_code,
                     e.response.text)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Сервер временно недоступен. Попробуйте позже."
        )

    except SQLAlchemyError as e:
        logger.exception("Ошибка базы данных при Google OAuth:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Сервер временно недоступен. Попробуйте позже."
        )

    except Exception as e:
        logger.exception("Ошибка во время обработки Google OAuth:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Сервер временно недоступен. Попробуйте позже."
        )
