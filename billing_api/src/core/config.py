import logging
from pathlib import Path

import dotenv
from pydantic import BaseModel, Field, HttpUrl
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
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class JWT(BaseModel):
    secretkey: str
    algorithm: str


class Kafka(BaseModel):
    """Настройки Kafka."""

    bootstrap_servers: str = "kafka-0:9092"
    topic_billing_events: str = "user-billing-events"
    request_timeout_ms: int = 30000
    enable_idempotence: bool = True
    acks: str = "all"

    @property
    def bootstrap_servers_list(self) -> list[str]:
        """Получить список серверов как массив."""
        return [server.strip() for server in self.bootstrap_servers.split(",")]


class Payment(BaseModel):
    redirect_url: HttpUrl = "https://example.com/"
    create_url: str = "http://payment_api:8000/api/v1/payment/youkassa/payment"


class AppConfig(BaseSettings):
    project_name: str = "billing-api"
    description: str = "Сервис биллинга для управления подписками и платежами"
    docs_url: str = "/api/v1/billing/docs"
    openapi_url: str = "/api/v1/billing/openapi.json"

    server: Server = Server()
    postgres: Postgres = Postgres()
    jwt: JWT
    kafka: Kafka = Kafka()
    payment: Payment = Payment()

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
