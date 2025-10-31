from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.schemas.role import RoleCreate, RoleRead, RoleUpdate
from src.services.role_service import RoleService, get_role_service
from src.core.security import get_superuser_user

router = APIRouter(dependencies=[Depends(get_superuser_user)])


@router.post(
    "/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой роли",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Роль с таким именем уже существует",
            "content": {"application/json": {"example": {"detail": "Роль с таким именем уже существует"}}},
        },
    },
)
async def create_role(
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service)
):
    existing_role = await role_service.get_role_by_name(role_data.name)
    if existing_role:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Роль с таким именем уже существует")

    role = await role_service.create_role(role_data)
    return RoleRead(id=role.id, name=role.name, description=role.description)


@router.get(
    "/",
    response_model=List[RoleRead],
    summary="Получить список всех ролей",
)
async def get_all_roles(
    role_service: RoleService = Depends(get_role_service)
):
    roles = await role_service.get_all_roles()
    return [RoleRead(id=role.id, name=role.name, description=role.description) for role in roles]


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    summary="Получить роль по ID",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Роль не найдена",
            "content": {"application/json": {"example": {"detail": "Роль не найдена"}}},
        },
    },
)
async def get_role(
    role_id: str,
    role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Роль не найдена")

    return RoleRead(id=role.id, name=role.name, description=role.description)


@router.put(
    "/{role_id}",
    response_model=RoleRead,
    summary="Обновить данные роли",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Роль не найдена",
            "content": {"application/json": {"example": {"detail": "Роль не найдена"}}},
        },
        status.HTTP_409_CONFLICT: {
            "description": "Роль с таким именем уже существует",
            "content": {"application/json": {"example": {"detail": "Роль с таким именем уже существует"}}},
        },
    },
)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    role_service: RoleService = Depends(get_role_service)
):
    existing_role = await role_service.get_role_by_id(role_id)
    if not existing_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Роль не найдена")

    if role_data.name and role_data.name != existing_role.name:
        name_exists = await role_service.get_role_by_name(role_data.name)
        if name_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Роль с таким именем уже существует")

    updated_role = await role_service.update_role(role_id, role_data)
    if not updated_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Роль не найдена")

    return RoleRead(id=updated_role.id, name=updated_role.name, description=updated_role.description)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить роль по ID",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Роль не найдена",
            "content": {"application/json": {"example": {"detail": "Роль не найдена"}}},
        },
    },
)
async def delete_role(
    role_id: str,
    role_service: RoleService = Depends(get_role_service)
):
    success = await role_service.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Роль не найдена")
