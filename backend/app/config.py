from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    cinii_app_id: str = ""
    openai_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    # CORS (frontend origin allowlist)
    # Comma-separated origins. Example:
    # CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    # Optional regex. Example:
    # CORS_ALLOW_ORIGIN_REGEX=^http://(localhost|127\.0\.0\.1)(:\d+)?$
    cors_allow_origin_regex: str = ""

    def cors_origins_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_allow_origins.split(",")]
        return [o for o in origins if o]


@lru_cache
def get_settings() -> Settings:
    return Settings()
