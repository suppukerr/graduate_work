from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

engine = None
async_session_maker = None


async def init_db():
    global engine, async_session_maker

    engine = create_async_engine(settings.postgres.async_database_url, echo=True)
    async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
