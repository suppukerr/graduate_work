import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.services.user_service import get_user_service, UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt.expire_access_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt.secret_access,
                      algorithm=settings.jwt.algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt.expire_refresh_days)
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),  # уникальный ID токена
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(to_encode,
                      settings.jwt.secret_refresh,
                      algorithm=settings.jwt.algorithm)


def decode_and_validate_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt.secret_refresh,
                             algorithms=[settings.jwt.algorithm])
        required_keys = ["jti", "sub", "ip", "user_agent"]
        if not all(payload.get(key) for key in required_keys):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Refresh-токен не содержит необходимые поля.")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Токен не проходил валидацию.")


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        user_service: UserService = Depends(get_user_service),
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,
                             settings.jwt.secret_access,
                             algorithms=[settings.jwt.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_by_user_id(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_superuser_user(current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас не достаточно прав"
        )
    return current_user
