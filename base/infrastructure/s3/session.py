from aioboto3 import Session

from base.settings import settings


def s3_session_from_settings() -> Session:
    return Session(
        aws_access_key_id=settings.s3_config.aws_access_key_id,
        aws_secret_access_key=settings.s3_config.aws_secret_access_key,
        region_name=settings.s3_config.region_name,
    )
