import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_login_history_contains_recent_login(authorized_client: AsyncClient):
    response = await authorized_client.get("/api/v1/auth/login-history")

    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "Login history is empty"

    login_entry = data[0]
    assert "ip_address" in login_entry
    assert "user_agent" in login_entry
    assert "login_time" in login_entry

    try:
        datetime.fromisoformat(login_entry["login_time"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("login_time is not a valid ISO datetime")


@pytest.mark.asyncio
async def test_login_history_returns_entries_for_user(client: AsyncClient, authorized_client):
    # Сделаем второй вход для создания 2 записей
    await client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "strongpassword"
    })

    # Запрос истории входов
    response = await authorized_client.get("/api/v1/auth/login-history")
    assert response.status_code == 200

    login_data = response.json()
    assert isinstance(login_data, list)
    assert len(login_data) >= 1

    for entry in login_data:
        assert "ip_address" in entry
        assert "user_agent" in entry
        assert "login_time" in entry


@pytest.mark.asyncio
async def test_login_history_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/auth/login-history")
    assert response.status_code == 403
