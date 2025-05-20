from pathlib import Path

import torch

from .preprocessing import PostProcessor, SEN12MSDataPreprocessor


class CloudRemovalModel:
    def __init__(
        self,
        model_path: Path,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        s2_max_reflectance: float = 3000.0,
        s1_clip_min: tuple = (-25.0, -32.5),
        s1_clip_max: tuple = (0.0, 0.0),
    ):
        """
        Класс для работы с моделью удаления облаков

        Параметры:
            - model_path: путь к файлу модели
            - device: устройство для вычислений (cuda/cpu)
            - s2_max_reflectance: максимальное значение отражательной способности S2
            - s1_clip_min: минимальные значения для клиппинга S1 (VV, VH)
            - s1_clip_max: максимальные значения для клиппинга S1 (VV, VH)
        """
        self.device = device
        self.model = self._load_model(model_path)
        self.preprocessor = SEN12MSDataPreprocessor(
            s2_max_reflectance=s2_max_reflectance, s1_clip_min=s1_clip_min, s1_clip_max=s1_clip_max
        )
        self.postprocessor = PostProcessor(s2_max_reflectance=s2_max_reflectance)

    def _load_model(self, model_path: Path) -> torch.nn.Module:
        """Загружает модель из файла"""
        model = torch.load(model_path, map_location=self.device)
        model.eval()
        return model

    def process(
        self, s2_cloudy_path: Path, s1_path: Path, output_path: Path | None = None, reference_path: Path | None = None
    ) -> torch.Tensor:
        """
        Обрабатывает изображение: предобработка -> модель -> постобработка

        Аргументы:
            - s2_cloudy_path: путь к файлу Sentinel-2 Cloudy
            - s1_path: путь к файлу Sentinel-1
            - output_path: путь для сохранения результата (опционально)
            - reference_path: путь к референсному изображению для метаданных (опционально)

        Возвращает:
            - torch.Tensor: результат работы модели
        """
        # Предобработка
        input_tensor = self.preprocessor.preprocess(s2_cloudy_path, s1_path)
        input_tensor = input_tensor.to(self.device)

        # Инференс
        with torch.no_grad():
            output = self.model(input_tensor)

        # Постобработка
        processed_img = self.postprocessor.postprocess(output)

        # Сохранение результата
        if output_path is not None:
            self.postprocessor.save_image(processed_img, output_path, reference_path)

        return output
