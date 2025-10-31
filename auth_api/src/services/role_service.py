from functools import lru_cache
from typing import List

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.role import Role
from src.db.session import get_db
from src.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role_data: RoleCreate) -> Role:
        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_all_roles(self) -> List[Role]:
        result = await self.db.execute(select(Role))
        return result.scalars().all()

    async def get_role_by_id(self, role_id: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def update_role(self, role_id: str, update_data: RoleUpdate) -> Role | None:
        role = await self.get_role_by_id(role_id)
        if not role:
            return None

        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.description is not None:
            update_dict["description"] = update_data.description

        if update_dict:
            stmt = (
                update(Role)
                .where(Role.id == role_id)
                .values(**update_dict)
                .execution_options(synchronize_session="fetch")
            )
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(role)

        return role

    async def delete_role(self, role_id: str) -> bool:
        role = await self.get_role_by_id(role_id)
        if not role:
            return False

        stmt = delete(Role).where(Role.id == role_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True


@lru_cache
def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db)
