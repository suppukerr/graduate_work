import logging
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from yookassa.domain.exceptions import ApiError

from src.api.v1.heath import router as health_router
from src.api.v1.youkassa import router as youkassa_router
from src.core.config import settings
from src.db import postgres
from src.db.postgres import Base
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
    postgres.async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("Application started")

    yield

    await engine.dispose()

    logger.info("Application shutdown completed")


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
app.include_router(youkassa_router)

# обработчики
app.add_exception_handler(httpx.TimeoutException, exceptions.timeout_exception_handler)
app.add_exception_handler(ApiError, exceptions.youkassa_api_error_handler)
app.add_exception_handler(HTTPException, exceptions.http_exception_handler)
app.add_exception_handler(Exception, exceptions.general_exception_handler)
