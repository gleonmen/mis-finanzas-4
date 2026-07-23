from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://finanzas:finanzas@db:5432/finanzas"
    # Frontend origin allowed by CORS (the browser calls the API directly).
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
