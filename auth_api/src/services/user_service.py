from functools import lru_cache
from uuid import UUID
import secrets
import string

from fastapi import Depends, status, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.login_history import LoginHistory
from src.db.models.user import User
from src.db.session import get_db
from src.schemas.user import UserCreate, UserResponse
from src.core.config import settings

from src.services.role_service import RoleService, RoleCreate
from src.services.user_role_service import UserRoleService
# from src.services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password)
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, username: str, update_data: dict) -> None:
        stmt = (
            update(User)
            .where(User.username == username)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        # print("В базе нашел по почте", result)
        return result.scalar_one_or_none()

    async def create_login_history(self, user_id: int, ip_address: str, user_agent: str) -> LoginHistory:
        history = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(history)
        await self.db.commit()
        return history

    async def get_user_login_history(
            self,
            user_id: UUID,
            page_number: int = 1,
            page_size: int = 10
    ) -> list[LoginHistory]:
        offset = (page_number - 1) * page_size

        query = select(LoginHistory).where(LoginHistory.user_id == user_id).order_by(
            LoginHistory.login_time.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        records = result.scalars().all()
        return records  # Возвращаем объекты ORM как есть

        # return [LoginHistory.model_validate(row) for row in records]

    async def get_superuser(self) -> User | None:
        result = await self.db.execute(select(User).where(User.is_superuser is True))
        return result.scalar_one_or_none()

    def hash_password(self, password: str) -> str:
        return get_password_hash(password)

    def generate_password(self, length: int = 16) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    async def create_user_with_base_role(
            self,
            user_data: UserCreate,
            role_service: RoleService,
            user_role_service: UserRoleService,
    ) -> UserResponse:
        existing = await self.get_by_username(user_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким логином уже существует"
            )

        # проверяем наличие роли USER / если нет то создаем
        role = await role_service.get_role_by_name(settings.api.base_role)
        if not role:
            role = await role_service.create_role(
                RoleCreate(name=settings.api.base_role,
                           description="Базовая роль пользователя")
            )

        # создаем пользователя
        user = await self.create_user(user_data)

        # назначаем роль пользователю
        result = await user_role_service.assign_role_to_user(user.id, role.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось назначить роль пользователю"
            )
        return user


@lru_cache
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)
