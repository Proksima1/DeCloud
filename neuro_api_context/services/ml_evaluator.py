from dataclasses import dataclass

import torch

from base.settings import settings

from neuro_api_context.presentation.ml.model import GeneratorUNet


@dataclass(frozen=True, slots=True)
class MLModelService:
    _model: GeneratorUNet

    @classmethod
    def load_model(cls, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        model = GeneratorUNet(in_channels=15, out_channels=13)
        model.load_state_dict(torch.load(settings.ml_model.ml_model_path, map_location=device, weights_only=False))
        model.eval()
        return model

    def predict(self, input_tensor: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return self._model(input_tensor)
