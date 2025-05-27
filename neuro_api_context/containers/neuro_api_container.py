from dataclasses import dataclass

from base.containers.base import Container
from base.infrastructure.pg.client import engine_from_settings_both
from base.infrastructure.s3.session import s3_session_from_settings
from neuro_api_context.repositories.db_repository import DBRepository
from neuro_api_context.repositories.s3_repository import S3Repository
from neuro_api_context.services.image_processing_service import ImageProcessor
from neuro_api_context.services.ml_evaluator import MLModelService
from neuro_api_context.services.neuro_api_service import NeuroApiService


@dataclass(frozen=True, slots=True)
class NeuroApiContainer(Container):
    neuro_api_service: NeuroApiService

    @classmethod
    async def build_from_settings(cls) -> "NeuroApiContainer":
        _s3_session = s3_session_from_settings()

        _s3_repository = S3Repository(_s3_session=_s3_session)

        pg_rw_client, pg_ro_client = engine_from_settings_both()
        db_repository = DBRepository(_engine_ro=pg_ro_client, _engine_rw=pg_rw_client)
        image_processor = ImageProcessor()
        ml_model_service = MLModelService(_model=MLModelService.load_model())
        neuro_api_service = NeuroApiService(
            _s3_repository=_s3_repository,
            _db_repository=db_repository,
            _image_processor=image_processor,
            _ml_model_service=ml_model_service,
        )

        return cls(neuro_api_service=neuro_api_service)
