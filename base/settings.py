import multiprocessing as mp
from datetime import timedelta
from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict

from base.logger import LoggerSettings, init_logger
from base.schemas.base import PureBaseModel

env_file_path = getenv("ENV_FILE_PATH", ".env")


class Uvicorn(PureBaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = mp.cpu_count() * 2 + 1


class Rabbit(PureBaseModel):
    host: str = "0.0.0.0"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"  # noqa: S105


class FastAPI(PureBaseModel):
    openapi_url: str = "/openapi.json"
    root_path: str = ""


class S3Config(PureBaseModel):
    endpoint_url: str = "https://storage.yandexcloud.net"
    generate_presigned_url_endpoint: str = "https://functions.yandexcloud.net/d4eca2ru45nceehl1hva"
    region_name: str = "ru-central1"
    aws_access_key_id: str = "key"
    aws_secret_access_key: str = "key"  # noqa: S105
    bucket_name: str = "testka"


class HTTPClient(PureBaseModel):
    timeout: timedelta = timedelta(seconds=5)


class Postgres(PureBaseModel):
    protocol: str = "postgresql+asyncpg"

    host: str = "localhost"
    port: int = 5432

    username: str | None = "postgres"
    password: str | None = "postgres"  # noqa: S105
    database: str = "decloud"

    echo: bool = False
    pool: bool = True
    max_pool_size: int = 5
    max_overflow: int = 30
    statement_cache_size: int = 0
    prepared_statement_cache_size: int = 0
    pool_recycle: timedelta = timedelta(minutes=20)
    pool_pre_ping: bool = True
    expire_on_commit: bool = False

    statement_timeout_ms: int = 10 * 1000
    connect_timeout_ms: int = 3 * 1000

    def dsn(self) -> str:
        return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def dsn_safe(self) -> str:
        return f"{self.protocol}://{self.username}:***@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    release: bool = False
    service_name: str = "undefined"

    uvicorn: Uvicorn = Uvicorn()
    rabbit: Rabbit = Rabbit()
    fastapi: FastAPI = FastAPI()
    s3_config: S3Config = S3Config()
    pg_rw: Postgres = Postgres()
    pg_ro: Postgres = Postgres()
    logger: LoggerSettings = LoggerSettings()
    http_client: HTTPClient = HTTPClient()

    model_config = SettingsConfigDict(
        env_file=env_file_path, env_prefix="cloud_", env_nested_delimiter="__", case_sensitive=False, extra="ignore"
    )


def _get_settings() -> Settings:
    settings = Settings()
    init_logger(settings.logger)
    return settings


settings = _get_settings()
