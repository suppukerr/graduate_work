from functools import lru_cache
from typing import List

from fastapi import Depends
from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.role import Role, user_roles_table
from src.db.models.user import User
from src.db.session import get_db


class UserRoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Назначить роль пользователю"""
        # Проверяем, что пользователь и роль существуют
        user = await self.db.execute(select(User).where(User.id == user_id))
        role = await self.db.execute(select(Role).where(Role.id == role_id))

        if not user.scalar_one_or_none() or not role.scalar_one_or_none():
            return False

        # Проверяем, что роль уже не назначена
        existing = await self.db.execute(
            select(user_roles_table).where(
                user_roles_table.c.user_id == user_id,
                user_roles_table.c.role_id == role_id
            )
        )
        if existing.scalar_one_or_none():
            return True  # Роль уже назначена

        # Назначаем роль через insert
        stmt = insert(user_roles_table).values(user_id=user_id, role_id=role_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Удалить роль у пользователя"""
        stmt = delete(user_roles_table).where(
            user_roles_table.c.user_id == user_id,
            user_roles_table.c.role_id == role_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Получить все роли пользователя"""
        result = await self.db.execute(
            select(Role)
            .join(user_roles_table, Role.id == user_roles_table.c.role_id)
            .where(user_roles_table.c.user_id == user_id)
        )
        return result.scalars().all()

    async def get_users_with_role(self, role_id: str) -> List[User]:
        """Получить всех пользователей с определенной ролью"""
        result = await self.db.execute(
            select(User)
            .join(user_roles_table, User.id == user_roles_table.c.user_id)
            .where(user_roles_table.c.role_id == role_id)
        )
        return result.scalars().all()


@lru_cache
def get_user_role_service(db: AsyncSession = Depends(get_db)) -> UserRoleService:
    return UserRoleService(db)
