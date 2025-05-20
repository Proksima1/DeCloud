from pathlib import Path

import numpy as np
import rasterio
import torch


class SEN12MSDataPreprocessor:
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

    def _load_and_validate_image(self, path: Path, expected_channels: int) -> np.ndarray:
        """Загружает изображение и проверяет количество каналов"""
        with rasterio.open(path) as src:
            img = src.read()
            if img.shape[0] != expected_channels:
                raise ValueError(f"Ожидается {expected_channels} каналов, получено {img.shape[0]} в файле {path}")
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

    def preprocess(self, s2_cloudy_path: Path, s1_path: Path) -> torch.Tensor:
        """
        Основной метод предобработки

        Аргументы:
            - s2_cloudy_path: путь к файлу Sentinel-2 Cloudy (13 каналов)
            - s1_path: путь к файлу Sentinel-1 (2 канала)

        Возвращает:
            - torch.Tensor: объединенный тензор в формате [1, 15, H, W]
        """
        # Загрузка данных
        s2_cloudy = self._load_and_validate_image(s2_cloudy_path, 13)
        s1 = self._load_and_validate_image(s1_path, 2)

        # Нормализация
        s2_norm = self._normalize_s2(s2_cloudy)
        s1_norm = self._normalize_s1(s1)

        # Объединение каналов
        combined = np.concatenate([s2_norm, s1_norm], axis=0)

        # Конвертация в тензор
        tensor = torch.from_numpy(combined).float()

        return tensor.unsqueeze(0)  # Добавляем batch dimension


class PostProcessor:
    def __init__(self, s2_max_reflectance: float = 3000.0):
        """
        Класс для постобработки результатов модели

        Параметры:
            - s2_max_reflectance: максимальное значение отражательной способности S2
        """
        self.s2_max_reflectance = s2_max_reflectance

    def postprocess(self, tensor: torch.Tensor) -> np.ndarray:
        """
        Преобразует выход модели обратно в формат изображения

        Аргументы:
            - tensor: выход модели в формате [1, 13, H, W]

        Возвращает:
            - np.ndarray: изображение в формате [13, H, W] с нормальными значениями
        """
        # Убираем batch dimension и переводим в numpy
        img = tensor.squeeze(0).numpy()

        # Денормализация
        img = ((img + 1.0) / 2.0) * self.s2_max_reflectance

        # Клиппинг значений
        return np.clip(img, 0, self.s2_max_reflectance)

    def save_image(self, img: np.ndarray, output_path: Path, reference_path: Path | None = None) -> None:
        """
        Сохраняет обработанное изображение в GeoTIFF

        Аргументы:
            - img: изображение в формате [13, H, W]
            - output_path: путь для сохранения
            - reference_path: путь к референсному изображению для копирования метаданных
        """
        if reference_path is not None:
            with rasterio.open(reference_path) as src:
                meta = src.meta.copy()
        else:
            meta = {
                "driver": "GTiff",
                "dtype": "float32",
                "count": img.shape[0],
                "height": img.shape[1],
                "width": img.shape[2],
            }

        meta.update(
            {
                "dtype": "float32",
                "count": img.shape[0],
            }
        )

        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(img.astype(np.float32))
