from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_user: str = "billing_user"
    postgres_password: str = "billing_pass"
    postgres_db: str = "billing_db"

    # Auth database settings (for user info)
    auth_postgres_host: str = "localhost"
    auth_postgres_port: int = 5432
    auth_postgres_user: str = "auth_user"
    auth_postgres_password: str = "auth_pass"
    auth_postgres_db: str = "auth_db"

    # Admin settings
    admin_secret_key: str = "your-secret-key-change-in-production"
    admin_title: str = "Billing Admin Panel"

    # Auth API settings
    auth_api_url: str = "http://localhost"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8002

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def auth_database_url(self) -> str:
        return (
            f"postgresql://{self.auth_postgres_user}:"
            f"{self.auth_postgres_password}@{self.auth_postgres_host}:"
            f"{self.auth_postgres_port}/{self.auth_postgres_db}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
