import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv


class EnvKeys(str, Enum):
    DJANGO_SECRET: str = "DJANGO_SECRET"  # noqa: S105
    DJANGO_DEBUG: str = "DJANGO_DEBUG"
    YC_ACCESS_KEY_ID: str = "YC_ACCESS_KEY_ID"
    YC_SECRET_ACCESS_KEY: str = "YC_SECRET_ACCESS_KEY"  # noqa: S105
    YC_STORAGE_BUCKET_NAME: str = "YC_STORAGE_BUCKET_NAME"
    YC_GENERATE_PRESIGNED_URL: str = "YC_GENERATE_PRESIGNED_URL"
    YC_ENDPOINT_URL: str = "YC_ENDPOINT_URL"
    POSTGRES_DB_NAME: str = "POSTGRES_DB_NAME"
    POSTGRES_DB_USER: str = "POSTGRES_DB_USER"
    POSTGRES_DB_PASSWORD: str = "POSTGRES_DB_PASSWORD"  # noqa: S105
    POSTGRES_DB_HOST: str = "POSTGRES_DB_HOST"
    POSTGRES_DB_PORT: str = "POSTGRES_DB_PORT"


load_dotenv(".env")

YC_ACCESS_KEY_ID = os.getenv(EnvKeys.YC_ACCESS_KEY_ID.value)
YC_SECRET_ACCESS_KEY = os.getenv(EnvKeys.YC_SECRET_ACCESS_KEY.value)
YC_STORAGE_BUCKET_NAME = os.getenv(EnvKeys.YC_STORAGE_BUCKET_NAME.value)
YC_ENDPOINT_URL = os.getenv(EnvKeys.YC_ENDPOINT_URL.value, "https://storage.yandexcloud.net")
YC_GENERATE_PRESIGNED_URL = os.getenv(EnvKeys.YC_GENERATE_PRESIGNED_URL.value)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(EnvKeys.DJANGO_SECRET.value, "not_secret")

DEBUG = bool(int(os.environ.get(EnvKeys.DJANGO_DEBUG.value, "1")))

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "core",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "decloud.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "decloud.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv(EnvKeys.POSTGRES_DB_NAME.value, "decloud"),
        "USER": os.getenv(EnvKeys.POSTGRES_DB_USER.value, "postgres"),
        "PASSWORD": os.getenv(EnvKeys.POSTGRES_DB_PASSWORD.value, "postgres"),
        "HOST": os.getenv(EnvKeys.POSTGRES_DB_HOST.value, "localhost"),
        "PORT": os.getenv(EnvKeys.POSTGRES_DB_PORT.value, "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "DeCloud",
    "DESCRIPTION": "Документация API DeCloud",
    "VERSION": "v0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
}

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = DEBUG

AUTH_USER_MODEL = "core.User"
