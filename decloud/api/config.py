from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/decloud"
    YC_STORAGE_BUCKET_NAME: str
    YC_ACCESS_KEY_ID: str
    YC_SECRET_ACCESS_KEY: str
    YC_ENDPOINT_URL: str = "https://storage.yandexcloud.net"
    YC_GENERATE_PRESIGNED_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
