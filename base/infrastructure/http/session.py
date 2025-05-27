from datetime import timedelta

from aiohttp import ClientSession, ClientTimeout
from ujson import dumps

from base.settings import settings


def new_session(timeout: timedelta) -> ClientSession:
    return ClientSession(
        timeout=ClientTimeout(total=timeout.total_seconds()),
        json_serialize=dumps,
        raise_for_status=False,
    )


def new_session_from_settings() -> ClientSession:
    return new_session(timeout=settings.http_client.timeout)
