import multiprocessing as mp
from os import getenv

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file_path = getenv("ENV_FILE_PATH", ".env")


class Uvicorn(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = mp.cpu_count() * 2 + 1


class Rabbit(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8082


class Settings(BaseSettings):
    uvicorn: Uvicorn = Uvicorn()
    rabbit: Rabbit = Rabbit()

    model_config = SettingsConfigDict(
        env_file=env_file_path, env_prefix="cloud_", env_nested_delimiter="__", case_sensitive=False, extra="ignore"
    )


def _get_settings() -> Settings:
    settings = Settings()
    return settings


settings = _get_settings()
