from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi import Query

from src.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    create_refresh_token,
    decode_and_validate_refresh_token,
)
from src.db.models.login_history import LoginHistoryRead
from src.db.models.user import User
from src.core.security import get_current_user
from src.schemas.token import Token, RefreshTokenRequest
from src.schemas.user import (
    UserCreate,
    UserLogin,
    ChangeCredentialsRequest,
    UserResponse,
    LogoutResponse,
)
from src.services.role_service import RoleService, get_role_service
from src.services.token_service import TokenService, get_token_service
from src.services.user_role_service import (UserRoleService,
                                            get_user_role_service)
from src.services.user_service import UserService, get_user_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя с логином, паролем и email.",
    responses={
        status.HTTP_409_CONFLICT: {"description": "Пользователь уже существует"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Ошибка валидации"},
    },
)
async def register_user_with_base_role(
        user_data: UserCreate,
        user_service: UserService = Depends(get_user_service),
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
):
    user = await user_service.create_user_with_base_role(
        user_data,
        role_service,
        user_role_service
    )
    return UserResponse(id=user.id,
                        username=user.username,
                        email=user.email
                        )
    # return {"id": user.id, "username": user.username, "email": user.email}


@router.post(
    "/login",
    response_model=Token,
    summary="Вход пользователя",
    description="Аутентификация по логину и паролю. Возвращает JWT токен.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Неверные логин или пароль"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Ошибка валидации"},
    },
)
async def login(
        user_data: UserLogin,
        request: Request,
        user_service: UserService = Depends(get_user_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
) -> Token:
    """
    Аутентификация пользователя: проверка логина и пароля,
    сохранение истории входа, генерация access и refresh токенов.
    """
    user = await user_service.get_by_username(user_data.username)
    if not user or not verify_password(user_data.password,
                                       user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные логин или пароль"
        )

    user_agent = request.headers.get("User-Agent") or "unknown"
    ip = request.client.host or "unknown"

    await user_service.create_login_history(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=user_agent,
    )

    user_role_names = [role.name for role in await user_role_service.get_user_roles(user.id)]
    access_token = create_access_token(
        {"sub": str(user.id),
         "roles": user_role_names})
    refresh_token = create_refresh_token(
        {"sub": user.username,
         "user_agent": request.headers.get("User-Agent"),
         "ip": ip,
         })

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.put(
    "/change-credentials",
    summary="Смена email или пароля",
    description="Позволяет сменить email или пароль текущего пользователя.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Неавторизованный пользователь"},
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
        status.HTTP_400_BAD_REQUEST: {"description": "Нет данных для обновления"},
    },
)
async def change_credentials(
        data: ChangeCredentialsRequest,
        current_user=Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_username(current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    update_data = {}

    if data.new_email:
        update_data["email"] = data.new_email

    if data.new_password:
        hashed = user_service.hash_password(data.new_password)
        update_data["hashed_password"] = hashed

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не указаны данные для обновления"
        )

    await user_service.update_user(user.username, update_data)

    return {"detail": "Данные успешно обновлены"}


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Выход пользователя",
    description="Завершение сессии пользователя. Добавляет refresh токен в блеклист.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Неавторизованный пользователь"},
        status.HTTP_200_OK: {"description": "Выход выполнен успешно"},
    },
)
async def logout(
        refresh_data: RefreshTokenRequest,
        current_user=Depends(get_current_user),
        token_service: TokenService = Depends(get_token_service),
) -> dict[str, str]:
    """
    Выход из системы.
    Добавляет refresh токен в блеклист.
    """
    token = refresh_data.refresh_token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Токен доступа не найден.")
    await token_service.invalidise_refresh_token(token)

    return LogoutResponse(detail="Успешный выход из системы.")


@router.get(
    "/login-history",
    response_model=list[LoginHistoryRead],
    summary="История входов",
    description="Получение истории входов текущего пользователя.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Неавторизованный пользователь"},
        status.HTTP_403_FORBIDDEN: {"description": "Доступ запрещен"},
    },
)
async def get_login_history(
        current_user=Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
        page_number: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await user_service.get_user_login_history(
        user_id=current_user.id,
        page_number=page_number,
        page_size=page_size
    )


@router.post("/refresh",
             response_model=Token)
async def refresh_token(
        request: Request,
        refresh_data: RefreshTokenRequest,
        token_service: TokenService = Depends(get_token_service),
) -> Token:
    """
    Обновляет access и refresh токены.

    Вызывает HTTPException,
    если токен недействителен, находится в черном списке
    или если User-Agent/IP не совпадают с сохраненными.
    """
    # 1. получить данные из запроса. для проверки и нового токена
    current_user_agent = request.headers.get("User-Agent") or "unknown"
    current_ip = request.client.host or "unknown"

    # 2. получить refresh_token
    refresh_token = refresh_data.refresh_token

    # 3. Получаем данные и валидируем по секрету и сроку жизни токена
    payload = decode_and_validate_refresh_token(refresh_token)

    # 4. Проверить по jti что токен не в блеклисте
    await token_service.check_in_blacklist(payload.get("jti"))

    # 5. Сравнить текущие IP и User-Agent с последним логином
    if current_user_agent != payload.get("user_agent"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Запрос с нового устройства. Для безопасности нужно еще раз залогиниться.")
    if current_ip != payload.get("ip"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подозрительное местоположение. Для безопасности нужно еще раз залогиниться.")

    # 6. Добавить jti токена в блеклист
    await token_service.invalidise_refresh_token(refresh_token)

    # 7. Создать новые access_token и refresh_token.
    access_token = create_access_token({"sub": payload.get("sub")})
    refresh_token = create_refresh_token({"sub": payload.get("sub"),
                                          "user_agent": current_user_agent,
                                          "ip": current_ip,
                                          })
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """
    Получение информации о текущем пользователе по JWT.
    Требуется передать заголовок Authorization: Bearer <token>
    """
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
    )