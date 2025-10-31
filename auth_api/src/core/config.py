import logging
from pathlib import Path

from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parents[2]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

PROJECT_ROOT = Path(__file__).parents[2]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

PROJECT_ROOT = Path(__file__).parents[2]
ENV_FILE_PATH = PROJECT_ROOT / ".env"
if ENV_FILE_PATH.is_file():
    print(f".env файл существует по пути: {ENV_FILE_PATH}")
else:
    print(f".env файл НЕ найден по пути: {ENV_FILE_PATH}. "
          f"Используются значения по умолчанию или переменные окружения.")


class ApiConfig(BaseModel):
    host: str
    port: int
    base_role: str = "USER"


class PostgresConfig(BaseModel):
    db: str
    user: str
    password: str
    host: str
    port: int

    @computed_field
    @property
    def async_database_url(self) -> str:
        """URL для асинхронного подключения к PostgreSQL"""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.db}"
        )

    @computed_field
    @property
    def database_url(self) -> str:
        """URL для синхронного подключения к PostgreSQL"""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


class RedisConfig(BaseModel):
    port: int
    host: str


class OAuthGoogleConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    auth_base_url: str
    token_url: str
    userinfo_url: str


# проверить ссылки
class OAuthYandexConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str  # поменять для докера
    auth_base_url: str
    token_url: str
    userinfo_url: str


class JWTConfig(BaseModel):
    algorithm: str
    secret_access: str
    secret_refresh: str
    expire_access_minutes: int
    expire_refresh_days: int


class CliConfig(BaseModel):
    secret: str = "secret"


class RateLimitConfig(BaseModel):
    rate_limit: int = 10  # Максимальное количество запросов
    leak_rate: int = 1  # Скорость утечки (запросов в секунду)


class OTLPConfig(BaseModel):
    host: str = "jaeger"
    port: int = 4317
    insecure: bool = True


class KafkaConfig(BaseModel):
    """Настройки Kafka."""
    bootstrap_servers: str = "kafka-0:9092"
    topic_billing_events: str = "user-billing-events"
    consumer_group_id: str = "auth-service-group"
    request_timeout_ms: int = 30000
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    subscriber_role_name: str = "SUBSCRIBER"

    @property
    def bootstrap_servers_list(self) -> list[str]:
        """Получить список серверов как массив."""
        return [server.strip() for server in self.bootstrap_servers.split(",")]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    testing: bool = False
    enable_tracing: bool = False
    api: ApiConfig
    postgres: PostgresConfig
    redis: RedisConfig
    jwt: JWTConfig
    cli: CliConfig
    rate_limit: RateLimitConfig = RateLimitConfig()  # что бы не искал имя в .env файле
    oauth_google: OAuthGoogleConfig
    oauth_yandex: OAuthYandexConfig
    otlp: OTLPConfig = OTLPConfig()
    kafka: KafkaConfig = KafkaConfig()


settings = Settings()
# settings.model_dump()
# print(settings)
