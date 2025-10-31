import logging

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings, PROJECT_ROOT
from src.db.session import get_db
from src.main import app
from src.schemas.user import UserCreate
from src.services.user_service import UserService

logging.basicConfig(level=logging.DEBUG)
# from dotenv import load_dotenv

# load_dotenv(".env")


# Применение миграций перед запуском тестов
@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_ini_path = PROJECT_ROOT / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture()
async def async_session_maker():
    engine = create_async_engine(settings.postgres.async_database_url, echo=False)
    async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session_maker
    await engine.dispose()


# Фикстура очистки БД
@pytest_asyncio.fixture(autouse=True)
async def clear_tables(async_session_maker):
    async with async_session_maker() as session:
        await session.execute(text("TRUNCATE login_history, users, user_roles, roles RESTART IDENTITY CASCADE"))
        await session.commit()


# Универсальный override для get_db
@pytest_asyncio.fixture()
async def override_get_db(async_session_maker):
    async def _override():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# HTTP-клиент с замещением зависимостей
@pytest_asyncio.fixture()
async def client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# Пользователь и токен
@pytest_asyncio.fixture()
async def access_token(client: AsyncClient) -> str:
    await client.post("/api/v1/auth/signup", json={
        "username": "testuser",
        "email": "user@example.com",
        "password": "strongpassword",
    })
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "strongpassword"
    })
    assert login_response.status_code == 200, login_response.text
    tokens = login_response.json()
    return tokens["access_token"]


# Авторизованный клиент
@pytest_asyncio.fixture()
async def authorized_client(client: AsyncClient, access_token: str) -> AsyncClient:
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client


# Фикстура для суперпользователя и его токена
@pytest_asyncio.fixture()
async def superuser_token(async_session_maker, client: AsyncClient) -> str:
    username = "superuser"
    email = "superuser@example.com"
    password = "superpassword"
    async with async_session_maker() as session:
        user_service = UserService(session)

        superuser = await user_service.get_superuser()
        if not superuser:
            user_data = UserCreate(username=username, email=email, password=password)
            await user_service.create_user(user_data)
            await user_service.update_user(username, {"is_superuser": True})

    login_response = await client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login_response.status_code == 200, login_response.text
    tokens = login_response.json()
    return tokens["access_token"]


@pytest_asyncio.fixture()
async def superuser_client(client: AsyncClient, superuser_token: str) -> AsyncClient:
    client.headers = {"Authorization": f"Bearer {superuser_token}"}
    return client
