import logging
import uuid
from dataclasses import dataclass

from backend_context.persistent.pg.api import ImageProcessing
from neuro_api_context.repositories.db_repository import DBRepository
from neuro_api_context.repositories.s3_repository import S3Repository

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NeuroApiService:
    _s3_repository: S3Repository
    _db_repository: DBRepository

    async def process_task(self, task_id: uuid.UUID) -> None:
        await self._db_repository.update_task_status(task_id=task_id, new_status=ImageProcessing.PROCESSING)
        optical_image, sar_image = await self._download_and_preprocess_files(task_id=task_id)
        result_image = await self._process_and_inverse_transform_images(
            task_id=task_id, optical_image=optical_image, sar_image=sar_image
        )
        await self._s3_repository.upload_result(task_id=task_id, result_content=result_image)
        await self._db_repository.update_task_status(task_id=task_id, new_status=ImageProcessing.READY)

    async def _preprocessing_images(self, optical_image: bytes, sar_image: bytes) -> tuple[bytes, bytes]:
        # TODO: preprocessing
        return optical_image, sar_image

    async def _download_and_preprocess_files(self, task_id: uuid.UUID) -> tuple[bytes, bytes]:
        optical_image, sar_image = await self._s3_repository.download_images(task_id=task_id)
        return await self._preprocessing_images(optical_image=optical_image, sar_image=sar_image)

    async def _process_and_inverse_transform_images(
        self,
        task_id: uuid.UUID,
        optical_image: bytes,  # noqa: ARG002
        sar_image: bytes,  # noqa: ARG002
    ) -> bytes:
        # TODO: process using ML
        processed_image = b"processed_image_data"
        result_image = await self._inverse_transform_images(processed_image)
        logger.info("image.ml.processed", extra={"task_id": task_id})
        return result_image

    async def _inverse_transform_images(self, result_image: bytes) -> bytes:
        # TODO: make inverse transform
        return result_image
