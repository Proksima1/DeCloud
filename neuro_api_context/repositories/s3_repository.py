import logging
import uuid
from dataclasses import dataclass

import botocore.exceptions
from aioboto3 import Session

from base.settings import settings

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class S3Repository:
    _s3_session: Session

    async def upload_result(self, task_id: uuid.UUID, result_content: bytes) -> None:
        async with self._s3_session.client("s3", endpoint_url=settings.s3_config.endpoint_url) as s3:
            result_key = self._build_key(task_id=task_id, key_name="result.tif")
            await s3.put_object(Bucket=settings.s3_config.bucket_name, Key=result_key, Body=result_content)
            logger.info("loaded.result.image", extra={"task_id": task_id, "image_size_bytes": len(result_key)})

    async def download_images(self, task_id: uuid.UUID) -> tuple[bytes, bytes]:
        async with self._s3_session.client("s3", endpoint_url=settings.s3_config.endpoint_url) as s3:
            try:
                optical_key = self._build_key(task_id=task_id, key_name="optical.tif")
                optical_response = await s3.get_object(Bucket=settings.s3_config.bucket_name, Key=optical_key)
                async with optical_response["Body"] as stream:
                    optical_content = await stream.read()

                sar_key = self._build_key(task_id=task_id, key_name="sar.tif")
                sar_response = await s3.get_object(Bucket=settings.s3_config.bucket_name, Key=sar_key)
                async with sar_response["Body"] as stream:
                    sar_content = await stream.read()

                logger.info("download.images.success", extra={"task_id": task_id})
            except botocore.exceptions.ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "NoSuchKey":
                    logger.warning("downloading.images.not.found", extra={"task_id": task_id})
                    return b"", b""
                raise
            return optical_content, sar_content

    def _build_key(self, task_id: uuid.UUID, key_name: str) -> str:
        return self._build_s3_path(task_id=task_id) + key_name

    def _build_s3_path(self, task_id: uuid.UUID) -> str:
        return f"{settings.s3_config.bucket_name}/uploads/{task_id}/"
