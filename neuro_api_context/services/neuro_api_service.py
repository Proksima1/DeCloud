import logging
import os
import tempfile
import uuid
from dataclasses import dataclass

import aiofiles

from backend_context.persistent.pg.api import ImageProcessing
from neuro_api_context.repositories.db_repository import DBRepository
from neuro_api_context.repositories.s3_repository import S3Repository
from neuro_api_context.services.postprocessing import SEN12MSPostprocessor
from neuro_api_context.services.preprocessing import SEN12MSDataPreprocessor

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NeuroApiService:
    _s3_repository: S3Repository
    _db_repository: DBRepository
    _preprocessor: SEN12MSDataPreprocessor = SEN12MSDataPreprocessor()
    _postprocessor: SEN12MSPostprocessor = SEN12MSPostprocessor()

    async def process_task(self, task_id: uuid.UUID) -> None:
        await self._db_repository.update_task_status(task_id=task_id, new_status=ImageProcessing.PROCESSING)
        optical_image, sar_image = await self._download_and_preprocess_files(task_id=task_id)
        result_image = await self._process_and_inverse_transform_images(
            task_id=task_id, optical_image=optical_image, sar_image=sar_image
        )
        await self._s3_repository.upload_result(task_id=task_id, result_content=result_image)
        await self._db_repository.update_task_status(task_id=task_id, new_status=ImageProcessing.READY)

    async def _preprocessing_images(self, optical_image: bytes, sar_image: bytes) -> tuple[bytes, bytes]:
        """
        Предобработка изображений

        Args:
            optical_image: Байты оптического изображения
            sar_image: Байты SAR изображения

        Returns:
            tuple[bytes, bytes]: Предобработанные изображения
        """
        try:
            with (
                tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as optical_file,
                tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as sar_file,
            ):
                async with aiofiles.open(optical_file.name, "wb") as f:
                    await f.write(optical_image)
                async with aiofiles.open(sar_file.name, "wb") as f:
                    await f.write(sar_image)

                input_tensor = self._preprocessor.preprocess(optical_file.name, sar_file.name)

                # TODO: preprocessing
                return optical_image, sar_image
        except Exception as e:
            logger.exception("Ошибка предобработки изображений", extra={"error": str(e)})
            raise
        finally:
            # Cleanup temporary files
            if "optical_file" in locals():
                os.unlink(optical_file.name)
            if "sar_file" in locals():
                os.unlink(sar_file.name)

    async def _download_and_preprocess_files(self, task_id: uuid.UUID) -> tuple[bytes, bytes]:
        optical_image, sar_image = await self._s3_repository.download_images(task_id=task_id)
        return await self._preprocessing_images(optical_image=optical_image, sar_image=sar_image)

    async def _process_and_inverse_transform_images(
        self,
        task_id: uuid.UUID,
        optical_image: bytes,
        sar_image: bytes,
    ) -> bytes:
        """
        Обработка и постобработка изображений

        Args:
            task_id: Идентификатор задачи
            optical_image: Байты оптического изображения
            sar_image: Байты SAR изображения

        Returns:
            bytes: Обработанное изображение
        """
        try:
            with (
                tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as optical_file,
                tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as sar_file,
            ):
                async with aiofiles.open(optical_file.name, "wb") as f:
                    await f.write(optical_image)
                async with aiofiles.open(sar_file.name, "wb") as f:
                    await f.write(sar_image)

                input_tensor = self._preprocessor.preprocess(optical_file.name, sar_file.name)

                # TODO: process using ML
                processed_tensor = input_tensor[:, :13, :, :]  # Берем только каналы S2

                result_image = self._postprocessor.postprocess(processed_tensor)

                logger.info("Изображение обработано ML моделью", extra={"task_id": task_id})
                return result_image
        except Exception as e:
            logger.exception("Ошибка обработки изображений", extra={"task_id": task_id, "error": str(e)})
            raise
        finally:
            if "optical_file" in locals():
                os.unlink(optical_file.name)
            if "sar_file" in locals():
                os.unlink(sar_file.name)

    async def _inverse_transform_images(self, result_image: bytes) -> bytes:
        # TODO: make inverse transform
        return result_image
