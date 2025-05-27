import io
import logging
from io import BytesIO

import numpy as np
import rasterio
import torch

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(
        self,
        s2_max_reflectance: float = 3000.0,
        s1_clip_min: tuple[float, float] = (-25.0, -32.5),  # VV, VH
        s1_clip_max: tuple[float, float] = (0.0, 0.0),
    ):
        """
        Класс для предобработки данных Sentinel-1 и Sentinel-2
        в формат, совместимый с обученной моделью Pix2Pix+SAR

        Параметры:
        - s2_max_reflectance: максимальное значение отражательной способности S2
        - s1_clip_min: минимальные значения для клиппинга S1 (VV, VH)
        - s1_clip_max: максимальные значения для клиппинга S1 (VV, VH)
        """
        # Параметры нормализации S2
        self.s2_max_reflectance = s2_max_reflectance

        # Параметры нормализации S1 (в формате для [2, 1, 1] reshape)
        self.s1_clip_min = np.array(s1_clip_min, dtype=np.float32).reshape(2, 1, 1)
        self.s1_clip_max = np.array(s1_clip_max, dtype=np.float32).reshape(2, 1, 1)
        self.s1_denominator = self.s1_clip_max - self.s1_clip_min
        self.s1_denominator[self.s1_denominator == 0] = 1e-6

    def _load_and_validate_image(self, data: bytes, expected_channels: int) -> np.ndarray:
        with rasterio.open(BytesIO(data), driver="GTiff") as src:
            img = src.read()
            if img.shape[0] != expected_channels:
                raise ValueError(f"Expected {expected_channels} channels, got {img.shape[0]}")
            return img

    def _handle_nan(self, data: np.ndarray) -> np.ndarray:
        """Обработка NaN значений (замена на среднее по каналу)"""
        data = data.astype(np.float32)
        for i in range(data.shape[0]):
            channel = data[i]
            if np.isnan(channel).any():
                nan_mask = np.isnan(channel)
                channel_mean = np.nanmean(channel)
                channel[nan_mask] = channel_mean
        return data

    def _normalize_s2(self, s2_data: np.ndarray) -> np.ndarray:
        """Нормализация данных Sentinel-2"""
        s2_processed = self._handle_nan(s2_data)
        s2_norm = (s2_processed / self.s2_max_reflectance) * 2.0 - 1.0
        return np.clip(s2_norm, -1.0, 1.0)

    def _normalize_s1(self, s1_data: np.ndarray) -> np.ndarray:
        """Нормализация данных Sentinel-1"""
        s1_processed = self._handle_nan(s1_data)
        s1_clipped = np.clip(s1_processed, self.s1_clip_min, self.s1_clip_max)
        s1_norm = ((s1_clipped - self.s1_clip_min) / self.s1_denominator) * 2.0 - 1.0
        return np.clip(s1_norm, -1.0, 1.0)

    def preprocess(self, s2_cloudy_bytes: bytes, s1_bytes: bytes) -> torch.Tensor:
        s2_cloudy = self._load_and_validate_image(s2_cloudy_bytes, 13)
        s1 = self._load_and_validate_image(s1_bytes, 2)

        s2_norm = self._normalize_s2(s2_cloudy)
        s1_norm = self._normalize_s1(s1)

        combined = np.concatenate([s2_norm, s1_norm], axis=0)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tensor = torch.from_numpy(combined).unsqueeze(0).to(device).float()

        return tensor

    def postprocess(self, output_tensor: torch.Tensor) -> bytes:
        try:
            image = output_tensor.squeeze().cpu().numpy()

            # Денормализация
            image = (image + 1.0) / 2.0 * self.s2_max_reflectance
            image = np.clip(image, 0, self.s2_max_reflectance)

            # Конвертация в uint16
            image = (image * 65535 / self.s2_max_reflectance).astype(np.uint16)

            # print(f"Форма тензора {image.shape}")
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
                    buffer.write(memfile.read())
                return buffer.getvalue()
        except Exception as e:
            logger.exception("Ошибка постобработки", extra={"error": str(e)})
