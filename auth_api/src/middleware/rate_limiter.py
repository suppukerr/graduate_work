import hashlib
import time
import uuid

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings
from src.db.redis import get_redis


def generate_rate_limit_key(request: Request):
    # Получаем session_id из cookies
    session_id = request.cookies.get("session_id")

    # Получаем User-Agent
    user_agent = request.headers.get("user-agent", "unknown")

    # Получаем IP-адрес
    ip = request.client.host or "unknown"

    # Создаем строку для хеширования
    raw_key = f"session:{session_id}|ua:{user_agent}|ip:{ip}"

    # Хешируем строку для получения уникального ключа
    unique_key = hashlib.sha256(raw_key.encode()).hexdigest()

    # print(f"DEBUG: Generated unique key: {unique_key}")
    return unique_key


async def leaky_bucket_rate_limiter(key: str):
    current_time = time.time()
    redis_client = await get_redis()
    bucket = await redis_client.hgetall(key)

    if not bucket:
        # Если ведро не существует, создаем новое
        bucket = {'tokens': settings.rate_limit.rate_limit, 'last_checked': current_time}
    else:
        # Преобразуем байтовые строки в строки
        bucket = {k.decode('utf-8'): v.decode('utf-8') for k, v in bucket.items()}

        # Обновляем количество токенов в ведре
        elapsed_time = current_time - float(bucket['last_checked'])
        bucket['tokens'] = min(
            settings.rate_limit.rate_limit,
            float(bucket['tokens']) + elapsed_time * settings.rate_limit.leak_rate
        )
        bucket['last_checked'] = current_time

    if float(bucket['tokens']) < 1:
        # Если нет токенов, отклоняем запрос
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too Many Requests")

    # Уменьшаем количество токенов и сохраняем состояние ведра
    bucket['tokens'] -= 1
    await redis_client.hmset(key, bucket)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Проверяем наличие session_id в cookies
        session_id = request.cookies.get("session_id")
        response = await call_next(request)

        if not session_id:
            # Создаем новый session_id и сохраняем в cookies
            session_id = str(uuid.uuid4())
            response.set_cookie(key="session_id", value=session_id, httponly=True)

        try:
            # генерим уникальный ключ пользователя
            key = generate_rate_limit_key(request)
            await leaky_bucket_rate_limiter(key)
        except HTTPException as e:
            if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                return JSONResponse(status_code=429, content={"detail": "Слишком много запросов"})

        return response
