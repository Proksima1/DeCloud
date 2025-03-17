from dataclasses import dataclass

from neuro_api_context.containers.base import Container
from neuro_api_context.services.neuro_api_service import NeuroApiService


@dataclass(frozen=True, slots=True)
class NeuroApiContainer(Container):
    neuro_api_service: NeuroApiService

    @classmethod
    async def build_from_settings(cls) -> "NeuroApiContainer": ...
