from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_base_url: str = "http://localhost:8000"

    database_url: str = "postgresql://soop:gumanoid99@localhost:5432/projectfsp"

    short_code_length: int = 6

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

@lru_cache
def get_setting(self) -> Setting:
    return Setting()

