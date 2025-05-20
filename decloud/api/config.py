from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/decloud"

    # Yandex Cloud settings (optional for development)
    YC_STORAGE_BUCKET_NAME: str | None = "dev-bucket"
    YC_ACCESS_KEY_ID: str | None = "dev-access-key"
    # Secret key should be provided via environment variable
    YC_SECRET_ACCESS_KEY: str
    YC_ENDPOINT_URL: str = "https://storage.yandexcloud.net"
    YC_GENERATE_PRESIGNED_URL: str | None = "http://localhost:8000/mock/generate-url"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
