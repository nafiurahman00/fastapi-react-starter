"""Application settings, read from environment variables / a .env file.

Equivalent of Spring's application.properties. Import the shared `settings`
object anywhere you need a value.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FastAPI + React Starter"

    # ----- Database -----
    database_url: str = "mysql+pymysql://root:root@localhost:3306/app_db"
    echo_sql: bool = False

    # ----- JWT (used by core/security.py) -----
    jwt_secret: str = "change-me-this-is-a-demo-secret-key-please-replace-32+chars"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 hours

    # ----- CORS -----
    cors_allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


settings = Settings()
