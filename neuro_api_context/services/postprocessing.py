import io
import logging

import numpy as np
import rasterio
import torch

logger = logging.getLogger(__name__)


class SEN12MSPostprocessor:
    def __init__(self, s2_max_reflectance: float = 3000.0):
        """
        Класс для постобработки данных после ML модели

        Параметры:
        - s2_max_reflectance: максимальное значение отражательной способности S2
        """
        self.s2_max_reflectance = s2_max_reflectance

    def postprocess(self, tensor: torch.Tensor) -> bytes:
        """
        Конвертация обработанного тензора обратно в байты изображения

        Args:
            tensor: Обработанный тензор в формате [1, 13, H, W]

        Returns:
            bytes: Обработанное изображение в формате байтов
        """
        try:
            image = tensor.squeeze(0).numpy()

            # Денормализация
            image = (image + 1.0) / 2.0 * self.s2_max_reflectance
            image = np.clip(image, 0, self.s2_max_reflectance)

            # Конвертация в uint16
            image = (image * 65535 / self.s2_max_reflectance).astype(np.uint16)

            # Сохранение в байты
            with io.BytesIO() as buffer:
                with rasterio.io.MemoryFile(buffer) as memfile:
                    with memfile.open(
                        driver="GTiff",
                        height=image.shape[1],
                        width=image.shape[2],
                        count=image.shape[0],
                        dtype=image.dtype,
                    ) as dst:
                        dst.write(image)
                return buffer.getvalue()
        except Exception as e:
            logger.exception("Ошибка постобработки", extra={"error": str(e)})
