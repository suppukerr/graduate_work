from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_role(superuser_client: AsyncClient):
    payload = {"name": "admin", "description": "Администратор"}
    response = await superuser_client.post("/api/v1/roles/", json=payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]

    # Попытка создать роль с тем же именем
    response_conflict = await superuser_client.post("/api/v1/roles/", json=payload)
    assert response_conflict.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_get_all_roles(superuser_client: AsyncClient):
    # Создаем две роли
    await superuser_client.post("/api/v1/roles/", json={"name": "user", "description": "Пользователь"})
    await superuser_client.post("/api/v1/roles/", json={"name": "moderator", "description": "Модератор"})
    response = await superuser_client.get("/api/v1/roles/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert any(role["name"] == "user" for role in data)
    assert any(role["name"] == "moderator" for role in data)


@pytest.mark.asyncio
async def test_get_role_by_id(superuser_client: AsyncClient):
    # Создаем роль
    payload = {"name": "support", "description": "Техподдержка"}
    create_resp = await superuser_client.post("/api/v1/roles/", json=payload)
    role_id = create_resp.json()["id"]

    # Получаем по id
    response = await superuser_client.get(f"/api/v1/roles/{role_id}")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == payload["name"]

    # Не найдено
    response_404 = await superuser_client.get("/api/v1/roles/00000000-0000-0000-0000-000000000000")
    assert response_404.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_role(superuser_client: AsyncClient):
    # Создаем роль
    payload = {"name": "editor", "description": "Редактор"}
    create_resp = await superuser_client.post("/api/v1/roles/", json=payload)
    role_id = create_resp.json()["id"]

    # Обновляем имя и описание
    update_payload = {"name": "chief_editor", "description": "Главный редактор"}
    response = await superuser_client.put(f"/api/v1/roles/{role_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]

    # Конфликт по имени
    await superuser_client.post("/api/v1/roles/", json={"name": "unique_name", "description": ""})
    conflict_payload = {"name": "unique_name"}
    response_conflict = await superuser_client.put(f"/api/v1/roles/{role_id}", json=conflict_payload)
    assert response_conflict.status_code == HTTPStatus.CONFLICT

    # Не найдено
    response_404 = await superuser_client.put("/api/v1/roles/00000000-0000-0000-0000-000000000000", json=update_payload)
    assert response_404.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_role(superuser_client: AsyncClient):
    # Создаем роль
    payload = {"name": "deleteme", "description": "Удалить"}
    create_resp = await superuser_client.post("/api/v1/roles/", json=payload)
    role_id = create_resp.json()["id"]

    # Удаляем
    response = await superuser_client.delete(f"/api/v1/roles/{role_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT

    # Повторное удаление — 404
    response_404 = await superuser_client.delete(f"/api/v1/roles/{role_id}")
    assert response_404.status_code == HTTPStatus.NOT_FOUND
