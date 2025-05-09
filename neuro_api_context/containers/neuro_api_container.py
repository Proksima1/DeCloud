from dataclasses import dataclass

from base.containers.base import Container
from base.infrastructure.pg.client import engine_from_settings_both
from base.infrastructure.s3.session import s3_session_from_settings
from neuro_api_context.repositories.db_repository import DBRepository
from neuro_api_context.repositories.s3_repository import S3Repository
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

        neuro_api_service = NeuroApiService(
            _s3_repository=_s3_repository,
            _db_repository=db_repository,
        )

        return cls(neuro_api_service=neuro_api_service)
