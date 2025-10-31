from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import get_superuser_user
from src.schemas.role import RoleResponse
from src.schemas.user import UserResponse
from src.schemas.user_role import UserRoleCreate
from src.services.user_role_service import UserRoleService, get_user_role_service

router = APIRouter(dependencies=[Depends(get_superuser_user)])


@router.post(
    "/assign",
    summary="Назначить роль пользователю",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Роль успешно назначена"},
        status.HTTP_400_BAD_REQUEST: {"description": "Ошибка назначения роли"},
    }
)
async def assign_role_to_user(
    user_role_data: UserRoleCreate,
    user_role_service: UserRoleService = Depends(get_user_role_service)

):
    """
    Назначить пользователю определённую роль.
    """
    success = await user_role_service.assign_role_to_user(
        str(user_role_data.user_id),
        str(user_role_data.role_id)
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось назначить роль. Проверьте существование пользователя и роли."
        )
    return {"message": "Роль успешно назначена"}


@router.delete(
    "/remove",
    summary="Удалить роль у пользователя",
    responses={
        status.HTTP_200_OK: {"description": "Роль успешно удалена"},
        status.HTTP_404_NOT_FOUND: {"description": "Роль не найдена у пользователя"},
    }
)
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_role_service)
):
    """
    Удалить роль у пользователя.
    """
    success = await user_role_service.remove_role_from_user(
        str(user_id),
        str(role_id)
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не найдена у пользователя."
        )
    return {"message": "Роль успешно удалена"}


@router.get(
    "/user/{user_id}/roles",
    summary="Получить роли пользователя",
    response_model=List[RoleResponse],
    responses={
        status.HTTP_200_OK: {"description": "Список ролей пользователя"},
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
    }
)
async def get_user_roles(
    user_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_role_service)
):
    """
    Получить все роли, назначенные пользователю.
    """
    roles = await user_role_service.get_user_roles(str(user_id))
    return roles


@router.get(
    "/role/{role_id}/users",
    summary="Получить пользователей с ролью",
    response_model=List[UserResponse],
    responses={
        status.HTTP_200_OK: {"description": "Список пользователей с ролью"},
        status.HTTP_404_NOT_FOUND: {"description": "Роль не найдена"},
    }
)
async def get_users_with_role(
    role_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_role_service)
):
    """
    Получить всех пользователей, имеющих определённую роль.
    """
    users = await user_role_service.get_users_with_role(str(role_id))
    return users
