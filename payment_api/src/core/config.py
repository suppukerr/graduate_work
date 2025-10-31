import logging

import dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.logger_config import LoggerSettings

ENV_FILE = dotenv.find_dotenv()


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 30
    backlog: int = 512
    max_requests: int = 1000
    max_requests_jitter: int = 50
    worker_class: str = "uvicorn.workers.UvicornWorker"


class Postgres(BaseModel):
    host: str = "localhost"  # почему в енв имя контейнера? # почему при запуске тут берется из енв
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class JWT(BaseModel):
    secret_key: str = "your-secret-key" # почему при запуске тут берется не из енв
    algorithm: str = "HS256"


class Subcription(BaseModel):
    update_url: str = "http://billing-api:8000/api/v1/billing/user-subscriptions/"


# не подтягивает из енв
class Youkassa(BaseModel):
    SHOP_ID: str = "1183493"
    SECRET_KEY: str = "test_KBmu1UV2eJvzYAHNQ7ZJDzTWjvrgtEajAYraaRI8fGA"
    API: str = "https://api.yookassa.ru/v3/payments"


class AppConfig(BaseSettings):
    project_name: str = "payment-api"
    description: str = "Сервис биллинга для управления платежами"
    docs_url: str = "/api/v1/payment/docs"
    openapi_url: str = "/api/v1/payment/openapi.json"

    server: Server = Server()
    postgres: Postgres = Postgres()
    jwt: JWT = JWT()
    youkassa: Youkassa = Youkassa()
    subscription: Subcription = Subcription()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> AppConfig:
    log = LoggerSettings()
    log.apply()
    # logger = logging.getLogger(__name__)
    app_config = AppConfig()
    # logger.info(f"app_config.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


settings = _get_config()
