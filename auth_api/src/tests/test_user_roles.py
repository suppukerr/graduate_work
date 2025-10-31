from http import HTTPStatus
from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_assign_role_to_user(superuser_client: AsyncClient):
    # Создаем пользователя
    user_payload = {"username": "user1", "email": "user1@example.com", "password": "pass1"}
    user_resp = await superuser_client.post("/api/v1/auth/signup", json=user_payload)
    user_id = user_resp.json()["id"]

    # Создаем роль
    role_payload = {"name": "role1", "description": "desc"}
    role_resp = await superuser_client.post("/api/v1/roles/", json=role_payload)
    role_id = role_resp.json()["id"]

    # Назначаем роль
    assign_payload = {"user_id": user_id, "role_id": role_id}
    assign_resp = await superuser_client.post("/api/v1/user-roles/assign", json=assign_payload)
    assert assign_resp.status_code == HTTPStatus.CREATED
    assert assign_resp.json()["message"] == "Роль успешно назначена"

    # Повторное назначение (роль уже есть)
    assign_resp2 = await superuser_client.post("/api/v1/user-roles/assign", json=assign_payload)
    assert assign_resp2.status_code == HTTPStatus.CREATED

    # Ошибка: несуществующий пользователь
    bad_payload = {"user_id": str(UUID(int=0)), "role_id": role_id}
    bad_resp = await superuser_client.post("/api/v1/user-roles/assign", json=bad_payload)
    assert bad_resp.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_remove_role_from_user(superuser_client: AsyncClient):
    # Создаем пользователя и роль
    user_payload = {"username": "user2", "email": "user2@example.com", "password": "pass2"}
    user_resp = await superuser_client.post("/api/v1/auth/signup", json=user_payload)
    user_id = user_resp.json()["id"]
    role_payload = {"name": "role2", "description": "desc"}
    role_resp = await superuser_client.post("/api/v1/roles/", json=role_payload)
    role_id = role_resp.json()["id"]

    # Назначаем роль
    assign_payload = {"user_id": user_id, "role_id": role_id}
    await superuser_client.post("/api/v1/user-roles/assign", json=assign_payload)

    # Удаляем роль
    remove_resp = await superuser_client.delete(f"/api/v1/user-roles/remove?user_id={user_id}&role_id={role_id}")
    assert remove_resp.status_code == HTTPStatus.OK
    assert remove_resp.json()["message"] == "Роль успешно удалена"

    # Повторное удаление — 404
    remove_resp2 = await superuser_client.delete(f"/api/v1/user-roles/remove?user_id={user_id}&role_id={role_id}")
    assert remove_resp2.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_roles(superuser_client: AsyncClient):
    # Создаем пользователя и две роли
    user_payload = {"username": "user3", "email": "user3@example.com", "password": "pass3"}
    user_resp = await superuser_client.post("/api/v1/auth/signup", json=user_payload)
    user_id = user_resp.json()["id"]
    role1_resp = await superuser_client.post("/api/v1/roles/", json={"name": "role3a", "description": ""})
    role2_resp = await superuser_client.post("/api/v1/roles/", json={"name": "role3b", "description": ""})
    role1_id = role1_resp.json()["id"]
    role2_id = role2_resp.json()["id"]

    # Назначаем роли
    await superuser_client.post("/api/v1/user-roles/assign", json={"user_id": user_id, "role_id": role1_id})
    await superuser_client.post("/api/v1/user-roles/assign", json={"user_id": user_id, "role_id": role2_id})

    # Получаем роли пользователя
    resp = await superuser_client.get(f"/api/v1/user-roles/user/{user_id}/roles")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    role_names = [r["name"] for r in data]
    assert "role3a" in role_names and "role3b" in role_names


@pytest.mark.asyncio
async def test_get_users_with_role(superuser_client: AsyncClient):
    # Создаем двух пользователей и роль
    user1_resp = await superuser_client.post(
        "/api/v1/auth/signup",
        json={"username": "user4a", "email": "user4a@example.com", "password": "pass4a"}
    )
    user2_resp = await superuser_client.post(
        "/api/v1/auth/signup",
        json={"username": "user4b", "email": "user4b@example.com", "password": "pass4b"}
    )
    user1_id = user1_resp.json()["id"]
    user2_id = user2_resp.json()["id"]
    role_resp = await superuser_client.post("/api/v1/roles/", json={"name": "role4", "description": ""})
    role_id = role_resp.json()["id"]

    # Назначаем роль обоим
    await superuser_client.post("/api/v1/user-roles/assign", json={"user_id": user1_id, "role_id": role_id})
    await superuser_client.post("/api/v1/user-roles/assign", json={"user_id": user2_id, "role_id": role_id})

    # Получаем пользователей с ролью
    resp = await superuser_client.get(f"/api/v1/user-roles/role/{role_id}/users")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    user_names = [u["username"] for u in data]
    assert "user4a" in user_names and "user4b" in user_names
