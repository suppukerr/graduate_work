from functools import lru_cache
from datetime import timedelta

from fastapi import Depends, HTTPException, status, Request
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.db.session import get_db
from src.db.redis import get_redis
from src.core.config import settings
from src.core.security import decode_and_validate_refresh_token


class TokenService:
    def __init__(
            self,
            db: AsyncSession,
            redis: Redis,
    ):
        self.db = db
        self.redis = redis

    async def invalidise_refresh_token(self, token: str) -> None:
        "Добавить токен в блеклист"
        payload = decode_and_validate_refresh_token(token)
        jti = payload.get("jti")
        key = f"blacklist:{jti}"

        ttl = int(timedelta(
            days=settings.jwt.expire_refresh_days).total_seconds())

        await self.redis.setex(key, ttl, "1")

    async def check_in_blacklist(self, jti: str) -> None:
        "Поднять исключение, если то токен в блеклисте"
        is_blacklisted = await self.redis.get(f"blacklist:{jti}")
        if is_blacklisted:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Токен в блеклисте")


@lru_cache
def get_token_service(
    db: AsyncSession = Depends(get_db),  # пока не используется
    redis: Redis = Depends(get_redis),
) -> TokenService:
    return TokenService(db, redis)
