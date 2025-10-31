# src/db/test_session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

test_engine = create_async_engine(settings.postgres.async_database_url, echo=True)
test_session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

