import logging
import uuid
from dataclasses import dataclass

from aioboto3 import Session

from base.settings import settings


@dataclass(slots=True, frozen=True)
class S3Repository:
    _s3_session: Session

    async def upload_images(self, task_id: uuid.UUID, optical_content: bytes, sar_content: bytes) -> None:
        async with self._s3_session.client("s3", endpoint_url=settings.s3_config.endpoint_url) as s3:
            optical_key = self._build_key(task_id=task_id, key_name="optical.tif")
            await s3.put_object(Bucket=settings.s3_config.bucket_name, Key=optical_key, Body=optical_content)
            logging.info("loaded.optical.image", extra={"task_id": task_id})
            sar_key = self._build_key(task_id=task_id, key_name="sar.tif")
            await s3.put_object(Bucket=settings.s3_config.bucket_name, Key=sar_key, Body=sar_content)
            logging.info("loaded.sar.image", extra={"task_id": task_id})

    def _build_key(self, task_id: uuid.UUID, key_name: str) -> str:
        return self._build_s3_path(task_id=task_id) + key_name

    def _build_s3_path(self, task_id: uuid.UUID) -> str:
        return f"{settings.s3_config.bucket_name}/uploads/{task_id}/"
