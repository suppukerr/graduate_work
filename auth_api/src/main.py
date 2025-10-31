import asyncio
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter, Request
from starlette.middleware.sessions import SessionMiddleware
from redis.asyncio import Redis
import httpx

from src.api.v1 import auth, roles, user_roles, oauth_yandex, oauth_google
from src.core.config import settings
from src.core.tracing import setup_tracing
from src.db import redis
from src.db.init import init_db
from src.middleware.rate_limiter import RateLimiterMiddleware
from src.services.kafka_consumer import start_kafka_consumer, stop_kafka_consumer

healthcheck_route = APIRouter()


@healthcheck_route.get("/healthcheck")
def health_check() -> dict:
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.testing:
        await init_db()

    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)

    app.state.http_client = httpx.AsyncClient()

    # Запускаем Kafka consumer в фоновой задаче
    kafka_task = asyncio.create_task(start_kafka_consumer())

    try:
        yield
    finally:
        await stop_kafka_consumer()
        kafka_task.cancel()
        try:
            await kafka_task
        except asyncio.CancelledError:
            pass
        await app.state.http_client.aclose()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/v1/auth/docs",
    redoc_url="/api/v1/auth/redoc",
    openapi_url="/api/v1/auth/openapi.json",
)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        request_id = str(uuid.uuid4())

    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response

if settings.enable_tracing:
    setup_tracing(app)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(oauth_yandex.router, prefix="/api/v1/auth/yandex", tags=["Oauth_Yandex"])
app.include_router(oauth_google.router, prefix="/api/v1/auth/google", tags=["Oauth_Google"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(user_roles.router, prefix="/api/v1/user-roles", tags=["UserRoles"])
app.include_router(healthcheck_route)

# Сначала добавляем наш middleware (будет выполняться последним)
app.add_middleware(RateLimiterMiddleware)

# Затем SessionMiddleware (будет выполняться первым)
app.add_middleware(
    SessionMiddleware,
    secret_key="your-super-secret-key",
    max_age=3600,  # 1 час
    same_site="lax"
)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=True
    )
