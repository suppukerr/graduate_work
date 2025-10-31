import logging
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.v1.heath import router as health_router
from src.api.v1.user_subscription import router as user_subscription_router
from src.core.config import settings
from src.db import postgres
from src.db.postgres import Base
from src.services.kafka import kafka_service
from src import exceptions

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""

    engine = create_async_engine(
        url=settings.postgres.ASYNC_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Подключение к Kafka
    await kafka_service.connect()

    # + создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created")

    logger.info(f"Приложение {settings.project_name.upper()} запущено!")

    yield

    # Отключение от Kafka
    await kafka_service.disconnect()
    await engine.dispose()

    logger.info(f"Приложение {settings.project_name.upper()} выключено!")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(health_router)
app.include_router(user_subscription_router)


# обработчики
app.add_exception_handler(httpx.TimeoutException, exceptions.timeout_exception_handler)
app.add_exception_handler(exceptions.HandledHTTPException, exceptions.handled_http_exception_handler)
app.add_exception_handler(HTTPException, exceptions.http_exception_handler)
app.add_exception_handler(Exception, exceptions.general_exception_handler)
