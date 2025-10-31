from functools import lru_cache
from src.core.config import settings
from urllib.parse import urlencode
from fastapi import Request
import httpx


class GoogleOAuthService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.client_id = settings.oauth_google.client_id
        self.client_secret = settings.oauth_google.client_secret
        self.redirect_uri = settings.oauth_google.redirect_uri

    def generate_redirect_uri(self) -> str:
        """
        Гененрирует URL на страницу авторизации Google OAuth
        """
        query_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join([
                "openid",
                "profile",
                "email",
            ]),
            "access_type": "offline",
        }
        query_string = urlencode(query_params)
        return f"{settings.oauth_google.auth_base_url}?{query_string}"

    async def get_access_token(self, code: str) -> str:
        """
        Обменивает код авторизации на access token Google OAuth.
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
            settings.oauth_google.token_url,
            data=data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()["access_token"]

    async def get_user_info(self, access_token: str) -> dict:
        """
        Получает информацию о пользователе из Google API по access token.
        """
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = await self.client.get(
            settings.oauth_google.userinfo_url,
            headers=headers
        )
        response.raise_for_status()
        return response.json()


@lru_cache
def get_oauth_service(
    request: Request
) -> GoogleOAuthService:
    return GoogleOAuthService(http_client=request.app.state.http_client)
