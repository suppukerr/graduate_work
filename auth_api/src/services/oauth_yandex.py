from functools import lru_cache
from src.core.config import settings
from urllib.parse import urlencode
from fastapi import Request
import httpx


class YandexOAuthService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.client_id = settings.oauth_yandex.client_id
        self.client_secret = settings.oauth_yandex.client_secret
        self.redirect_uri = settings.oauth_yandex.redirect_uri

    def generate_redirect_uri(self) -> str:
        """
        Гененрирует URL на страницу авторизации Yandex OAuth
        """
        query_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join([
                "login:email",
                "login:info",
            ]),
        }
        query_string = urlencode(query_params)
        return f"{settings.oauth_yandex.auth_base_url}?{query_string}"

    async def get_access_token(self, code: str) -> str:
        """
        Обменивает код авторизации на access token Yandex OAuth.
        """

        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = await self.client.post(
            settings.oauth_yandex.token_url,
            data=data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()["access_token"]

    async def get_user_info(self, access_token: str) -> dict:
        """
        Получает информацию о пользователе из Yandex API по access token.
        """
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = await self.client.get(
            settings.oauth_yandex.userinfo_url,
            headers=headers
        )
        response.raise_for_status()
        return response.json()


@lru_cache
def get_oauth_service(
    request: Request
) -> YandexOAuthService:
    return YandexOAuthService(http_client=request.app.state.http_client)
