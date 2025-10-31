from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from .config import settings


# Синхронный движок для SQLAdmin
engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Асинхронный движок для приложения
async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db():
    """Получить синхронную сессию для SQLAdmin"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Получить асинхронную сессию"""
    async with AsyncSessionLocal() as session:
        yield session
