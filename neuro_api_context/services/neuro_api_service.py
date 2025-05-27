import logging
import uuid
from dataclasses import dataclass

import torch

from backend_context.persistent.pg.api import ImageProcessing
from neuro_api_context.repositories.db_repository import DBRepository
from neuro_api_context.repositories.s3_repository import S3Repository
from neuro_api_context.services.image_processing_service import ImageProcessor
from neuro_api_context.services.ml_evaluator import MLModelService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NeuroApiService:
    _s3_repository: S3Repository
    _db_repository: DBRepository
    _image_processor: ImageProcessor
    _ml_model_service: MLModelService

    async def process_task(self, task_id: uuid.UUID) -> None:
        await self._db_repository.update_task_status(task_id=task_id, new_status=ImageProcessing.PROCESSING)
        input_tensor = await self._download_and_preprocess_files(task_id=task_id)
        result_image = await self._process_and_inverse_transform_images(
            task_id=task_id,
            input_tensor=input_tensor,
        )
        await self._s3_repository.upload_result(task_id=task_id, result_content=result_image)
        await self._db_repository.update_task_status(task_id=task_id, new_status=ImageProcessing.READY)

    async def _preprocessing_images(self, optical_image: bytes, sar_image: bytes) -> torch.Tensor:
        return self._image_processor.preprocess(optical_image, sar_image)

    async def _download_and_preprocess_files(self, task_id: uuid.UUID) -> torch.Tensor:
        optical_image, sar_image = await self._s3_repository.download_images(task_id=task_id)
        return await self._preprocessing_images(optical_image=optical_image, sar_image=sar_image)

    async def _process_and_inverse_transform_images(
        self,
        task_id: uuid.UUID,
        input_tensor: torch.Tensor,
    ) -> bytes:
        try:
            output_tensor = self._ml_model_service.predict(input_tensor=input_tensor)

            result_image_bytes = self._image_processor.postprocess(output_tensor)

            logger.info("image.processed", extra={"task_id": task_id})
            return result_image_bytes
        except Exception as e:
            logger.exception("Ошибка обработки изображений", extra={"task_id": task_id, "error": str(e)})
            raise
