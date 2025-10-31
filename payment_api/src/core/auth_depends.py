from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from src.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    roles: List[str] = []
    exp: Optional[int] = None  # если нужна проверка на срок действия — опционально


async def get_current_user(token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token.credentials,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise credentials_exception

    if not token_data.sub:
        raise credentials_exception

    return token_data


async def get_user_roles_from_token(token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> List[str]:
    """
    Извлекает роли пользователя из JWT токена.
    Возвращает список ролей пользователя.
    """
    user_data = await get_current_user(token)
    return user_data.roles
