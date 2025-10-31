from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    payload = {
        "username": "testuser",
        "email": "user@example.com",
        "password": "strongpassword",
    }

    response = await client.post("/api/v1/auth/signup", json=payload)

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Сначала регистрируем пользователя
    signup_payload = {
        "username": "testuser",
        "email": "user@example.com",
        "password": "strongpassword"
    }
    signup_response = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_response.status_code == HTTPStatus.CREATED

    # Теперь логинимся
    login_payload = {
        "username": "testuser",
        "password": "strongpassword",
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    data = login_response.json()
    assert login_response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_change_credentials(client: AsyncClient, access_token: str):
    payload = {
        "new_email": "new_user@example.com",
        "new_password": "newstrongpassword"
    }

    response = await client.put(
        "/api/v1/auth/change-credentials",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["detail"] == "Данные успешно обновлены"
